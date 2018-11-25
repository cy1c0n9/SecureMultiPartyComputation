
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018

import yao
import time
import bob_ot
import util


class Bob:
    def __init__(self):
        context = bob_ot.zmq.Context()
        self.socket_ = context.socket(bob_ot.zmq.PAIR)
        self.socket_.connect("tcp://" + str(util.SERVER_HOST) + ":" + str(util.SERVER_PORT))
        self.json_ = None
        self.cir_ = None

    @staticmethod
    def __read_alice_key__(json_keys):
        wire_key_list = json_keys["alice_keys"]
        alice_key_val = {}
        for rec in wire_key_list:
            wire_id = rec['wire']
            val = rec['value']
            key = rec['key'].encode('utf-8')
            alice_key_val[wire_id] = (key, val)
        return alice_key_val

    def __truth_table__(self, n):
        if n < 1:
            return [[]]
        sub_table = self.__truth_table__(n-1)
        return [row + [v] for row in sub_table for v in [0, 1]]

    def __fire_1_circuit__(self):
        truth_t = self.__truth_table__(len(self.cir_.bob_))
        for i in range(2**len(self.cir_.alice_)):
            alice_key_json = self.socket_.recv_json()
            alice_key = self.__read_alice_key__(alice_key_json)
            for b_input in truth_t:
                bob_key = {}
                for idx, wire_id in enumerate(self.cir_.bob_):
                    key = bob_ot.bob(b_input[idx], self.socket_)
                    p_bit = self.cir_.input_p_bit_[wire_id]
                    val = b_input[idx] ^ p_bit
                    bob_key[wire_id] = (key, val)
                res = self.cir_.fire_circuit(alice_key, bob_key)
                file = open("out.txt", "a+")
                s_bob = " ".join(map(str, b_input))
                s_res = " ".join(map(str, res))
                file.write("Bob" + str(self.cir_.bob_) + " = " + s_bob + "   ")
                file.write("Outputs" + str(self.cir_.out_gate_id_) + " = " + s_res + "\n")
                file.close()

    def listen(self):
        while True:
            self.json_ = self.socket_.recv_json()
            self.cir_ = yao.BobCircuits(self.json_)
            self.__fire_1_circuit__()
