from probset.hdlbits_probset import HDLBitsProbSet

def create_probset(probset_name, probset_paras):
    if probset_name == "HDLBits":
        return HDLBitsProbSet(**probset_paras)