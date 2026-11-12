/*
 * __restore_fpr: out-of-line FPR restore of the PowerPC EABI runtime
 * (CodeWarrior Runtime.PPCEABI.H, runtime.c).
 *
 * Nothing calls __restore_fpr by name. A compiler-generated epilogue points r11 at the
 * top of its FPR save area and calls _restfpr_N, which reloads fN..f31 (register k at
 * -8 * (32 - k)(r11)) and returns. Those registers belong to the caller and r11 is
 * not an argument register, so the routine cannot be written in C: it is a
 * function-level assembly routine (`asm`, no frame) with one `entry` label per
 * first register.
 */
void _restfpr_14(void); void _restfpr_15(void); void _restfpr_16(void); void _restfpr_17(void); void _restfpr_18(void); void _restfpr_19(void);
void _restfpr_20(void); void _restfpr_21(void); void _restfpr_22(void); void _restfpr_23(void); void _restfpr_24(void); void _restfpr_25(void);
void _restfpr_26(void); void _restfpr_27(void); void _restfpr_28(void); void _restfpr_29(void); void _restfpr_30(void); void _restfpr_31(void);

asm void __restore_fpr(void) {
    nofralloc
    entry _restfpr_14
    lfd f14, -144(r11)
    entry _restfpr_15
    lfd f15, -136(r11)
    entry _restfpr_16
    lfd f16, -128(r11)
    entry _restfpr_17
    lfd f17, -120(r11)
    entry _restfpr_18
    lfd f18, -112(r11)
    entry _restfpr_19
    lfd f19, -104(r11)
    entry _restfpr_20
    lfd f20, -96(r11)
    entry _restfpr_21
    lfd f21, -88(r11)
    entry _restfpr_22
    lfd f22, -80(r11)
    entry _restfpr_23
    lfd f23, -72(r11)
    entry _restfpr_24
    lfd f24, -64(r11)
    entry _restfpr_25
    lfd f25, -56(r11)
    entry _restfpr_26
    lfd f26, -48(r11)
    entry _restfpr_27
    lfd f27, -40(r11)
    entry _restfpr_28
    lfd f28, -32(r11)
    entry _restfpr_29
    lfd f29, -24(r11)
    entry _restfpr_30
    lfd f30, -16(r11)
    entry _restfpr_31
    lfd f31, -8(r11)
    blr
}
