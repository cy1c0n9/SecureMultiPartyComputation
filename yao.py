
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018

import json	    # load
import sys	    # argv
import util     # log
import crypto
import itertools


# Class for circuit ________________________________________________
class Circuits:
    """
    Attributes:
        name_:      name of the circuits
        alice_:     list of alice's input wire
        bob_:       list of bob's input wire
        out_gate_id_:       list of output wire
        gates_:     dictionary of (gate id x Gate object)
        inputs_keys_:    dictionary of (input wire id : key pair)
    """

    def __init__(self, name, a, b, out, gates):
        """
        :param name:    circuits name
        :param a:       list of alice's input wire
        :param b:       list of bob's input wire
        :param out:     list of output wire
        :param gates:   [{"id":3, "type":"AND", "in": [1, 2]]}]
        """
        self.name_ = name
        util.log(self.name_ + ":")
        self.alice_ = a
        self.bob_ = b
        self.out_gate_id_ = out
        # generate inputs
        self.inputs_keys_ = {}
        self.__generate_input__()
        # generate gates
        self.__generate_gates__(gates)
        # self.__test__()

    def __generate_gates__(self, gates_json):
        """
        initialize all gates
        :return: self.gates : dictionary of (gate id : Gate object)
        """
        self.gates_ = {}
        for g in gates_json:
            new_gate = Gate(self, g["id"], g["type"], g["in"])
            new_gate.make_garble_table()
            self.gates_[g["id"]] = new_gate
            new_gate.print_garble_table()

    def __generate_input__(self):
        """
        :return: self.inputs_keys :   dictionary of (wire : key pair)
        """
        self.inputs_keys_ = {}
        input_wire_id_list = sorted(self.alice_ + self.bob_)

        for i, idx in enumerate(input_wire_id_list):
            self.inputs_keys_[idx] = crypto.key_pair()
        # util.log(str(self.inputs_keys_))

    def __run_circuit__(self):
        """
        launch circuit using given input in the self.input
        :return:
        """
        for out_id in self.out_gate_id_:
            res = self.gates_[out_id].run_gates()
            print(res)

    def get_gate_by_id(self, gate_id):
        return self.gates_[gate_id]

    def get_in_keys_by_id(self, in_id):
        return self.inputs_keys_[in_id]

    def print_out(self):
        util.log(self.name_ + ": ")
        util.log("Alice input wire:" + str(self.alice_))
        util.log("Bob input wire  :" + str(self.bob_))
        util.log("Output wire     :" + str(self.out_gate_id_))
        for idx, g in self.gates_.items():
            g.print_out()

    def __test__(self):
        print(str(crypto.key_pair()[0].hex()))

        # self.__generate_input__([0, 1, 1, 0, 1])
        # util.log(self.__input_table)
        util.log(self.name_)
        for idx, g in self.gates_.items():
            g.print_out()
        self.__run_circuit__()
        pass


class Gate:
    def __init__(self, circuit, gate_id, type_, inputs):
        """

        :param circuit: Circuit that the gate belongs to
        :param gate_id: int
        :param type_:   string
        :param inputs:  list of input gate id
        """
        self.circuit_ = circuit
        self.type_ = type_
        self.gate_id_ = gate_id
        self.inputs_ = inputs
        self.garble_table_ = {}
        self.input_keys_ = {}
        # self.input_keys_ = {0: {0:key_a0, 1:key_a1}, 1: {0:key_b0, 1:key_b1}}
        for i, idx in enumerate(self.inputs_):
            try:
                self.input_keys_[i] = self.circuit_.get_gate_by_id(idx).output_keys_
            except KeyError:
                self.input_keys_[i] = self.circuit_.get_in_keys_by_id(idx)

        self.output_keys_ = crypto.key_pair()
        self.output_ = None

    @staticmethod
    def __truth_table__(n):
        """
        :param n: dimension of the truth table
        :return:  list of tuple
        """
        # if n < 1:
        #     return [[]]
        # sub_table = self.__truth_table__(n - 1)
        # return [row + [v] for row in sub_table for v in [0, 1]]
        return list(itertools.product([0, 1], repeat=n))

    def run_gates(self):
        """
        construct gate according to type:
        NOT , OR , AND , XOR , NOR , NAND , XNOR
        INPUT gate: retrieve the value of input
        :return:
        """

        input0 = 0
        input1 = 0
        if self.type_ != "INPUT":
            input_gate0 = self.circuit_.get_gate_by_id(self.inputs_[0])
            if input_gate0.output_ is None:
                input0 = input_gate0.run_gates()
            else:
                input0 = input_gate0.output_
        if self.type_ != "NOT" and self.type_ != "INPUT":
            input_gate1 = self.circuit_.get_gate_by_id(self.inputs_[1])
            if input_gate1.output_ is None:
                input1 = input_gate1.run_gates()
            else:
                input1 = input_gate1.output_

        if self.output_ is None:
            if self.type_ == "NOT":
                self.output_ = 1 - input0
            elif self.type_ == "OR":
                self.output_ = input0 or input1
            elif self.type_ == "AND":
                self.output_ = input0 and input1
            elif self.type_ == "XOR":
                self.output_ = input0 ^ input1
            elif self.type_ == "NOR":
                self.output_ = 1 - (input0 or input1)
            elif self.type_ == "NAND":
                self.output_ = 1 - (input0 and input1)
            elif self.type_ == "XNOR":
                self.output_ = 1 - (input0 ^ input1)
            elif self.type_ == "INPUT":
                self.output_ = self.circuit_.get_in_by_id(self.gate_id_)
            else:
                util.log("bad gate type")
        self.print_out()
        return self.output_

    def make_garble_table(self):
        """
        Ek[2, x], k[4, y](k[6, z], t) where x = 0⊕p[2], y = 0⊕p[4], z = XOR(x, y), t = z⊕p[6]
        x -> entry[0]
        y -> entry[1]
        z -> out_val
        t = z
        :return:
        """
        # table -> list of (key, index)
        table = []

        if self.type_ == "NOT":
            truth_table = self.__truth_table__(1)
        else:
            truth_table = self.__truth_table__(2)

        for entry in truth_table:
            wire0_idx = 0
            wire1_idx = 0
            try:
                wire0_idx = entry[0]
            except IndexError:
                util.log("invalid gate input")
            try:
                wire1_idx = entry[1]
            except IndexError:
                pass

            if self.type_ == "NOT":
                out_val = 1 - wire0_idx
            elif self.type_ == "OR":
                out_val = wire0_idx or wire1_idx
            elif self.type_ == "AND":
                out_val = wire0_idx and wire1_idx
            elif self.type_ == "XOR":
                out_val = wire0_idx ^ wire1_idx
            elif self.type_ == "NOR":
                out_val = 1 - (wire0_idx or wire1_idx)
            elif self.type_ == "NAND":
                out_val = 1 - (wire0_idx and wire1_idx)
            elif self.type_ == "XNOR":
                out_val = 1 - (wire0_idx ^ wire1_idx)
            else:
                out_val = -1
                util.log("bad gate type")
            try:
                encrypt_key = crypto.encrypt(crypto.encrypt(self.output_keys_[out_val],
                                                            self.input_keys_[1][wire1_idx]),
                                             self.input_keys_[0][wire0_idx])
            except KeyError:
                encrypt_key = crypto.encrypt(self.output_keys_[out_val],
                                             self.input_keys_[0][wire0_idx])
            table.append((encrypt_key, out_val))

        for i, entry in enumerate(truth_table):
            self.garble_table_[entry] = table[i]

    def print_garble_table(self, verbose=0):
        util.log("gate id   :" + str(self.gate_id_) + "     gate type   :" + str(self.type_))
        if verbose == 2:
            for key, val in self.garble_table_.items():
                util.log("      " + str(key) + "  -> input key 0: " + str(self.input_keys_[0][key[0]]))
                try:
                    util.log("              -> input key 1: " + str(self.input_keys_[1][key[1]]))
                except KeyError:
                    pass
                util.log("              ->  output: " + str(val))
        elif verbose == 1:
            for key, val in self.garble_table_.items():
                util.log("      " + str(key) + "   ->   " + str(val))
        elif verbose == 0:
            for key, val in self.garble_table_.items():
                util.log("      " + str(key) + "   ->   " + str(val[1]))

    def reset(self):
        self.output_ = None

    def print_out(self):
        util.log(self.circuit_.name_ + ": ")
        util.log("type     :" + str(self.type_))
        util.log("gate id  :" + str(self.gate_id_))
        util.log("inputs   :" + str(self.inputs_))
        util.log("outputs  :" + str(self.output_))


# for json reading _________________________________________________
def get_attribute(data, attribute, default_value):
    return data.get(attribute) or default_value

