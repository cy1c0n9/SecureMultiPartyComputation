import json	    # load
import sys	    # argv
import util
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
        inputs_:    dictionary of (input wire x input value)
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
        self.alice_ = a
        self.bob_ = b
        self.out_gate_id_ = out
        # print(self.inputs)

        # generate gates except input
        self.__gates_json_ = gates
        self.__generate_gates__()

        # generate input
        self.__input_table = self.__truth_table__(len(self.alice_) + len(self.bob_))

        self.__test__()

    def __generate_gates__(self):
        """
        generate gates
        :return: self.gates : dictionary of (gate id x Gate object)
        """
        self.gates_ = {}
        for g in self.__gates_json_:
            new_gate = Gate(self, g["id"], g["type"], g["in"])
            self.gates_[g["id"]] = new_gate
            # new_gate.print_out()

    def __generate_input__(self, in_data_list):
        """

        :param in_data_list:        list of input value
        :return: self.inputs :      dictionary of (input wire x input value)
        """
        self.inputs_ = {}
        input_wire_id_list = sorted(self.alice_ + self.bob_)

        for i, idx in enumerate(input_wire_id_list):
            self.inputs_[idx] = in_data_list[i]

        for idx, v in self.inputs_.items():
            new_gate = Gate(self, idx, "INPUT", [v])
            self.gates_[idx] = new_gate

    def __truth_table__(self, n):
        """
        recursive generate truth table for input
        :param n: dimension of the truth table
        :return:
        """
        if n < 1:
            return [[]]
        sub_table = self.__truth_table__(n - 1)
        return [row + [v] for row in sub_table for v in [0, 1]]

    def __run_circuit__(self):
        """
        launch circuit using given input in the self.input
        :return:
        """
        for out_id in self.out_gate_id_:
            res = self.gates_[out_id].run_gates()
            print(res)

    def construct_out(self):

        pass

    def get_gate_by_id(self, gate_id):
        return self.gates_[gate_id]

    def get_in_by_id(self, in_id):
        return self.inputs_[in_id]

    def print_out(self):
        util.log(self.name_ + ": ")
        util.log("Alice input wire:" + str(self.alice_))
        util.log("Bob input wire  :" + str(self.bob_))
        util.log("Output wire     :" + str(self.out_gate_id_))
        util.log("Gates           :" + str(self.__gates_json_))

    def __test__(self):
        self.__generate_input__([0, 1, 1, 0, 1])
        # util.log(self.__input_table)
        util.log(self.name_)
        # for idx, g in self.gates_.items():
        #     g.print_out()
        self.__run_circuit__()


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
        self.output_ = None

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

