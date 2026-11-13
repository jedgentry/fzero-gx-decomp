"""Carve functions into their own compilation units.

For each claimed function: add a `splits.txt` entry covering its `.text` range
(plus any data it references exclusively, when contiguous), create the stub
source file, and register the unit in config/<VERSION>/units.json as
`nonmatching` so the retail object keeps linking until `fzgx submit` flips it.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import oracle, tufile
from .project import ROOT, Function, Project, Symbol
from .tu import unit_dir_for

DATA_SECTIONS = {".rodata", ".data", ".sdata", ".sdata2", ".bss", ".sbss", ".sbss2"}


@dataclass
class CarveResult:
    symbol: str
    module: str
    source: str
    created: bool
    ranges: List[Tuple[str, int, int, int]] = field(default_factory=list)  # section,start,end,align
    notes: List[str] = field(default_factory=list)


def _registered(project: Project, module: str, name: str) -> bool:
    """True when units.json already registers this symbol, by any unit's `symbols` list.

    The registry, not the split, is what makes a unit compile. Matching on `source` instead
    would miss a record registered under a different path, and matching on the split would say
    yes for every function whose range is claimed -- which is the bug this replaces.
    """
    return any(name in (u.get("symbols") or ()) for u in project.load_units()
               if u.get("module") == module)


def _registered_asm(project: Project, module: str, name: str) -> bool:
    """True when units.json already registers this symbol as an assembly unit.

    Such a unit is built from the split's `.s`, so carve adds the missing range and stops --
    it must not leave a C stub beside it (see the call site for the measured consequence).
    """
    return any(u.get("asm") and name in (u.get("symbols") or ())
               for u in project.load_units() if u.get("module") == module)


def _align_for(addr: int, cap: int) -> int:
    a = 4
    while a * 2 <= cap and addr % (a * 2) == 0:
        a *= 2
    return a


def _section_default_align(project: Project, module: str, section: str) -> int:
    text = (project.module_config_dir(module) / "splits.txt").read_text()
    for line in text.splitlines():
        parts = line.split()
        if parts and parts[0] == section and "align:" in line:
            return int([p for p in parts if p.startswith("align:")][0][6:])
    return 4


def exclusive_data(project: Project, fn: Function) -> Dict[str, List[Symbol]]:
    """Data symbols referenced only by this function, grouped by section."""
    syms = project.symbols(fn.symbol.module)
    index = project.function_asm(fn.symbol.module)
    out: Dict[str, List[Symbol]] = defaultdict(list)
    for name in fn.refs:
        s = syms.get(name)
        if not s or s.kind != "object" or s.section not in DATA_SECTIONS or s.scope != "local":
            continue
        users = [f for f in index.values() if name in f.refs]
        if len(users) == 1:
            out[s.section].append(s)
    return out


def order_labels_after_functions(symbols_path: Path) -> bool:
    """mwld hangs (never returns) on an object whose first symbol is a size-0 label followed by
    a function at the same offset while the object carries dtk's CodeWarrior `.comment`
    section; dtk emits symbols in symbols.txt line order, so at every address a function
    shares with a label the function line goes first. A carve boundary can land on any label,
    so this runs after every carve. Returns True if the file changed."""
    lines = symbols_path.read_text().splitlines()
    key = {}
    for i, l in enumerate(lines):
        m = re.match(r"\S+ = (\.\w+):0x([0-9A-Fa-f]+); // type:(\w+)", l)
        if m:
            key.setdefault((m.group(1), int(m.group(2), 16)), []).append((i, m.group(3)))
    changed = False
    for entries in key.values():
        idx = [i for i, _ in entries]
        order = sorted(entries, key=lambda e: (e[1] != "function", e[0]))
        new = [lines[i] for i, _ in order]
        if new != [lines[i] for i in idx]:
            for i, l in zip(idx, new):
                lines[i] = l
            changed = True
    if changed:
        symbols_path.write_text("\n".join(lines) + "\n")
    return changed


def globalize_local_function(project: Project, module: str, name: str, res=None) -> bool:
    """A `scope:local` function carved into its own unit is defined by our object under its
    plain name, but dtk exported it from the auto object under `name_ADDR` and every other
    object (auto objects, and the asm units copied from dtk's output) references that name.
    Flip it to global in symbols.txt (the next split re-names the auto objects' references)
    and rename the references in the copied sources ourselves."""
    sp = project.module_config_dir(module) / "symbols.txt"
    text = sp.read_text()
    m = re.search(rf"^{re.escape(name)} = (\.\w+):0x([0-9A-Fa-f]+); // type:function[^\n]*?scope:local", text, re.M)
    if not m:
        return False
    line = m.group(0)
    text = text.replace(line, line.replace("scope:local", "scope:global"), 1)
    sp.write_text(text)
    project._symbols.pop(module, None)
    suffixed = f"{name}_{int(m.group(2), 16):08X}"
    n = len(project.rewrite_global_references(module, [name]))
    if res is not None:
        res.notes.append(f"scope local -> global; {n} source(s) renamed {suffixed} -> {name}")
    return True


def retain_entry_labels(project: Project, sym: Symbol) -> List[str]:
    """A C definition replaces the function, but cannot emit its additional entry labels."""
    template = project.module_config_dir(sym.module) / 'ldscript.tpl'
    if not template.exists():
        return []
    labels = [s.name for s in project.symbols(sym.module).values()
              if s.kind == 'label' and s.section == sym.section and s.addr == sym.addr
              and s.scope == 'global' and s.name.isidentifier()]
    text = template.read_text()
    additions = [name for name in labels if not re.search(r'^\s*' + re.escape(name) + r'\s*=', text, re.M)]
    if additions:
        block = '\n    /* Retail labels sharing a C function entry. */\n'
        block += ''.join(f'    {name} = {sym.name};\n' for name in additions)
        template.write_text(text.replace('\n}\n\nFORCEACTIVE', block + '}\n\nFORCEACTIVE'))
    return additions


def carve(project: Project, symbol: str, dry_run: bool = False, entry_aliases: bool = True) -> CarveResult:
    sym = project.resolve(symbol)
    if sym is None or sym.kind != "function":
        raise LookupError(f"{symbol}: not a known (or unambiguous) function symbol; use module:name for _prolog/_epilog")
    module = sym.module
    existing = project.unit_of(sym)
    source = f"{unit_dir_for(project, sym)}/{sym.name}.c"
    if existing:
        # A split range and a units.json entry are different things (findings 279/280), and
        # `unit_of` reads the *split*, so `existing` is truthy whenever the range is claimed --
        # including for a function that has a source file but was never registered, which then
        # compiles nothing and leaves the retail auto object supplying the bytes. Returning
        # here made those bodies permanently unregisterable: every later carve also saw
        # `existing` and bailed, so nothing could ever add the missing record.
        #
        # Measured on fn_1_128B60, fn_8_704, fn_3_17098, fn_1_17A9C, fn_1_3F4B8, fn_1_611EC and
        # fn_1_FC760: all seven check at 100.0 against retail and all seven were missing only
        # the units.json entry.
        if _registered(project, module, sym.name):
            return CarveResult(sym.name, module, existing if existing.endswith(".c") else existing,
                               created=False, notes=[f"already in unit {existing}"])
        notes = [f"split exists at {existing} but no units.json entry; registering"]
        if not (ROOT / "src" / existing).exists():
            notes.append(f"no source at src/{existing}; carved stub")
    else:
        notes = []
    fn = project.function_asm(module).get(sym.name)
    if fn is None:
        raise LookupError(f"{symbol}: no disassembly found under build/ (run ninja first)")

    res = CarveResult(sym.name, module, existing or source, created=True, notes=notes)
    # The function's own .text range goes in `res.ranges` only when no split already claims it.
    # `unit_of` is split-based, so reaching here with `existing` set means the range IS covered,
    # and re-adding it appended a second entry for the same bytes. dtk then refuses the module:
    #   Split 0:0x00000704..0x00000754 overlaps with previous split      (fn_8_704, title)
    # That is not a cosmetic duplicate -- it breaks the whole build, and it happened on the
    # first attempt at this fix. .init functions in the DOL are not .text, hence sym.section.
    if not existing:
        res.ranges.append((sym.section, sym.addr, sym.end, 4))
    else:
        res.notes.append(f"split range already present; not re-adding {sym.section}")
    for section, objs in exclusive_data(project, fn).items():
        objs.sort(key=lambda s: s.addr)
        contiguous = all(objs[i].end <= objs[i + 1].addr <= objs[i].end + 32 for i in range(len(objs) - 1))
        if not contiguous:
            res.notes.append(f"{section}: exclusive data not contiguous ({', '.join(o.name for o in objs)}); left in auto unit")
            continue
        start, end = objs[0].addr, objs[-1].end
        if any(sp.section == section and sp.start < end and start < sp.end for sp in project.splits(module)):
            res.notes.append(f"{section}: 0x{start:X}-0x{end:X} overlaps an existing split; left in auto unit")
            continue
        cap = _section_default_align(project, module, section)
        res.ranges.append((section, start, end, _align_for(start, cap)))
    if dry_run:
        return res

    # a switch jump table the function references stays in the data unit that owns its range:
    # our object references it by name, so the retail symbol must be global (dtk emits locals
    # without `.global`, unreachable from another object)
    sp_ = project.module_config_dir(module) / "symbols.txt"
    text_ = sp_.read_text(); changed_ = False
    for ref in fn.refs:
        if not ref.startswith("jumptable_"):
            continue
        new_text_, k = re.subn(rf"^({re.escape(ref)} = [^\n]*?)scope:local", r"\1scope:global", text_, count=1, flags=re.M)
        if k:
            text_ = new_text_; changed_ = True; res.notes.append(f"{ref}: scope local -> global (referenced from this unit)")
    if changed_:
        sp_.write_text(text_)
        project._symbols.pop(module, None)
    # the table's own range stays with the data unit that has it
    res.ranges = [r_ for r_ in res.ranges if not (r_[0] == ".data" and any(ref.startswith("jumptable_") and project.symbols(module)[ref].addr == r_[1] for ref in fn.refs if ref in project.symbols(module)))]

    splits_path = project.module_config_dir(module) / "splits.txt"
    # Only write a split block when there is a range to write. A registration-only carve (a
    # function whose range is already covered, which is the whole point of the `existing`
    # branch above) has nothing to add, and emitting a bare `unit:` header with no sections
    # leaves a dead entry that later reads as a claim on nothing.
    if res.ranges:
        with splits_path.open("a") as f:
            f.write(f"\n{source}:\n")
            for section, start, end, align in res.ranges:
                f.write(f"\t{section:<11} start:0x{start:08X} end:0x{end:08X} align:{align}\n")
    # The split must actually cover the function's .text range. A body for an uncovered
    # range still checks at 100% (the per-object oracle never builds the module) but cannot
    # link: the unit adds a second copy of the function, so the module grows past retail or
    # the REL step cannot resolve. Observed on fn_8_704, whose range went missing between
    # carve and verify. Re-assert the range here so the guarantee holds whatever touched the
    # file in between. See docs/findings/279 and tools/fzgx/splitgaps.py.
    project.__dict__.get("_splits_cache", {}).pop(module, None)
    if not any(sp.section == sym.section and sp.start <= sym.addr and sym.end <= sp.end
               for sp in project.splits(module)):
        align = _align_for(sym.addr, _section_default_align(project, module, sym.section))
        with splits_path.open("a") as f:
            f.write(f"{source}:\n\t{sym.section:<11} start:0x{sym.addr:08X} "
                    f"end:0x{sym.end:08X} align:{align}\n")
        res.notes.append(f"{sym.section}: 0x{sym.addr:X}-0x{sym.end:X} was uncovered after carve; "
                         "range re-asserted")
    if module == "main" and not project.callers(sym.name, limit=1):
        # inside its auto object a callerless function survives the link with its neighbours;
        # alone in its own object mwld drops it and the DOL comes out short. dtk lists a
        # `force_active` symbol in the link script's FORCEACTIVE block, as retail's link kept it.
        sp = project.module_config_dir(module) / "symbols.txt"
        text = sp.read_text()
        new_text, k = re.subn(rf"^({re.escape(sym.name)} = [^\n]*?)(\s*)$", lambda m: m.group(1) + (" force_active" if "force_active" not in m.group(1) else ""), text, count=1, flags=re.M)
        if k and new_text != text:
            sp.write_text(new_text)
            project._symbols.pop(module, None)
            res.notes.append("force_active: no callers")

    globalize_local_function(project, module, sym.name, res)
    for label in (retain_entry_labels(project, sym) if entry_aliases else []):
        res.notes.append(f'{label}: linker alias of the C function entry')
    if order_labels_after_functions(project.module_config_dir(module) / "symbols.txt"):
        project._symbols.pop(module, None)
        res.notes.append("symbols.txt: function lines moved before same-address labels (mwld hang)")

    tu_src = tufile.tu_source_for(project, sym)
    with oracle.build_lock("units.lock"):  # submits flip statuses concurrently
        units = project.load_units()
        # Match on the symbol, not on `source`: when a split already claims the range the
        # unit path comes from that split and may differ from the `unit_dir_for` default, so
        # a source-equality test would append a second record for one function.
        if not _registered(project, module, sym.name):
            rec = {"module": module, "source": source, "symbols": [sym.name],
                   "status": "nonmatching", "mw_version": None, "extra_cflags": []}
            if tu_src:
                rec["tu"] = tu_src  # block unit: the C lives in the TU file, the object is generated
            units.append(rec)
            project.save_units(units)
            res.notes.append(f"registered in units.json as {source}")
    if tu_src:
        # no file in the tree: a stub is generated until the function's block is spliced in
        tufile.write_gen(project, {"module": module, "source": source, "symbols": [sym.name], "tu": tu_src})
    else:
        src_path = ROOT / "src" / source
        # An asm unit is compiled from `src/<source>.s`, which the split generates, not from C.
        # Writing a C stub for one leaves an empty function body beside the assembly; the body
        # carries no relocation for the symbols the real code references, and the REL step then
        # fails with "Failed to find symbol <fn> in any module", taking all fifteen .rel targets
        # with it. `asmunit.make` deletes this stub for exactly that reason and `asmunit.resume`
        # expects the range but no source, so carve must not create one either.
        #
        # Measured 2026-10-05 on fn_12_D0B8: the stub C was built and linked, and
        # movie_module.plf then failed to resolve fn_12_5674. Reverted (docs/findings/290).
        if not src_path.exists() and not _registered_asm(project, module, sym.name):
            src_path.parent.mkdir(parents=True, exist_ok=True)
            src_path.write_text(
                f'#include "types.h"\n\n'
                f"// {sym.name}: {module} {sym.section}:0x{sym.addr:08X} size 0x{sym.size:X}\n"
                f"// Carved by fzgx. Replace this file's body with the matching C.\n"
            )
    return res
