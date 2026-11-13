.include "macros.inc"
.file "lbl_8006DC20.c"

# Assembly by evidence (docs/ASM_POLICY.md section 1).
# Drops the top entry of the locked-cache matrix stack (pointer at 0xE0000094).
# - Register usage no allocation produces: C compiles the drop to `lwz r3; addi r0, r3, 0x30` (the
#   allocator gives the sum r0) where retail keeps the pointer in r4 (measured). No frame.
# - Source: the engine math library (Amusement Vision's mathutil, shared with Super Monkey Ball,
#   where these routines are nofralloc asm functions).

# 0x8006DC20..0x8006DC34 | size: 0x14
.text
.balign 4

# .text:0x0 | 0x8006DC20 | size: 0x14
.fn lbl_8006DC20, global
/* 8006DC20 0006AC20  3C 60 E0 00 */	lis r3, 0xe000
/* 8006DC24 0006AC24  80 83 00 94 */	lwz r4, 0x94(r3)
/* 8006DC28 0006AC28  38 84 00 30 */	addi r4, r4, 0x30
/* 8006DC2C 0006AC2C  90 83 00 94 */	stw r4, 0x94(r3)
/* 8006DC30 0006AC30  4E 80 00 20 */	blr
.endfn lbl_8006DC20
