.include "macros.inc"
.file "lbl_8006D21C.c"

# Assembly by evidence (docs/ASM_POLICY.md section 1).
# tan(angle) of an s16 angle from the half-wave table lbl_80142840 (rebased with
# addis +1 and a negated index).
# - Hand-allocated table lookup: the quadrant fold keeps angle, index and table in r3-r6 (sine returns
#   early with beqlr, tangent rebases its table with addis +1 and a negated index); MWCC allocates and
#   lowers these differently (measured, decomp/fn-8006d044-mathutil_r2 6e78ea6f). No frame.
# - Source: the engine math library (Amusement Vision's mathutil, shared with Super Monkey Ball,
#   where these routines are nofralloc asm functions).

# 0x8006D21C..0x8006D24C | size: 0x30
.text
.balign 4

# .text:0x0 | 0x8006D21C | size: 0x30
.fn lbl_8006D21C, global
/* 8006D21C 0006A21C  3C 80 80 14 */	lis r4, lbl_80142840@h
/* 8006D220 0006A220  70 66 40 00 */	andi. r6, r3, 0x4000
/* 8006D224 0006A224  54 65 14 3A */	clrlslwi r5, r3, 18, 2
/* 8006D228 0006A228  60 84 28 40 */	ori r4, r4, lbl_80142840@l
/* 8006D22C 0006A22C  41 82 00 18 */	beq .L_8006D244
/* 8006D230 0006A230  3C 84 00 01 */	addis r4, r4, 0x1
/* 8006D234 0006A234  7C A5 00 D0 */	neg r5, r5
/* 8006D238 0006A238  7C 25 24 2E */	lfsx f1, r5, r4
/* 8006D23C 0006A23C  FC 20 09 10 */	fnabs f1, f1
/* 8006D240 0006A240  4E 80 00 20 */	blr
.L_8006D244:
/* 8006D244 0006A244  7C 25 24 2E */	lfsx f1, r5, r4
/* 8006D248 0006A248  4E 80 00 20 */	blr
.endfn lbl_8006D21C
