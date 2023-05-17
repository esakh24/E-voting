
from crypto.Util.number import *
from crypto import Random
import crypto
import random
import libnum
import sys
import hashlib
import ast

def str_to_list(enc1:str):
    # initializing string representation of a list
    ini_list = enc1


    # Converting string to list
    res = ast.literal_eval(ini_list)
    return res

def get_generator(p: int):
    while True:
        # Find generator which doesn't share factor with p
        generator = random.randrange(3, p)
        if pow(generator, 2, p) == 1:
            continue
        if pow(generator, p, p) == 1:
            continue
        return generator
def generate_keys(bits = 512):
    bits=512
    p = crypto.Util.number.getPrime(bits, randfunc=crypto.Random.get_random_bytes) # cyclic group   
    g = get_generator(p)  
    x = random.randrange(3, p)  # private key
    Y = pow(g,x,p) # h
    return p,g,Y,x
v1=10
v2=5


# print (f"v1={v1}\nv2={v2}\n")
# print (f"Public key:\ng={g}\nY={Y}\np={p}\n\nPrivate key\nx={x}")
def encrypt_votes(vote, p, g, Y, audit_vote = False):
    k1=random.randrange(3, p)  # random number
#     a1=pow(g,k1,p) # g^random
#     b1=(pow(Y,k1,p)*pow(g,v1,p)) % p # g^m * h^random
    enc_vote = [(pow(g,k1,p), (pow(Y,k1,p)*pow(g,v1,p)) % p) for v1 in vote]
    if audit_vote is True:
        return enc_vote, k1
    return enc_vote

# k2=random.randrange(3, p)  
# a2=pow(g,k2,p)
# b2=(pow(Y,k2,p)*pow(g,v2,p)) % p
def add_encrypted_votes(p, *args):
    # homomorphic addition
    if(len(args)>0):
        enc_vote = args[0]
        for i in range(1,len(args)):
          
            enc_vote = [((a1*a2)%p, (b1*b2)%p) for (a1,b1),(a2,b2) in zip(enc_vote,args[i])]
        return enc_vote
    return []



# decryption
def decrypt_vote(enc_vote, x, p, g):
    v_r=[(b*libnum.invmod(pow(a,x,p),p)) % p for(a,b) in enc_vote]
    dvr = [None] * len(v_r)
    for j in range(len(v_r)):
        vr=v_r[j]
        for i in range(0,2**64):
            if (pow(g,i,p)==vr):
                
                dvr[j] = i
                break
    return dvr

# print ("\nResult: ",v_r )


# Now search for g^i
