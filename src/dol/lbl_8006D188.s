.include "macros.inc"
.file "lbl_8006D188.c"

# Assembly by evidence (docs/ASM_POLICY.md section 1).
# sin(angle) of an s16 angle from the quarter-wave table lbl_80132820.
# - Hand-allocated table lookup: the quadrant fold keeps angle, index and table in r3-r6 (sine returns
#   early with beqlr, tangent rebases its table with addis +1 and a negated index); MWCC allocates and
#   lowers these differently (measured, decomp/fn-8006d044-mathutil_r2 6e78ea6f). No frame.
# - Source: the engine math library (Amusement Vision's mathutil, shared with Super Monkey Ball,
#   where these routines are nofralloc asm functions).

# 0x8006D188..0x8006D1B8 | size: 0x30
.text
.balign 4

# .text:0x0 | 0x8006D188 | size: 0x30
.fn lbl_8006D188, global
/* 8006D188 0006A188  70 65 40 00 */	andi. r5, r3, 0x4000
/* 8006D18C 0006A18C  54 64 04 BE */	clrlwi r4, r3, 18
/* 8006D190 0006A190  41 82 00 08 */	beq .L_8006D198
/* 8006D194 0006A194  20 84 40 00 */	subfic r4, r4, 0x4000
.L_8006D198:
/* 8006D198 0006A198  3C C0 80 13 */	lis r6, lbl_80132820@h
/* 8006D19C 0006A19C  54 84 10 3A */	slwi r4, r4, 2
/* 8006D1A0 0006A1A0  60 C6 28 20 */	ori r6, r6, lbl_80132820@l
/* 8006D1A4 0006A1A4  70 65 80 00 */	andi. r5, r3, 0x8000
/* 8006D1A8 0006A1A8  7C 26 24 2E */	lfsx f1, r6, r4
/* 8006D1AC 0006A1AC  4D 82 00 20 */	beqlr
/* 8006D1B0 0006A1B0  FC 20 08 50 */	fneg f1, f1
/* 8006D1B4 0006A1B4  4E 80 00 20 */	blr
.endfn lbl_8006D188
