import zmq
import random
import sys
import time
import ot
import numpy
import util


def alice(m, socket):
    """

    :param m:       string alice's message(keys)
    :param socket:  socket, connected socket
    :return:
    """

    alice_ = ot.Alice(m)
    c = alice_.alice_sendc()
    socket.send_string(str(c))
    # time.sleep(1)

    h0 = socket.recv()
    h0 = int(h0)
    # time.sleep(1)
    c1, e0, e1 = alice_.alice_sende(h0)
    socket.send_string(str(c1))
    # time.sleep(1)
    socket.send(e0)
    # time.sleep(1)
    socket.send(e1)
    # time.sleep(1)


# M = ["message1", "message2"]
# alice(M)
