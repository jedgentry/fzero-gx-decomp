.include "macros.inc"
.file "lbl_8006E2C0.c"

# Assembly by evidence (docs/ASM_POLICY.md section 1). CodeWarrior asm function with entry labels.
# *dst = transpose of mtxA's 3x3 times (x, y, z), the inverse rotation for a rigid mtxA; entries
# lbl_8006E2D0 (entered by fn_8006E2B0) and fn_8006E2D8 (entered by fn_8006E250 and fn_8006E294)
# (SMB: mathutil_mtxA_rigid_inv_tf_vec_xyz and the shared tail). The tail takes its sign from
# cr0[eq] set by the entry (crclr). This unit absorbs the former asm unit fn_8006E2D8 and the 0x18
# bytes at 0x8006E2C0 that no unit owned.
# - Falls through into two entries reached directly by other routines and takes a cr0 argument no
#   C calling convention expresses.
#   Measured 2026-11-12 (x1 probes): MWCC deletes inline-asm code unreachable from the function's own
#   entry (GC/1.2.5n, 1.3.2, 2.6; opt_dead_code, peephole, optimization_level 0), `entry`/`nofralloc`
#   are rejected outside an asm function, and a C function cannot emit a global symbol at an interior
#   offset (an ldscript alias makes `dtk rel make` panic, rel.rs:240).
# - Source: the engine math library (Amusement Vision's mathutil, shared with Super Monkey Ball,
#   where these routines are nofralloc asm functions).

# 0x8006E2C0..0x8006E324 | size: 0x64
.text
.balign 4

# .text:0x0 | 0x8006E2C0 | size: 0x64
.fn lbl_8006E2C0, global
/* 8006E2C0 0006B2C0  10 21 0C 20 */	ps_merge00 f1, f1, f1
/* 8006E2C4 0006B2C4  10 42 14 20 */	ps_merge00 f2, f2, f2
/* 8006E2C8 0006B2C8  10 63 1C 20 */	ps_merge00 f3, f3, f3
/* 8006E2CC 0006B2CC  7C 64 1B 78 */	mr r4, r3
# .text:0x10 | 0x8006E2D0 | size: 0x0
.sym lbl_8006E2D0, global
/* 8006E2D0 0006B2D0  3C A0 E0 00 */	lis r5, 0xe000
/* 8006E2D4 0006B2D4  4C 42 11 82 */	crclr eq
# .text:0x18 | 0x8006E2D8 | size: 0x0
.sym fn_8006E2D8, global
/* 8006E2D8 0006B2D8  E0 85 00 00 */	psq_l f4, 0x0(r5), 0, qr0
/* 8006E2DC 0006B2DC  C0 A5 00 08 */	lfs f5, 0x8(r5)
/* 8006E2E0 0006B2E0  10 84 00 72 */	ps_mul f4, f4, f1
/* 8006E2E4 0006B2E4  E0 C5 00 10 */	psq_l f6, 0x10(r5), 0, qr0
/* 8006E2E8 0006B2E8  EC A5 00 72 */	fmuls f5, f5, f1
/* 8006E2EC 0006B2EC  C0 E5 00 18 */	lfs f7, 0x18(r5)
/* 8006E2F0 0006B2F0  10 86 20 BA */	ps_madd f4, f6, f2, f4
/* 8006E2F4 0006B2F4  E1 05 00 20 */	psq_l f8, 0x20(r5), 0, qr0
/* 8006E2F8 0006B2F8  EC A7 28 BA */	fmadds f5, f7, f2, f5
/* 8006E2FC 0006B2FC  C1 25 00 28 */	lfs f9, 0x28(r5)
/* 8006E300 0006B300  41 82 00 10 */	beq .L_8006E310
/* 8006E304 0006B304  10 88 20 FA */	ps_madd f4, f8, f3, f4
/* 8006E308 0006B308  EC A9 28 FA */	fmadds f5, f9, f3, f5
/* 8006E30C 0006B30C  48 00 00 0C */	b .L_8006E318
.L_8006E310:
/* 8006E310 0006B310  10 88 20 FE */	ps_nmadd f4, f8, f3, f4
/* 8006E314 0006B314  EC A9 28 FE */	fnmadds f5, f9, f3, f5
.L_8006E318:
/* 8006E318 0006B318  F0 84 00 00 */	psq_st f4, 0x0(r4), 0, qr0
/* 8006E31C 0006B31C  D0 A4 00 08 */	stfs f5, 0x8(r4)
/* 8006E320 0006B320  4E 80 00 20 */	blr
.endfn lbl_8006E2C0
