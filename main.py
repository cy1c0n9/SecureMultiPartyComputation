
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018

import json	    # load
import sys	    # argv

import ot	    # alice, bob
import util	    # ClientSocket, log, ServerSocket
import yao	    # Circuit


# Alice is the circuit generator (client) __________________________________

def alice(filename):
    socket = util.ClientSocket()

    with open(filename) as json_file:
        json_circuits = json.load(json_file)

    for json_circuit in json_circuits['circuits']:
        pass
        # << removed >>


# Bob is the circuit evaluator (server) ____________________________________

def bob():
    socket = util.ServerSocket()
    util.log(f'Bob: Listening ...')
    while True:
        pass
        # << removed >>


# local test of circuit generation and evaluation, no transfers_____________

def local_test(filename):
    with open(filename) as json_file:
        json_circuits = json.load(json_file)

    for json_circuit in json_circuits['circuits']:
        # print(json_circuit["name"])
        name = json_circuit["name"]
        a = yao.get_attribute(json_circuit, "alice", [])
        b = yao.get_attribute(json_circuit, "bob", [])
        out = json_circuit["out"]
        cir = yao.Alice(name, a, b, out, json_circuit["gates"])
        # cir.print_out()
        # print(json_circuit["gates"])
        pass
    # yao.Bob("json_out/circuit from Smart, figure 2.2, page 443.json")
    yao.Bob("json_out/AND gate.json")
        # << removed >>

# main _____________________________________________________________________


def main():
    behaviour = sys.argv[1]
    if behaviour == 'alice':
        alice(filename=sys.argv[2])
    elif behaviour == 'bob':
        bob()
    elif behaviour == 'local':
        local_test(filename=sys.argv[2])


if __name__ == '__main__':
    main()

# __________________________________________________________________________


