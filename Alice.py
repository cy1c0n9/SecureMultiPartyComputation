
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018

import yao
import time
import alice_ot
import util


class Alice:
    """
    Attributes:
        name_:          name of the circuits
        alice_:         list of alice's input wire id
        bob_:           list of bob's input wire id
        out_id_:        list of output wire id
    """
    def __init__(self, json_circuits):
        context = alice_ot.zmq.Context()
        self.socket_ = context.socket(alice_ot.zmq.PAIR)
        self.socket_.bind("tcp://*:" + str(util.SERVER_PORT))
        for json_circuit in json_circuits['circuits']:
            self.name_ = json_circuit["name"]
            self.alice_ = yao.get_attribute(json_circuit, "alice", [])
            self.bob_ = yao.get_attribute(json_circuit, "bob", [])
            self.out_id_ = json_circuit["out"]
            self.cir_ = yao.AliceCircuits(self.name_,
                                          self.alice_,
                                          self.bob_,
                                          self.out_id_,
                                          json_circuit["gates"])
            circuit_json = self.cir_.convert_gt_to_json()
            self.socket_.send_json(circuit_json)
            self.__setup_circuit__()

    def __truth_table__(self, n):
        if n < 1:
            return [[]]
        sub_table = self.__truth_table__(n-1)
        return [row + [v] for row in sub_table for v in [0, 1]]

    def __setup_circuit__(self):
        truth_t = self.__truth_table__(len(self.alice_))
        file = open("out.txt", "a+")
        file.write("======= " + self.name_ + " =======\n")
        file.close()
        for a_input in truth_t:
            wire_val = {}
            for idx, input_wire in enumerate(self.alice_):
                wire_val[input_wire] = a_input[idx]
            alice_key = self.__convert_keys_to_json__(wire_val)
            self.socket_.send_json(alice_key)
            for i in range(2**len(self.bob_)):
                file = open("out.txt", "a")
                s = " ".join(map(str, a_input))
                file.write("  Alice" + str(self.alice_) + " = " + s + "  ")
                file.close()
                for wire_id in self.bob_:
                    wire = self.cir_.get_wire_by_id(wire_id)
                    message = [wire.key_pair_[0], wire.key_pair_[1]]
                    alice_ot.alice(message, self.socket_)
                time.sleep(0.1)
        file = open("out.txt", "a")
        file.write("\n")
        file.close()

    def __convert_keys_to_json__(self, wire_val):
        """
        :param wire_val:    dict
        :return:
        """
        j = {"alice_keys": []}
        for wire_id, val in wire_val.items():
            wire = self.cir_.get_wire_by_id(wire_id)
            val_after_p_bit = val ^ wire.p_bit_
            input_json = {"wire" : wire_id,
                          "value": val_after_p_bit,
                          "key"  : wire.key_pair_[val]}
            j["alice_keys"].append(input_json)
        return j




