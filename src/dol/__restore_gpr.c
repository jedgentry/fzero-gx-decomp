/*
 * __restore_gpr: out-of-line GPR restore of the PowerPC EABI runtime
 * (CodeWarrior Runtime.PPCEABI.H, runtime.c).
 *
 * Nothing calls __restore_gpr by name. A compiler-generated epilogue points r11 at the
 * top of its GPR save area and calls _restgpr_N, which reloads rN..r31 (register k at
 * -4 * (32 - k)(r11)) and returns. Those registers belong to the caller and r11 is
 * not an argument register, so the routine cannot be written in C: it is a
 * function-level assembly routine (`asm`, no frame) with one `entry` label per
 * first register.
 */
void _restgpr_14(void); void _restgpr_15(void); void _restgpr_16(void); void _restgpr_17(void); void _restgpr_18(void); void _restgpr_19(void);
void _restgpr_20(void); void _restgpr_21(void); void _restgpr_22(void); void _restgpr_23(void); void _restgpr_24(void); void _restgpr_25(void);
void _restgpr_26(void); void _restgpr_27(void); void _restgpr_28(void); void _restgpr_29(void); void _restgpr_30(void); void _restgpr_31(void);

asm void __restore_gpr(void) {
    nofralloc
    entry _restgpr_14
    lwz r14, -72(r11)
    entry _restgpr_15
    lwz r15, -68(r11)
    entry _restgpr_16
    lwz r16, -64(r11)
    entry _restgpr_17
    lwz r17, -60(r11)
    entry _restgpr_18
    lwz r18, -56(r11)
    entry _restgpr_19
    lwz r19, -52(r11)
    entry _restgpr_20
    lwz r20, -48(r11)
    entry _restgpr_21
    lwz r21, -44(r11)
    entry _restgpr_22
    lwz r22, -40(r11)
    entry _restgpr_23
    lwz r23, -36(r11)
    entry _restgpr_24
    lwz r24, -32(r11)
    entry _restgpr_25
    lwz r25, -28(r11)
    entry _restgpr_26
    lwz r26, -24(r11)
    entry _restgpr_27
    lwz r27, -20(r11)
    entry _restgpr_28
    lwz r28, -16(r11)
    entry _restgpr_29
    lwz r29, -12(r11)
    entry _restgpr_30
    lwz r30, -8(r11)
    entry _restgpr_31
    lwz r31, -4(r11)
    blr
}
