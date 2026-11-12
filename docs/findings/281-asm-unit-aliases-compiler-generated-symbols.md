# 281 — the SDK save/restore register family cannot be asm units: it aliases compiler-generated symbols

> **Correction (2026-11-12).** The conclusion below is wrong. mwld does not synthesise
> `_savefpr_N`/`_savegpr_N`: a C function whose prologue calls `_savegpr_22` fails to link with
> "undefined: '_savegpr_22'" until these objects are supplied. The "linker generated symbol"
> warning was our own `carve.retain_entry_labels` alias written to `ldscript.tpl` for labels the
> unit itself defines. With carve leaving those labels to the unit, all four link byte-exact as
> CodeWarrior `asm` functions with `entry` labels (src/dol/__save_fpr.c etc.), and also as asm
> units. The analysis of the population and of the C forms below still holds.

Date: 2026-10-04. Tool: `fzgx asm-unit`, `mwldeppc.exe`. Goal context: (b), all 16 targets linked.

## The population

Eight of the 631 never-attempted functions are the SDK's GPR/FPR save/restore family, and they
look like the cheapest possible wins -- 76 bytes each, perfectly regular, no calls:

    __save_fpr      0x800797C0   19x stfd f14..f31, -0x90(r11) step 8, then blr
    __restore_fpr   0x8007980C   19x lfd  f14..f31, same displacements
    __save_gpr      0x80079858   18x stw  r14..r31, -0x48(r11) step 4, then blr
    __restore_gpr   0x800798A4   18x lwz  r14..r31, same displacements

The four `*_runtime` names in the ledger are not symbols at all -- `p.resolve` returns None --
so the real family is four functions, not eight.

**No C can express these.** The context bundle says `hints: leaf, no stack frame`, and the
body addresses everything off `r11`, a register MWCC never materialises in C. `__save_gpr`
already carries 2 prior fleet attempts at best 0.0%, which is what a structurally
inexpressible function looks like rather than a hard one. So `fzgx asm-unit` is the right
tool: it links the function from its own assembly, byte-exact by construction, and records it
as `asm` -- done, but not decompiled.

## Why it does not work

The carve succeeds and the hash check fails, so the tool rolls itself back:

    ### mwldeppc.exe Linker Warning:
    #   Symbol '_restfpr_14' defined in '__restore_fpr.o' is also defined as a
    #   linker generated symbol.
    #   The linker generated symbol will be used.
    ninja: build stopped: subcommand failed.

`__save_fpr` is not an independent function. `symbols.txt` has it and `_savefpr_14` at the
**same address**, and every `_savefpr_15..31` label too:

    __save_fpr    = .text:0x800797C0; // type:function size:0x4C scope:global
    _savefpr_14   = .text:0x800797C0; // type:label scope:global
    _savefpr_15   = .text:0x800797C4; // type:label scope:global

Those `_savefpr_*` / `_restfpr_*` names are **compiler-generated**: mwld synthesises them for
any prologue that saves f14-f31, and they are also the exact symbols the runtime's own
C code references. Handing mwld an object that defines them collides with the ones it is about
to generate. Carve also added `force_active` to `__save_fpr`/`__restore_fpr` (its no-callers
path), which makes the collision load-bearing rather than incidental.

## The rule this establishes

An asm unit is only safe when the function's retail name is **not** an alias of a
compiler-generated symbol. `carve.retain_entry_labels` handles the ordinary linker-alias case
(`fn_8006E4D8` style, where our C must keep retail's label reachable), but that is the
opposite requirement: here retail's labels *must not* be defined by us at all, because mwld
owns them.

So the eligibility test `if sym is None or p.unit_of(sym): continue` in
`asmunit.make` is not sufficient. It needs to also refuse any function whose address carries a
`_save*pr_*` / `_rest*pr_*` (and the GPR equivalents) label, and say why, rather than
producing a link failure that costs a full configure-split-build cycle to discover.

**Not attempted beyond this:** rewriting the family as C against a declared frame. There is
no C spelling for `r11` as a base register, so that path does not exist without inline
assembly, which this project bans.

## Cost of the dead end

One `asm-unit` invocation: configure 11 s, split 26 s, then a link failure and a full
rollback. No damage -- `git status` clean afterwards and `16 files OK` re-verified. The
rollback path is what makes this cheap to record.

## What is still available in this population

Nothing from these four. The remaining 437 virgin schedulable functions (541 KB) are ordinary
C and unmeasured; this family is 304 bytes of it and is now known to be a dead end rather
than an unknown.