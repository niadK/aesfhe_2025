import time
import numpy as np
from desilofhe import Engine
from he_context import HEContext, input_handler, output_print
from he_lut import LUT_setup_xor, LUT_setup_sbox, LUT_setup_gfmul
from he_aes import HEaddRoundKey, HEsubBytes, HEshiftRows, HEmixCols, HEmixColsBT, Bootstrapping
from interface import get_engine_param, get_input_pair, select_test_type
from plain_aes import addRoundKey, subBytes, shiftRows, mixColumns

inp = [0x01, 0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x78, 0x89, 0x9A, 0xAB, 0xBC, 0xCD, 0xDE, 0xEF, 0xF0]
key = [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0, 0xB0, 0xC0, 0xD0, 0xE0, 0xF0, 0x01]

thread_count = get_engine_param()
print("\n[●] Initializing  components...")
start = time.time()
print("   ├─ Setting up Engine...")
ctx = HEContext(Engine('parallel', use_bootstrap=True, thread_count=thread_count))
print("   ├─ Building XOR LUT...")
C_xor_upper, C_xor_lower = LUT_setup_xor(ctx)
print("   ├─ Building  S-Box LUT...")
C_sbox_upper, C_sbox_lower = LUT_setup_sbox(ctx)
print("   └─ Building GF multiplication LUTs (×2, ×3)...")
C2_upper, C2_lower, C3_upper, C3_lower = LUT_setup_gfmul(ctx)
end = time.time()
print(f"[✓] Setup completed in {end - start:.2f} seconds.")

turnon = True
while turnon:
    inp, key = get_input_pair()

    print("\n[●] Processing test input..")
    start = time.time()
    enc_A_upper, enc_A_lower = input_handler(inp, ctx)
    enc_B_upper, enc_B_lower = input_handler(key, ctx)
    inp_AES = np.array(inp, dtype=np.uint8).reshape((4, 4), order='F')
    key_AES = np.array(key, dtype=np.uint8).reshape((4, 4), order='F')
    end = time.time()
    print(f"[✓] Processing test input is done... Total time: {end - start:.2f} seconds.")

    test_type, subfunc = select_test_type()
    if test_type == '1':
        print("\n[One round (AddRoundKey → SubBytes → ShiftRows → MixColumns)]")
        
        print("\n[●] Plain AES running for comparison...")
        out_1 = addRoundKey(inp_AES, key_AES)
        out_2 = subBytes(out_1)
        out_3 = shiftRows(out_2)
        out_4 = mixColumns(out_3)
        print(f"[✓] Plain AES done!\n")
        
        print("[●] ADDKEY running...")
        start = time.time()
        out_upper_1, out_lower_1 = HEaddRoundKey(enc_A_upper, enc_A_lower, enc_B_upper, enc_B_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] ADDKEY done in {end - start:.2f} sec, in level: {enc_A_upper.level}, out level: {out_upper_1.level}")
        output_print(out_upper_1, out_lower_1, out_1, ctx)

        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_1, out_lower_1 = Bootstrapping(out_upper_1, out_lower_1, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_1.level}")
        
        print("\n[●] SUBBYTES running...")
        start = time.time()
        out_upper_1 = ctx.intt(out_upper_1)
        out_lower_1 = ctx.intt(out_lower_1)
        out_upper_2, out_lower_2 = HEsubBytes(out_upper_1, out_lower_1, C_sbox_upper, C_sbox_lower, ctx)
        end = time.time()
        print(f"[✓] SUBBYTES done in {end - start:.2f} sec, in level {out_upper_1.level}, out level: {out_upper_2.level}")
        output_print(out_upper_2, out_lower_2, out_2, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_2, out_lower_2 = Bootstrapping(out_upper_2, out_lower_2, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_2.level}")
        
        print("\n[●] SHIFTROWS running...")
        start = time.time()
        out_upper_3, out_lower_3 = HEshiftRows(out_upper_2, out_lower_2, ctx)
        end = time.time()
        print(f"[✓] SHIFTROWS done in {end - start:.2f} sec, in level: {out_upper_2.level}, out level: {out_upper_3.level}")
        output_print(out_upper_3, out_lower_3, out_3, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_3, out_lower_3 = Bootstrapping(out_upper_3, out_lower_3, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_3.level}")

        print("\n[●] MIXCOLUMNS running...")
        start = time.time()
        out_upper_4, out_lower_4 = HEmixColsBT(out_upper_3, out_lower_3, C2_upper, C2_lower, C3_upper, C3_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] MIXCOLUMNS done in {end - start:.4f} sec, in level: {out_upper_3.level} out level: {out_upper_4.level}")
        
        output_print(out_upper_4, out_lower_4, out_4, ctx)

    elif test_type == '2':
        print("\n[Two rounds (AddRoundKey → SubBytes → ShiftRows → MixColumns → AddRoundKey → ...)]")
        
        print("\n[●] Plain AES running for comparison...")
        out_1 = addRoundKey(inp_AES, key_AES)
        out_2 = subBytes(out_1)
        out_3 = shiftRows(out_2)
        out_4 = mixColumns(out_3)
        out_5 = addRoundKey(out_4, key_AES)
        out_6 = subBytes(out_5)
        out_7 = shiftRows(out_6)
        out_8 = mixColumns(out_7)
        out_9 = addRoundKey(out_8, key_AES)
        print(f"[✓] Plain AES done!")
        
        print("[●] ADDKEY running...")
        start = time.time()
        out_upper_1, out_lower_1 = HEaddRoundKey(enc_A_upper, enc_A_lower, enc_B_upper, enc_B_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] ADDKEY done in {end - start:.2f} sec, in level: {enc_A_upper.level}, out level: {out_upper_1.level}")
        output_print(out_upper_1, out_lower_1, out_1, ctx)

        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_1, out_lower_1 = Bootstrapping(out_upper_1, out_lower_1, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_1.level}")
        
        print("\n[●] SUBBYTES running...")
        start = time.time()
        out_upper_1 = ctx.intt(out_upper_1)
        out_lower_1 = ctx.intt(out_lower_1)
        out_upper_2, out_lower_2 = HEsubBytes(out_upper_1, out_lower_1, C_sbox_upper, C_sbox_lower, ctx)
        end = time.time()
        print(f"[✓] SUBBYTES done in {end - start:.2f} sec, in level {out_upper_1.level}, out level: {out_upper_2.level}")
        output_print(out_upper_2, out_lower_2, out_2, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_2, out_lower_2 = Bootstrapping(out_upper_2, out_lower_2, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_2.level}")
        
        print("\n[●] SHIFTROWS running...")
        start = time.time()
        out_upper_3, out_lower_3 = HEshiftRows(out_upper_2, out_lower_2, ctx)
        end = time.time()
        print(f"[✓] SHIFTROWS done in {end - start:.2f} sec, in level: {out_upper_2.level}, out level: {out_upper_3.level}")
        output_print(out_upper_3, out_lower_3, out_3, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_3, out_lower_3 = Bootstrapping(out_upper_3, out_lower_3, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_3.level}")

        print("\n[●] MIXCOLUMNS running...")
        start = time.time()
        out_upper_4, out_lower_4 = HEmixColsBT(out_upper_3, out_lower_3, C2_upper, C2_lower, C3_upper, C3_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] MIXCOLUMNS done in {end - start:.4f} sec, in level: {out_upper_3.level} out level: {out_upper_4.level}")
        output_print(out_upper_4, out_lower_4, out_4, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_4, out_lower_4 = Bootstrapping(out_upper_4, out_lower_4, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_4.level}")
        
        print("[●] ADDKEY running...")
        start = time.time()
        out_upper_5, out_lower_5 = HEaddRoundKey(out_upper_4, out_lower_4, enc_B_upper, enc_B_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] ADDKEY done in {end - start:.2f} sec, in level: {out_upper_4.level}, out level: {out_upper_5.level}")
        output_print(out_upper_5, out_lower_5, out_5, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_5, out_lower_5 = Bootstrapping(out_upper_5, out_lower_5, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_5.level}")
        
        print("\n[●] SUBBYTES running...")
        start = time.time()
        out_upper_5 = ctx.intt(out_upper_5)
        out_lower_5 = ctx.intt(out_lower_5)
        out_upper_6, out_lower_6 = HEsubBytes(out_upper_5, out_lower_5, C_sbox_upper, C_sbox_lower, ctx)
        end = time.time()
        print(f"[✓] SUBBYTES done in {end - start:.2f} sec, in level {out_upper_5.level}, out level: {out_upper_6.level}")
        output_print(out_upper_6, out_lower_6, out_6, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_6, out_lower_6 = Bootstrapping(out_upper_6, out_upper_6, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_6.level}")
        
        print("\n[●] SHIFTROWS running...")
        start = time.time()
        out_upper_7, out_lower_7 = HEshiftRows(out_upper_6, out_upper_6, ctx)
        end = time.time()
        print(f"[✓] SHIFTROWS done in {end - start:.2f} sec, in level: {out_upper_6.level}, out level: {out_upper_7.level}")
        output_print(out_upper_7, out_lower_7, out_7, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_7, out_lower_7 = Bootstrapping(out_upper_7, out_lower_7, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_7.level}")

        print("\n[●] MIXCOLUMNS running...")
        start = time.time()
        out_upper_8, out_lower_8 = HEmixColsBT(out_upper_7, out_upper_7, C2_upper, C2_lower, C3_upper, C3_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] MIXCOLUMNS done in {end - start:.4f} sec, in level: {out_upper_7.level} out level: {out_upper_8.level}")
        output_print(out_upper_8, out_lower_8, out_8, ctx)
        
        print("\n[●] Bootstrapping...")
        start = time.time()
        out_upper_8, out_lower_8 = Bootstrapping(out_upper_8, out_lower_8, ctx)
        end = time.time()
        print(f"[✓] Bootstrapping done in {end - start:.2f} sec, out level: {out_upper_8.level}")
        
        print("[●] ADDKEY running...")
        start = time.time()
        out_upper_9, out_lower_9 = HEaddRoundKey(out_upper_8, out_lower_8, enc_B_upper, enc_B_lower, C_xor_lower, ctx)
        end = time.time()
        print(f"[✓] ADDKEY done in {end - start:.2f} sec, in level: {out_upper_8.level}, out level: {out_upper_9.level}")
        output_print(out_upper_9, out_lower_9, out_9, ctx)
        
    elif test_type == '3':
        if subfunc == '1':
            print("\n[AddRoundKey]")
            print("[●] ADDKEY running...")
            start = time.time()
            out_upper_1, out_lower_1 = HEaddRoundKey(enc_A_upper, enc_A_lower, enc_B_upper, enc_B_lower, C_xor_lower, ctx)
            end = time.time()
            print(f"[✓] ADDKEY done in {end - start:.2f} sec, in level: {enc_A_upper.level}, out level: {out_upper_1.level}")
            res2 = addRoundKey(inp_AES, key_AES)
            output_print(out_upper_1, out_lower_1, res2, ctx)
            
        elif subfunc == '2':
            print("\n[SubBytes]")
            print("[●] SUBBYTES running...")
            start = time.time()
            out_upper_1 = ctx.intt(enc_A_upper)
            out_lower_1 = ctx.intt(enc_A_lower)
            out_upper_2, out_lower_2 = HEsubBytes(out_upper_1, out_lower_1, C_sbox_upper, C_sbox_lower, ctx)
            end = time.time()
            print(f"[✓] SUBBYTES done in {end - start:.2f} sec, in level {enc_A_upper.level}, out level: {out_upper_2.level}")
            output_print(out_upper_2, out_lower_2, subBytes(inp_AES), ctx)
        
        elif subfunc == '3':
            print("\n[ShiftRows]")
            print("[●] SHIFTROWS running...")
            start = time.time()
            out_upper_3, out_lower_3 = HEshiftRows(enc_A_upper, enc_A_lower, ctx)
            end = time.time()
            print(f"[✓] SHIFTROWS done in {end - start:.2f} sec, in level: {enc_A_upper.level}, out level: {out_upper_3.level}")
            output_print(out_upper_3, out_lower_3, shiftRows(inp_AES), ctx)
            
        elif subfunc == '4':
            print("\n[MixColumns]")
            print("[●] MIXCOLUMNS running...")
            start = time.time()
            out_upper_4, out_lower_4 = HEmixCols(enc_A_upper, enc_A_lower, C2_upper, C2_lower, C3_upper, C3_lower, C_xor_lower, ctx)
            end = time.time()
            print(f"[✓] MIXCOLUMNS done in {end - start:.4f} sec, in level: {enc_A_upper.level} out level: {out_upper_4.level}")
            output_print(out_upper_4, out_lower_4, mixColumns(inp_AES), ctx)
    
        else:
            print("Wrong selection")

    elif test_type == '4':
        turnon = False
    
    else:
        print("Wrong selection")
