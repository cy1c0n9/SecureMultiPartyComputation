
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018

import json	    # dump
import sys	    # argv
import util     # log
import crypto
import base64
import itertools

DEBUG = 0
ALICE_INPUT_KEYS = {}
BOB_INPUT_KEYS = {}


# Class for circuit ________________________________________________
class Circuits:
    """
    Attributes:
        name_:          name of the circuits
        alice_:         list of alice's input wire id
        bob_:           list of bob's input wire id
        out_gate_id_:   list of output wire id
    """

    def __init__(self, name, a, b, out):
        """
        :param name:    circuits name
        :param a:       list of alice's input wire
        :param b:       list of bob's input wire
        :param out:     list of output wire
        """
        self.name_ = name
        util.log(self.name_ + ":")
        self.alice_ = a
        self.bob_ = b
        self.out_gate_id_ = out

    # def __run_circuit__(self, input_value_list):
    #     """
    #     launch circuit using given input in the self.input
    #     :return:
    #     """
    #     input_id_list = sorted(self.alice_ + self.bob_)
    #     for i, val in enumerate(input_value_list):
    #         wire_id = input_id_list[i]
    #         in_wire = self.get_wire_by_id(wire_id)
    #         in_wire.value_ = val
    #     for out_id in self.out_gate_id_:
    #         res = self.gates_[out_id].estimate_gates()
    #         print(res)


class AliceCircuits(Circuits):
    """
    Attributes:
        gates_:         dictionary of (gate id : Gate object)
        wires_:         dictionary of (wire id : AliceWire object)
        inputs_keys_:   dictionary of (input wire id : key pair)
    """

    def __init__(self, name, a, b, out, gates):
        """
        :param name:    circuits name
        :param a:       list of alice's input wire
        :param b:       list of bob's input wire
        :param out:     list of output wire
        :param gates:   [{"id":3, "type":"AND", "in": [1, 2]]}]
        """
        Circuits.__init__(self, name, a, b, out)
        self.inputs_keys_ = {}
        self.wires_ = {}
        self.gates_ = {}
        # generate inputs
        self.__generate_input__()
        # generate gates
        self.__generate_gates__(gates)
        self.convert_gt_to_json()
        if DEBUG:
            # test
            self.__test__()

    def __generate_input__(self):
        """
        :return: self.inputs_keys :   dictionary of (wire id : Wire)
        """
        self.inputs_keys_ = {}
        input_wire_id_list = sorted(self.alice_ + self.bob_)

        for i, idx in enumerate(input_wire_id_list):
            wire = AliceWire(idx, crypto.key_pair())
            self.inputs_keys_[idx] = wire
            self.wires_[idx] = wire

    def __generate_gates__(self, gates_json):
        """
        initialize all gates
        :return: self.gates : dictionary of (gate id : Gate object)
        """
        self.gates_ = {}
        for g in gates_json:
            new_gate = Gate(self, g["id"], g["type"], g["in"])
            self.wires_[new_gate.gate_id_] = new_gate.output_wire_
            new_gate.make_garble_table()
            self.gates_[g["id"]] = new_gate
            # new_gate.convert_gt_to_json()
            # new_gate.print_garble_table()

    def convert_gt_to_json(self):
        j = {"circuit"  : self.name_,
             "alice"    : self.alice_,
             "bob"      : self.bob_,
             "bob_p_bit": [],
             "out_wire" : self.out_gate_id_,
             "p_bit"    : [],
             "gt_list"  : []}
        for wire_id in self.bob_:
            p_bit_json = {"wire": wire_id,
                          "p_bit": self.get_wire_by_id(wire_id).p_bit_}
            j["bob_p_bit"].append(p_bit_json)
        for out_id in self.out_gate_id_:
            p_bit_json = {"wire" : out_id,
                          "p_bit": self.get_wire_by_id(out_id).p_bit_}
            j["p_bit"].append(p_bit_json)
        for gate_id, gate in self.gates_.items():
            gate_json = gate.convert_gt_to_json()
            j["gt_list"].append(gate_json)
        with open('json_out/' + self.name_ + '.json', 'w') as outfile:
            json.dump(j, outfile, indent=4)
        return j

    def get_gate_by_id(self, gate_id):
        return self.gates_[gate_id]

    def get_in_keys_by_id(self, in_id):
        return self.inputs_keys_[in_id]

    def get_wire_by_id(self, wire_id):
        return self.wires_[wire_id]

    def print_out(self):
        util.log(self.name_ + ": ")
        util.log("Alice input wire:" + str(self.alice_))
        util.log("Bob input wire  :" + str(self.bob_))
        util.log("Output wire     :" + str(self.out_gate_id_))
        for idx, g in self.gates_.items():
            g.print_out()

    def __test__(self):
        # print(str(crypto.key_pair()[0].hex()))
        #
        # util.log(self.name_)
        # for idx, g in self.gates_.items():
        #     g.print_out()
        for idx in self.alice_:
            alice_val = 1
            wire = self.get_wire_by_id(idx)
            key = wire.key_pair_[alice_val]
            val = alice_val ^ wire.p_bit_
            ALICE_INPUT_KEYS[idx] = (key, val)
        for idx in self.bob_:
            bob_val = 1
            wire = self.get_wire_by_id(idx)
            key = wire.key_pair_[bob_val]
            val = bob_val ^ wire.p_bit_
            BOB_INPUT_KEYS[idx] = (key, val)
        pass


class BobCircuits(Circuits):
    """
    Attributes
        p_bit_json_:    json file for p bit
        gt_list_json_:  json file for list of garble table
        p_bit_:         dict {output wire: p bit value}
        input_p_bit_:   dict {bob's input wire: p bit value}
        gt_list_:       list []
        wires_:         dict {wire_id: BobWire}
    """
    def __init__(self, json_circuits):

        name = json_circuits["circuit"]
        a = get_attribute(json_circuits, "alice", [])
        b = get_attribute(json_circuits, "bob", [])
        out = json_circuits["out_wire"]
        Circuits.__init__(self, name, a, b, out)
        # retrieve p bit
        self.p_bit_json_ = json_circuits["p_bit"]
        self.p_bit_ = {}
        self.__get_p_bit_from_json__()
        self.input_p_bit_json_ = json_circuits["bob_p_bit"]
        self.input_p_bit_ = {}
        self.__get_input_p_bit_from_json__()
        # retrieve garble tables
        self.gt_list_json_ = json_circuits["gt_list"]
        self.gt_list_ = []
        self.__get_garble_circuit__()
        # set wires
        self.wires_ = {}
        # self.fire_circuit(ALICE_INPUT_KEYS, BOB_INPUT_KEYS)

    def __get_p_bit_from_json__(self):
        """
        retrieve p bit from json
        store in self.p_bit_, as {wire_id: p_bit_value}
        """
        for rec in self.p_bit_json_:
            self.p_bit_[rec['wire']] = rec['p_bit']
        # util.log(str(self.p_bit_))

    def __get_input_p_bit_from_json__(self):
        """
        retrieve p bit from json
        store in self.p_bit_, as {wire_id: p_bit_value}
        """
        for rec in self.input_p_bit_json_:
            self.input_p_bit_[rec['wire']] = rec['p_bit']

    def __get_garble_circuit__(self):
        for rec in self.gt_list_json_:
            self.gt_list_.append(GarbleTable(rec))

    def fire_circuit(self, alice_keys, bob_keys_):
        """

        :param alice_keys:  dict, {wire_id: (key, value)}
        :param bob_keys_:   dict, {wire_id: (key, value)}
        :return:            list, [out_put]
        """
        output = []
        for wire_id, key_val in alice_keys.items():
            self.wires_[wire_id] = BobWire(wire_id, key_val)
        for wire_id, key_val in bob_keys_.items():
            self.wires_[wire_id] = BobWire(wire_id, key_val)
        for gt in self.gt_list_:
            in_wire0 = self.wires_[gt.input_wire_[0]]
            try:
                in_wire1 = self.wires_[gt.input_wire_[1]]
            except IndexError:
                in_wire1 = None

            if in_wire1 is None:
                cipher = gt.garble_table_[(in_wire0.value_, 0)]
            else:
                if DEBUG:
                    util.log(str((in_wire0.value_, in_wire1.value_)))
                    util.log(gt.garble_table_)
                cipher = gt.garble_table_[(in_wire0.value_, in_wire1.value_)]
            if DEBUG:
                util.log("decrypting....")
                util.log(cipher)
                util.log(in_wire0.key_)
                util.log(in_wire1.key_)
            if in_wire1 is None:
                decrypt_ = crypto.decrypt(cipher_txt=cipher, key0=in_wire0.key_, key1=None)
            else:
                decrypt_ = crypto.decrypt(cipher_txt=cipher, key0=in_wire0.key_, key1=in_wire1.key_)
            key = decrypt_[0:-1]
            val = decrypt_[-1]
            if DEBUG:
                util.log("decrypt all:")
                util.log(decrypt_)
                util.log("retrieve out_val:   type:" + str(type(val)) + "val:" + str(val))
                util.log("retrieve key:")
                util.log(key)
                util.log(" ")
            self.wires_[gt.gate_id_] = BobWire(gt.gate_id_, (key, val))

        for out in self.out_gate_id_:
            output.append(self.wires_[out].value_ ^ self.p_bit_[out])
        if DEBUG:
            util.log(output)
        return output


class Gate:
    """
    Attributes:
        circuit_:       Circuit that the gate belongs to
        gate_id_:       int
        type_:          string, type of the gate
        inputs_:        list of input wire id
        input_wires_:   dictionary of Wire, {0: wire0, 1: wire1}
        output_:        output value according to the input_wires_[i].value_ i = 0, 1
        output_wire_:   Wire
        garble_table_:  dictionary of tuple, {(0, 1):encrypt_(key, 0)} if 0 $type 0 = 0
    """
    def __init__(self, circuit, gate_id, gate_type, inputs):
        """

        :param circuit: Circuit that the gate belongs to
        :param gate_id: int
        :param gate_type:   string
        :param inputs:  list of input gate id
        """
        self.circuit_ = circuit
        self.type_ = gate_type
        self.gate_id_ = gate_id
        self.inputs_ = inputs
        self.garble_table_ = {}
        self.input_wires_ = {}
        for i, idx in enumerate(self.inputs_):
            self.input_wires_[i] = self.circuit_.get_wire_by_id(idx)
            # util.log("input:  " + str(i) + "  :  " + str(self.input_wires_[i].wire_id_)
            #          + ":" + str(self.input_wires_[i].key_pair_))

        self.output_wire_ = AliceWire(gate_id, crypto.key_pair())
        # util.log(str(crypto.find_key_pair_index(self.output_wire_.key_pair_,
        #                                         self.output_wire_.key_pair_[1])))
        self.output_ = None

    @staticmethod
    def __truth_table__(n):
        """
        :param n: dimension of the truth table
        :return:  list of tuple
        """
        return list(itertools.product([0, 1], repeat=n))

    def make_garble_table(self):
        """
        Ek[2, x], k[4, y](k[6, z], t) where x = 0⊕p[2], y = 0⊕p[4], z = XOR(x, y), t = z⊕p[6]
        x -> entry[0]
        y -> entry[1]
        z -> out_val
        t = z ^ p_bit
        :return:
        """
        # table -> list of (key, index)
        table = []
        # generate truth table
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
            # encrypt keys according to the entry of truth table via  crypto.py
            plain_txt = self.output_wire_.key_pair_[out_val]
            # util.log(plain_txt)
            plain_txt += bytes([out_val ^ self.output_wire_.p_bit_])
            # util.log(plain_txt)
            try:
                encrypt_ = crypto.encrypt(plain_txt=plain_txt,
                                          key0=self.input_wires_[0].key_pair_[wire0_idx],
                                          key1=self.input_wires_[1].key_pair_[wire1_idx])
                if DEBUG:
                    util.log(encrypt_)
                # test crypto function
                # util.log("decrypting....")
                # decrypt_ = crypto.decrypt(cipher_txt=encrypt_,
                #                           key0=self.input_wires_[0].key_pair_[wire0_idx],
                #                           key1=self.input_wires_[1].key_pair_[wire1_idx])
                # decrypt_key = decrypt_[0:-1]
                # util.log("decrypt all:")
                # util.log(decrypt_)
                # util.log("retrieve out_val:   type:" + str(type(decrypt_[-1])) + "val:" + str(decrypt_[-1]))
                # util.log("retrieve key:")
                # util.log(decrypt_key)
                # util.log(" ")
                # if decrypt_ == self.output_wire_.key_pair_[out_val]:
                #     util.log("successful decrypt!")
                # else:
                #     util.log("decrypt error!")
            except KeyError:
                encrypt_ = crypto.encrypt(plain_txt=plain_txt,
                                          key0=self.input_wires_[0].key_pair_[wire0_idx],
                                          key1=None)
            table.append(encrypt_)
        # shuffle the output value of garble table by p bit
        if self.type_ == "NOT":
            if self.input_wires_[0].p_bit_ == 1:
                table[0], table[1] = table[1], table[0]
        else:
            if self.input_wires_[0].p_bit_ == 1:
                table[0], table[2] = table[2], table[0]
                table[1], table[3] = table[3], table[1]
            if self.input_wires_[1].p_bit_ == 1:
                table[0], table[1] = table[1], table[0]
                table[2], table[3] = table[3], table[2]

        # collect garble table
        for i, entry in enumerate(truth_table):
            self.garble_table_[entry] = table[i]

    def print_garble_table(self, verbose=1):
        util.log("gate id   :" + str(self.gate_id_) + "     gate type   :" + str(self.type_))
        if verbose == 2:
            for key, val in self.garble_table_.items():
                util.log("      " + str(key) + "  -> input key 0: " + str(self.input_wires_[0].key_pair_[key[0]]))
                try:
                    util.log("              -> input key 1: " + str(self.input_wires_[1].key_pair_[key[1]]))
                except KeyError:
                    pass
                util.log("              ->  output: " + str(val))
        elif verbose == 1:
            for key, val in self.garble_table_.items():
                util.log("      " + str(key) + "   ->   " + str(val))
        elif verbose == 0:
            for key, val in self.garble_table_.items():
                util.log("      " + str(key) + "   ->   " + str(val[1]))

    def convert_gt_to_json(self):
        j = {"gate_id"      : self.gate_id_,
             "input_wire"   : self.inputs_,
             "garble_table" : []}
        for entry, val in self.garble_table_.items():
            entry_json = {"input_value": entry,
                          "encryption" : val.decode('utf8')}
            j["garble_table"].append(entry_json)
        return j

    def reset(self):
        self.output_ = None

    def print_out(self):
        util.log(self.circuit_.name_ + ": ")
        util.log("type     :" + str(self.type_))
        util.log("gate id  :" + str(self.gate_id_))
        util.log("inputs   :" + str(self.inputs_))
        util.log("outputs  :" + str(self.output_))


class GarbleTable:
    """
    Attributes
        input_wire_:        list
        gate_id_:           int
        garble_table_:      dict {(in_val0, in_val1): encryption} or {(in_val0, 0): encryption}#NOT#
    """
    def __init__(self, gt_json):
        self.input_wire_ = gt_json["input_wire"]
        self.gate_id_ = gt_json["gate_id"]
        self.garble_table_ = {}
        self.__build_garble_table__(gt_json["garble_table"])
        # self.print_out()
        pass

    def __build_garble_table__(self, gt):
        for rec in gt:
            try:
                input_value = (rec["input_value"][0], rec["input_value"][1])
            except IndexError:
                input_value = (rec["input_value"][0], 0)
            # encryption = base64.b64encode(rec["encryption"].encode('utf-8'))
            encryption = rec["encryption"].encode('utf-8')
            # util.log(str(input_value))
            # util.log(encryption)
            self.garble_table_[input_value] = encryption

    def print_out(self):
        util.log("input wires:   " + str(self.input_wire_))
        util.log("output wire:   " + str(self.gate_id_))
        util.log("garble_table:  " + str(self.garble_table_))


class Wire:
    """
    Attribute:
        wire_id_:       int, index of the wire
    """
    def __init__(self, idx):
        self.wire_id_ = idx


class AliceWire(Wire):
    """
    Attribute:
        key_pair_:      dictionary {truth value : key}
        p_bit_:         int, p bit 0 or 1
    """
    def __init__(self, idx, key_pair):
        """

        :param idx:         int, wire index
        :param key_pair:    {0:key0, 1:key1}
        """
        # valid_p_bit = [0, 1]
        Wire.__init__(self, idx)
        self.key_pair_ = key_pair
        self.p_bit_ = None
        self.set_p_bit()
        if DEBUG:
            self.print_out(1)

    def set_p_bit(self, val=None):
        valid_val_list = [0, 1]
        if val is None:
            self.p_bit_ = crypto.random_1_bit()
        elif val in valid_val_list:
            util.log("warning: p_bit already set, wire id - " + str(self.wire_id_))
            self.p_bit_ = val
        else:
            raise ValueError("invalid p bit value")
        # self.__update_key_by_p_bit__()

    def __update_key_by_p_bit__(self):
        if self.p_bit_ == 1:
            # util.log("original key pair")
            # for rec in self.key_pair_:
            #     util.log(str(rec))
            self.key_pair_[0], self.key_pair_[1] = self.key_pair_[1], self.key_pair_[0]
            # util.log("original key pair")
            # for rec in self.key_pair_:
            #     util.log(str(rec))

    def print_out(self, verbose=0):
        util.log("wire id: " + str(self.wire_id_))
        if verbose == 1:
            util.log("        key pair: " + str(self.key_pair_))
            util.log("        p bit:    " + str(self.p_bit_))


class BobWire(Wire):
    """
    Attribute:
        key_:   bytes, key
        value_: int 0 or 1
    """
    def __init__(self, idx, key_val):
        Wire.__init__(self, idx)
        self.key_ = key_val[0]
        self.value_ = key_val[1]


# for json reading _________________________________________________
def get_attribute(data, attribute, default_value):
    return data.get(attribute) or default_value


def bytes_to_int(bytes_):
    result = 0
    for b in bytes_:
        result = result * 256 + int(b)
    return result
