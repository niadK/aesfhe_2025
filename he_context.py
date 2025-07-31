import numpy as np

BLOCK_SIZE = 16

class HEContext:
    def __init__(self, engine):
        self.engine = engine
        print("   │   ├─ Generating keys...")
        self.sk = engine.create_secret_key()
        self.pk = engine.create_public_key(self.sk)
        self.rlk = engine.create_relinearization_key(self.sk)
        self.rotk = engine.create_rotation_key(self.sk)
        self.cjk = engine.create_conjugation_key(self.sk)
        self.btk = engine.create_bootstrap_key(self.sk, stage_count=3)
        self.slot_count = engine.slot_count
        self.gap = self.slot_count // BLOCK_SIZE
        print("   │   └─ Total num_slots =", self.slot_count)
        
    def add(self, ct1, ct2):
        return self.engine.add(ct1, ct2)
    
    def rotate(self, ct1, delta):
        return self.engine.rotate(ct1, self.rotk, delta=delta)
    
    def multiply(self, ct1, ct2, relinearization=False):
        if relinearization: 
            return self.engine.multiply(ct1, ct2, self.rlk)
        return self.engine.multiply(ct1, ct2)
    
    def intt(self, ct):
        return self.engine.intt(ct)
    
    def bootstrap(self, ct):
        return self.engine.bootstrap(ct, self.rlk, self.cjk, self.btk)  
    
    def rescale(self, ct):
        return self.engine.rescale(ct)
    
    def make_power_basis(self, val, max_power):
        return self.engine.make_power_basis(val, max_power=max_power, relinearization_key=self.rlk)
    
    def encode(self, val, level=None):
        if level is not None:
            return self.engine.encode(val, level=level)
        return self.engine.encode(val)
    
    def encrypt(self, val):
        return self.engine.encrypt(val, self.pk)
    
    def decrypt(self, val):
        return self.engine.decrypt(val, self.sk)
    
    def encode_with_roots(self, val, n=BLOCK_SIZE):
        zeta = np.exp(-2j * np.pi / n)
        arr = np.array([zeta ** v for v in val], dtype=np.complex128)
        return self.encode(arr)
    
    def with_roots(self, val, n=BLOCK_SIZE):
        zeta = np.exp(-2j * np.pi / n)
        arr = np.array([zeta ** v for v in val], dtype=np.complex128)
        return arr
        
    def decode_to_real(self, val, num_inps=None, n=BLOCK_SIZE):
        theta = np.angle(val)
        theta = np.where(theta > 0, theta - 2 * np.pi, theta)
        k = np.round(-n * theta / (2 * np.pi)).astype(int) % n
        return k[:num_inps] if num_inps else k

def divide_bytes(val):
    upper = np.array([(b >> 4) & 0x0F for b in val])
    lower = np.array([b & 0x0F for b in val])
    return upper, lower

def gap_packing(val, ctx):
    gap = ctx.gap
    slot_values = np.zeros(ctx.slot_count)
    slot_values[::gap] = val
    return slot_values

def input_handler(input, ctx):
    upper, lower = divide_bytes(input)
    upper = gap_packing(upper, ctx)
    lower = gap_packing(lower, ctx)
    roots_upper = ctx.encode_with_roots(upper)
    roots_lower = ctx.encode_with_roots(lower)
    enc_upper = ctx.encrypt(roots_upper)
    enc_lower = ctx.encrypt(roots_lower)
    return enc_upper, enc_lower

def output_handler(enc_upper, enc_lower, ctx):
    dec_upper = ctx.decrypt(enc_upper)
    dec_lower = ctx.decrypt(enc_lower)
    decode_upper = ctx.decode_to_real(dec_upper, num_inps=ctx.slot_count)
    decode_lower = ctx.decode_to_real(dec_lower, num_inps=ctx.slot_count)
    return decode_upper, decode_lower

def output_print(enc_upper, enc_lower, res2, ctx):
    dec_upper, dec_lower = output_handler(enc_upper, enc_lower, ctx)
    gap = ctx.gap
    res = (dec_upper << 4) | dec_lower
    hex_matrix = np.vectorize(lambda x: f"{x:02X}")(res[::gap]).reshape((4, 4), order='F')
    hex2 = np.vectorize(lambda x: f"{x:02X}")(res2)
    print(">>> LEFT: fheAES, RIGHT: plain AES")
    for row1, row2 in zip(hex_matrix, hex2):
        line1 = '  '.join(row1)
        line2 = '  '.join(row2)
        print(f">>> {line1}    ||    {line2}")