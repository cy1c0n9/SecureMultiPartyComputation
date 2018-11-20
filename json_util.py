import json	    # load
import sys	    # argv


# Class for circuit ________________________________________________
class Circuits:
    def __init__(self, name, a, b, out, gates):
        """

        :param name:    circuits name
        :param a:       list of alice's input wire
        :param b:       list of bob's input wire
        :param out:     list of output wire
        :param gates:   [{"id":3, "type":"AND", "in": [1, 2]]}]
        """
        self.name = name
        self.alice = a
        self.bob = b
        self.out = out
        self.gates_json = gates
        self.gates = {}
        for g in self.gates_json:
            new_gate = Gate(self, g["id"], g["type"], g["in"])
            self.gates[g["id"]] = new_gate
            new_gate.print_out()

        self.gate_ids = []
        self.output_gate_ids = []
        print(self.gates)

    def print_out(self):
        print(self.name + ": ")
        print("Alice input wire:", end=" ")
        print(self.alice)
        print("Bob input wire  :", end=" ")
        print(self.bob)
        print("Output wire     :", end=" ")
        print(self.out)
        print("Gates:", end=" ")
        print(self.gates_)


class Gate:
    def __init__(self, circuit, gate_id, type_, inputs):
        self.circuit = circuit
        self.type = type_
        self.gate_id = gate_id
        self.inputs = inputs
        self.output = None

    def construct(self):
        """
        construct gate according to type:
        NOT , OR , AND , XOR , NOR , NAND , XNOR
        :return:
        """
        input0 = self.circuit.get(self.inputs[0]).construct()
        input1 = 0
        if self.type != "NOT":
            input1 = self.circuit.get(self.inputs[1]).construct()

        if self.output is None:
            if self.type == "NOT":
                self.output = 1 - input0
            elif self.type == "OR":
                self.output = input0 or input1
            elif self.type == "AND":
                self.output = input0 and input1
            elif self.type == "XOR":
                self.output = input0 ^ input1
            elif self.type == "NOR":
                self.output = 1 - (input0 or input1)
            elif self.type == "NAND":
                self.output = 1 - (input0 and input1)
            elif self.type == "XNOR":
                self.output = 1 - (input0 ^ input1)
            else:
                print("bad gate type")

        return self.output

    def reset(self):
        self.output = None

    def print_out(self):
        print(self.circuit.name + ": ")
        print("type     :", end=" ")
        print(self.type)
        print("gate id  :", end=" ")
        print(self.gate_id)
        print("inputs   :", end=" ")
        print(self.inputs)
        print("outputs  :", end=" ")
        print(self.output)


# for json reading _________________________________________________
def get_attribute(data, attribute, default_value):
    return data.get(attribute) or default_value

