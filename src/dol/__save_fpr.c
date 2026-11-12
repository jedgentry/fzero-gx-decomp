/*
 * __save_fpr: out-of-line FPR save of the PowerPC EABI runtime
 * (CodeWarrior Runtime.PPCEABI.H, runtime.c).
 *
 * Nothing calls __save_fpr by name. A compiler-generated prologue points r11 at the
 * top of its FPR save area and calls _savefpr_N, which stores fN..f31 (register k at
 * -8 * (32 - k)(r11)) and returns. Those registers belong to the caller and r11 is
 * not an argument register, so the routine cannot be written in C: it is a
 * function-level assembly routine (`asm`, no frame) with one `entry` label per
 * first register.
 */
void _savefpr_14(void); void _savefpr_15(void); void _savefpr_16(void); void _savefpr_17(void); void _savefpr_18(void); void _savefpr_19(void);
void _savefpr_20(void); void _savefpr_21(void); void _savefpr_22(void); void _savefpr_23(void); void _savefpr_24(void); void _savefpr_25(void);
void _savefpr_26(void); void _savefpr_27(void); void _savefpr_28(void); void _savefpr_29(void); void _savefpr_30(void); void _savefpr_31(void);

asm void __save_fpr(void) {
    nofralloc
    entry _savefpr_14
    stfd f14, -144(r11)
    entry _savefpr_15
    stfd f15, -136(r11)
    entry _savefpr_16
    stfd f16, -128(r11)
    entry _savefpr_17
    stfd f17, -120(r11)
    entry _savefpr_18
    stfd f18, -112(r11)
    entry _savefpr_19
    stfd f19, -104(r11)
    entry _savefpr_20
    stfd f20, -96(r11)
    entry _savefpr_21
    stfd f21, -88(r11)
    entry _savefpr_22
    stfd f22, -80(r11)
    entry _savefpr_23
    stfd f23, -72(r11)
    entry _savefpr_24
    stfd f24, -64(r11)
    entry _savefpr_25
    stfd f25, -56(r11)
    entry _savefpr_26
    stfd f26, -48(r11)
    entry _savefpr_27
    stfd f27, -40(r11)
    entry _savefpr_28
    stfd f28, -32(r11)
    entry _savefpr_29
    stfd f29, -24(r11)
    entry _savefpr_30
    stfd f30, -16(r11)
    entry _savefpr_31
    stfd f31, -8(r11)
    blr
}
