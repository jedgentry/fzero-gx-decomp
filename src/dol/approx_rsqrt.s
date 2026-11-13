.include "macros.inc"
.file "approx_rsqrt.c"

# Assembly by evidence (docs/ASM_POLICY.md section 1).
# f1 = 1/sqrt(f1) by frsqrte and two Newton steps; f2 = 0.5f.
# - Frameless leaf (frsqrte and two Newton steps) called by `bl` from the frameless square-root and
#   vector-length routines, which keep r3-r6 and their saved link register in volatile registers
#   across the call: a contract outside the EABI calling convention.
# - Source: the engine math library (Amusement Vision's mathutil, shared with Super Monkey Ball,
#   where these routines are nofralloc asm functions).

# 0x8006D088..0x8006D0B4 | size: 0x2C
.text
.balign 4

# .text:0x0 | 0x8006D088 | size: 0x2C
.fn approx_rsqrt, global
/* 8006D088 0006A088  EC 82 00 72 */	fmuls f4, f2, f1
/* 8006D08C 0006A08C  EC 62 10 2A */	fadds f3, f2, f2
/* 8006D090 0006A090  FC 20 08 34 */	frsqrte f1, f1
/* 8006D094 0006A094  EC 63 10 2A */	fadds f3, f3, f2
/* 8006D098 0006A098  EC A1 00 72 */	fmuls f5, f1, f1
/* 8006D09C 0006A09C  EC A5 19 3C */	fnmsubs f5, f5, f4, f3
/* 8006D0A0 0006A0A0  EC 21 01 72 */	fmuls f1, f1, f5
/* 8006D0A4 0006A0A4  EC A1 00 72 */	fmuls f5, f1, f1
/* 8006D0A8 0006A0A8  EC A5 19 3C */	fnmsubs f5, f5, f4, f3
/* 8006D0AC 0006A0AC  EC 21 01 72 */	fmuls f1, f1, f5
/* 8006D0B0 0006A0B0  4E 80 00 20 */	blr
.endfn approx_rsqrt
