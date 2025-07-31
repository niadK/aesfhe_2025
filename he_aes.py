import numpy as np
from he_lut import get_power_basis, eval_multivar_poly, sim_eval_multivar_poly

## shiftRows ##
def shiftRows_small(ct, ctx):
    gap = ctx.gap
    mask = np.zeros(ctx.slot_count)
    mask[::gap * 4] = 1
    res = None
    for _ in range(4):
        masked = ctx.multiply(ct, mask)
        res = ctx.add(res, masked) if res else masked
        ct = ctx.rotate(ct, -4*gap)
        mask = np.roll(mask, gap)
    return res

def HEshiftRows(enc_upper, enc_lower, ctx):
    out_upper = shiftRows_small(enc_upper, ctx)
    out_lower = shiftRows_small(enc_lower, ctx)
    return out_upper, out_lower

## XOR ##
def HEaddRoundKey(enc_upper, enc_lower, key_upper, key_lower, C_xor_lower, ctx):
    u_power_basis_upper = get_power_basis(enc_upper, ctx)
    u_power_basis_lower = get_power_basis(key_upper, ctx)
    l_power_basis_upper = get_power_basis(enc_lower, ctx)
    l_power_basis_lower = get_power_basis(key_lower, ctx)
    out_upper = eval_multivar_poly(u_power_basis_upper, u_power_basis_lower, C_xor_lower, ctx)
    out_lower = eval_multivar_poly(l_power_basis_upper, l_power_basis_lower, C_xor_lower, ctx)
    return out_upper, out_lower

## subBytes ##
def HEsubBytes(enc_upper, enc_lower, C_sbox_upper, C_sbox_lower, ctx):
    power_basis_upper = get_power_basis(enc_upper, ctx)
    power_basis_lower = get_power_basis(enc_lower, ctx)
    out_upper, out_lower = sim_eval_multivar_poly(power_basis_upper, power_basis_lower, C_sbox_upper, C_sbox_lower, ctx)
    return out_upper, out_lower

# mixColumns
def make_gap_row(base, ctx):
    gap = ctx.gap
    slot_count = ctx.slot_count
    row = np.zeros(slot_count)
    for i, val in enumerate(base):
        start = i * gap
        end = start + gap
        row[start:min(end, slot_count)] = val
    return ctx.encode(row)

def combine_rows(M0, M1, M2, M3, ct1, ct2, ct3, C_xor, ctx):
    gap = ctx.gap

    #print("R0 start")
    t00 = ctx.intt(ctx.multiply(ct2, M0))
    pb00 = get_power_basis(t00, ctx)
    
    t01 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M1), -1*gap))   
    pb01 = get_power_basis(t01, ctx)
    R0 = ctx.intt(eval_multivar_poly(pb00, pb01, C_xor, ctx))
    #R0 = ctx.bootstrap(R0)
    pbR0 = get_power_basis(R0, ctx)
    
    t02 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M2), -2*gap))
    pb02 = get_power_basis(t02, ctx)
    R0 = ctx.intt(eval_multivar_poly(pbR0, pb02, C_xor, ctx))
    #R0 = ctx.bootstrap(R0)
    pbR0 = get_power_basis(R0, ctx)
    
    t03 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M3), -3*gap))  
    pb03 = get_power_basis(t03, ctx)
    R0 = ctx.intt(eval_multivar_poly(pbR0, pb03, C_xor, ctx))    

    #print("R1 start")
    t10 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M0), +1*gap))   
    pb10 = get_power_basis(t10, ctx)
    
    t11 = ctx.intt(ctx.multiply(ct2, M1))                                  
    pb11 = get_power_basis(t11, ctx)
    R1 = ctx.intt(eval_multivar_poly(pb10, pb11, C_xor, ctx))        
    #R1 = ctx.bootstrap(R1)
    pbR1 = get_power_basis(R1, ctx)

    t12 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M2), -1*gap))  
    pb12 = get_power_basis(t12, ctx)
    R1 = ctx.intt(eval_multivar_poly(pbR1, pb12, C_xor, ctx))
    #R1 = ctx.bootstrap(R1)
    pbR1 = get_power_basis(R1, ctx)

    t13 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M3), -2*gap))  
    pb13 = get_power_basis(t13, ctx)
    R1 = ctx.intt(eval_multivar_poly(pbR1, pb13, C_xor, ctx))

    #print("R2 start")
    t20 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M0), +2*gap))   
    pb20 = get_power_basis(t20, ctx)
    
    t21 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M1), +1*gap))  
    pb21 = get_power_basis(t21, ctx)
    R2 = ctx.intt(eval_multivar_poly(pb20, pb21, C_xor, ctx))        
    #R2 = ctx.bootstrap(R2)
    pbR2 = get_power_basis(R2, ctx)

    t22 = ctx.intt(ctx.multiply(ct2, M2))                                
    pb22 = get_power_basis(t22, ctx)
    R2 = ctx.intt(eval_multivar_poly(pbR2, pb22, C_xor, ctx))
    #R2 = ctx.bootstrap(R2)
    pbR2 = get_power_basis(R2, ctx)

    t23 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M3), -1*gap))  
    pb23 = get_power_basis(t23, ctx)
    R2 = ctx.intt(eval_multivar_poly(pbR2, pb23, C_xor, ctx))

    #print("R3 start")
    t30 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M0), +3*gap))   
    pb30 = get_power_basis(t30, ctx)
    
    t31 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M1), +2*gap)) 
    pb31 = get_power_basis(t31, ctx)
    R3 = ctx.intt(eval_multivar_poly(pb30, pb31, C_xor, ctx))         
    #R3 = ctx.bootstrap(R3)
    pbR3 = get_power_basis(R3, ctx)

    t32 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M2), +1*gap))  
    pb32 = get_power_basis(t32, ctx)
    R3 = ctx.intt(eval_multivar_poly(pbR3, pb32, C_xor, ctx))
    #R3 = ctx.bootstrap(R3)
    pbR3 = get_power_basis(R3, ctx)

    t33 = ctx.intt(ctx.multiply(ct2, M3))                              
    pb33 = get_power_basis(t33, ctx)
    R3 = ctx.intt(eval_multivar_poly(pbR3, pb33, C_xor, ctx))

    return ctx.add(ctx.add(R0, R1), ctx.add(R2, R3))

def combine_rowsBT(M0, M1, M2, M3, ct1, ct2, ct3, C_xor, ctx):
    gap = ctx.gap

    #print("R0 start")
    t00 = ctx.intt(ctx.multiply(ct2, M0))
    pb00 = get_power_basis(t00, ctx)
    
    t01 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M1), -1*gap))   
    pb01 = get_power_basis(t01, ctx)
    R0 = ctx.intt(eval_multivar_poly(pb00, pb01, C_xor, ctx))
    R0 = ctx.bootstrap(R0)
    pbR0 = get_power_basis(R0, ctx)
    
    t02 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M2), -2*gap))
    pb02 = get_power_basis(t02, ctx)
    R0 = ctx.intt(eval_multivar_poly(pbR0, pb02, C_xor, ctx))
    R0 = ctx.bootstrap(R0)
    pbR0 = get_power_basis(R0, ctx)
    
    t03 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M3), -3*gap))  
    pb03 = get_power_basis(t03, ctx)
    R0 = ctx.intt(eval_multivar_poly(pbR0, pb03, C_xor, ctx))    

    #print("R1 start")
    t10 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M0), +1*gap))   
    pb10 = get_power_basis(t10, ctx)
    
    t11 = ctx.intt(ctx.multiply(ct2, M1))                                  
    pb11 = get_power_basis(t11, ctx)
    R1 = ctx.intt(eval_multivar_poly(pb10, pb11, C_xor, ctx))        
    R1 = ctx.bootstrap(R1)
    pbR1 = get_power_basis(R1, ctx)

    t12 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M2), -1*gap))  
    pb12 = get_power_basis(t12, ctx)
    R1 = ctx.intt(eval_multivar_poly(pbR1, pb12, C_xor, ctx))
    R1 = ctx.bootstrap(R1)
    pbR1 = get_power_basis(R1, ctx)

    t13 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M3), -2*gap))  
    pb13 = get_power_basis(t13, ctx)
    R1 = ctx.intt(eval_multivar_poly(pbR1, pb13, C_xor, ctx))

    #print("R2 start")
    t20 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M0), +2*gap))   
    pb20 = get_power_basis(t20, ctx)
    
    t21 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M1), +1*gap))  
    pb21 = get_power_basis(t21, ctx)
    R2 = ctx.intt(eval_multivar_poly(pb20, pb21, C_xor, ctx))        
    R2 = ctx.bootstrap(R2)
    pbR2 = get_power_basis(R2, ctx)

    t22 = ctx.intt(ctx.multiply(ct2, M2))                                
    pb22 = get_power_basis(t22, ctx)
    R2 = ctx.intt(eval_multivar_poly(pbR2, pb22, C_xor, ctx))
    R2 = ctx.bootstrap(R2)
    pbR2 = get_power_basis(R2, ctx)

    t23 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M3), -1*gap))  
    pb23 = get_power_basis(t23, ctx)
    R2 = ctx.intt(eval_multivar_poly(pbR2, pb23, C_xor, ctx))

    #print("R3 start")
    t30 = ctx.intt(ctx.rotate(ctx.multiply(ct3, M0), +3*gap))   
    pb30 = get_power_basis(t30, ctx)
    
    t31 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M1), +2*gap)) 
    pb31 = get_power_basis(t31, ctx)
    R3 = ctx.intt(eval_multivar_poly(pb30, pb31, C_xor, ctx))         
    R3 = ctx.bootstrap(R3)
    pbR3 = get_power_basis(R3, ctx)

    t32 = ctx.intt(ctx.rotate(ctx.multiply(ct1, M2), +1*gap))  
    pb32 = get_power_basis(t32, ctx)
    R3 = ctx.intt(eval_multivar_poly(pbR3, pb32, C_xor, ctx))
    R3 = ctx.bootstrap(R3)
    pbR3 = get_power_basis(R3, ctx)

    t33 = ctx.intt(ctx.multiply(ct2, M3))                              
    pb33 = get_power_basis(t33, ctx)
    R3 = ctx.intt(eval_multivar_poly(pbR3, pb33, C_xor, ctx))

    return ctx.add(ctx.add(R0, R1), ctx.add(R2, R3))

def HEmixCols(enc_upper, enc_lower, C2_upper, C2_lower, C3_upper, C3_lower, C_xor, ctx):
    
    power_basis_upper = get_power_basis(enc_upper, ctx)
    power_basis_lower = get_power_basis(enc_lower, ctx)
    
    #print("gfmul start")
    upper_2, lower_2 = sim_eval_multivar_poly(power_basis_upper, power_basis_lower, C2_upper, C2_lower, ctx)
    upper_3, lower_3 = sim_eval_multivar_poly(power_basis_upper, power_basis_lower, C3_upper, C3_lower, ctx)
    #print("gfmul done")
    
    upper_2 = ctx.intt(upper_2)
    lower_2 = ctx.intt(lower_2)
    upper_3 = ctx.intt(upper_3)
    lower_3 = ctx.intt(lower_3)
    # upper_2 = ctx.bootstrap(upper_2)
    # lower_2 = ctx.bootstrap(lower_2)
    # upper_3 = ctx.bootstrap(upper_3)
    # lower_3 = ctx.bootstrap(lower_3)
    
    row0 = [1,0,0,0] * 4
    row1 = [0,1,0,0] * 4
    row2 = [0,0,1,0] * 4
    row3 = [0,0,0,1] * 4
    
    M0 = make_gap_row(row0, ctx)
    M1 = make_gap_row(row1, ctx)
    M2 = make_gap_row(row2, ctx)
    M3 = make_gap_row(row3, ctx)
    
    out_upper = combine_rows(M0, M1, M2, M3, enc_upper, upper_2, upper_3, C_xor, ctx)
    out_lower = combine_rows(M0, M1, M2, M3, enc_lower, lower_2, lower_3, C_xor, ctx)
    
    return out_upper, out_lower

def HEmixColsBT(enc_upper, enc_lower, C2_upper, C2_lower, C3_upper, C3_lower, C_xor, ctx):
    
    power_basis_upper = get_power_basis(enc_upper, ctx)
    power_basis_lower = get_power_basis(enc_lower, ctx)
    
    #print("gfmul start")
    upper_2, lower_2 = sim_eval_multivar_poly(power_basis_upper, power_basis_lower, C2_upper, C2_lower, ctx)
    upper_3, lower_3 = sim_eval_multivar_poly(power_basis_upper, power_basis_lower, C3_upper, C3_lower, ctx)
    #print("gfmul done")
    
    upper_2 = ctx.intt(upper_2)
    lower_2 = ctx.intt(lower_2)
    upper_3 = ctx.intt(upper_3)
    lower_3 = ctx.intt(lower_3)
    upper_2 = ctx.bootstrap(upper_2)
    lower_2 = ctx.bootstrap(lower_2)
    upper_3 = ctx.bootstrap(upper_3)
    lower_3 = ctx.bootstrap(lower_3)
    
    row0 = [1,0,0,0] * 4
    row1 = [0,1,0,0] * 4
    row2 = [0,0,1,0] * 4
    row3 = [0,0,0,1] * 4
    
    M0 = make_gap_row(row0, ctx)
    M1 = make_gap_row(row1, ctx)
    M2 = make_gap_row(row2, ctx)
    M3 = make_gap_row(row3, ctx)
    
    out_upper = combine_rowsBT(M0, M1, M2, M3, enc_upper, upper_2, upper_3, C_xor, ctx)
    out_lower = combine_rowsBT(M0, M1, M2, M3, enc_lower, lower_2, lower_3, C_xor, ctx)
    
    return out_upper, out_lower

def Bootstrapping(upper, lower, ctx):
    out_upper = ctx.intt(upper)
    out_lower = ctx.intt(lower)
    out_upper = ctx.bootstrap(out_upper)
    out_lower = ctx.bootstrap(out_lower)
    return out_upper, out_lower
    