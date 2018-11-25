
# original transform through json file
# yao garbled circuit evaluation v1. simple version based on smart
# lin liu, dept of computing, imperial college, october 2018
import json
import util


# Alice functions of OT
class Alice:
    def __init__(self, M):
        #  M responds to kb0 kb1   including m0,m1
        self.M = M
        self.G = util.PrimeGroup()
        k = self.G.rand_int()
        self.c = self.G.primeM1

    # Alice sends a randint c to Bob  -- the first step of OT
    def alice_sendc(self):
        j = {"c": self.c}
        # print("c:"+str(type(self.c)))
        # with open(file_name, 'w') as f:
        #     json.dump(j, f)
        # print("alice generates and sends c -- the first step of OT")
        return self.c

    def alice_sende(self, h0):

        # print("received h0:" + str(type(h0)))
        h1 = self.G.mul(self.G.inv(h0), self.c)

        k = self.G.primeM1
        c1 = self.G.gen_pow(k)

        # m0 = bytes(str(self.M[0]), 'utf-8')
        # m1 = bytes(str(self.M[1]), 'utf-8')
        m0 = self.M[0]
        m1 = self.M[1]
        h0k = self.G.pow(h0, k)
        H0 = util.ot_hash(h0k, len(str(m0)))
        e0 = util.xor_bytes(m0, H0)
        h1k = self.G.pow(h1, k)
        H1 = util.ot_hash(h1k, len(str(m1)))
        e1 = util.xor_bytes(m1, H1)
        j = {"c1": c1, "e0": e0, "e1": e1}
        # print("c1:"+str(type(c1))+"e0:"+str(type(e0))+"e1:"+str(type(e1)))
        return c1, e0, e1


# Bob functions of OT
class Bob:
    def __init__(self, b):   # b refers to which Bob selects
        self.b = b
        self.G = util.PrimeGroup()
        self.x = self.G.rand_int()

    # Bob gets c from Alice(step 1)
    def bob_setup(self, c):
        # with open(alice_filename) as f:
        #     alice = json.load(f)
        # print("receive c:"+str(type(c)))
        x = self.G.prime
        if self.b == 0:
            h0 = self.G.gen_pow(x)
        else:
            h0 = self.G.mul(c, self.G.inv(self.G.gen_pow(x)))
        # print("Bob sends hb -- the second step of OT")
        # print("h0:"+str(type(h0)))
        return h0

    def bob_decode(self, c1, e0, e1):
        if self.b == 0:
            H = util.ot_hash(self.G.pow(c1, self.x), len(e0))
            mb = util.xor_bytes(e0, H)
        else:
            H = util.ot_hash(self.G.pow(c1, self.x), len(e1))
            mb = util.xor_bytes(e1, H)
        return mb

# def OT(M,b):
#     alice = Alice(M)
#     c = alice.Alice_sendc()
#     bob = Bob(b)
#     h0 = bob.Bob_setup(c)
#     c1, e0, e1 = alice.Alice_sende(h0)
#     # bob.Bob_setup()
#     mb = bob.Bob_decode(c1, e0, e1)
#     return mb
#
#
# M = ["message1", "message2"]
# b = 1
# print(OT(M,b))




