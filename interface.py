def get_engine_param():
    print("\n=== AES Homomorphic Encryption Test ===")
    print("This program runs AES operations over CKKS.\n")
    print("--CKKS Engine Parameter Setup--")
    print("  • Fixed parameters: mode = 'parallel', use_bootstrap = True")
    print("  • Can modify: thread_count \n")
    default_thread_count = 256
    user_input = input(f">> Enter the number of threads to use [default: {default_thread_count}]: ")
    thread_count = int(user_input) if user_input.strip() else default_thread_count
    return thread_count

def get_input_pair():
    print("\n--Test Input Setup--")
    print("Select test input for AES encryption:")
    print("  1. Predefined test input (Pattern A)")
    print("  2. Predefined test input (Pattern B)")
    print("  3. Manually enter 16-byte plaintext and key")
    print("  4. Exit\n")
    
    choice = input(">> Enter your choice (1/2/3/4): ").strip() or '1'

    if choice == '1':
        inp = [0x01, 0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x78, 0x89, 0x9A, 0xAB, 0xBC, 0xCD, 0xDE, 0xEF, 0xF0]
        key = [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0, 0xB0, 0xC0, 0xD0, 0xE0, 0xF0, 0x01]
    elif choice == '2':
        inp = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10]
        key = [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0xA0, 0xB0, 0xC0, 0xD0, 0xE0, 0xF0, 0x01]
    elif choice == '3':
        print("\n[Manual Input] Please enter 16 integers between 0 and 255 for the plaintext.")
        inp = []
        for i in range(16):
            val = int(input(f"  Byte {i+1}/16: "))
            while not (0 <= val <= 255):
                print("    [!] Invalid value. Enter an integer between 0 and 255.")
                val = int(input(f"  Byte {i+1}/16: "))
            inp.append(val)

        print("\nNow enter 16 integers between 0 and 255 for the key.")
        key = []
        for i in range(16):
            val = int(input(f"  Byte {i+1}/16: "))
            while not (0 <= val <= 255):
                print("    [!] Invalid value. Enter an integer between 0 and 255.")
                val = int(input(f"  Byte {i+1}/16: "))
            key.append(val)
    elif choice == '4':
        exit()
    else:
        print("[X] Invalid option selected. Using default Pattern A.")
        return get_input_pair()

    print("\n[✓] Input selection complete.\n")
    print("Plaintext:")
    print("  " + " ".join(f"0x{b:02X}" for b in inp))
    print("Key:")
    print("  " + " ".join(f"0x{b:02X}" for b in key))

    return inp, key

def select_test_type():
    print("\n--AES Test Setup--")
    print("Select AES test type:")
    print("  1. One round (AddRoundKey → SubBytes → ShiftRows → MixColumns)")
    print("  2. Two rounds (repeat step 1 twice)")
    print("  3. Single sub-function test")

    choice = input(">> Enter your choice (1/2/3): ").strip()

    if choice == '3':
        print("\nChoose the sub-function to test:")
        print("  1. AddRoundKey")
        print("  2. SubBytes")
        print("  3. ShiftRows")
        print("  4. MixColumns\n")

        sub_choice = input(">> Enter your choice (1/2/3/4): ").strip()
        return choice, sub_choice
    else:
        return choice, None