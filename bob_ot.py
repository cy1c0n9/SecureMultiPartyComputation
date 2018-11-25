import zmq
import random
import sys
import time
import ot
import numpy


def bob(b, socket):
    """

    :param b:       int 0 or 1, bob's choice
    :param socket:  socket, connected socket
    :return:
    """
    bob_ = ot.Bob(b)

    c = socket.recv()
    c = int(c)
    # print("received c:"+str(c))
    h0 = bob_.bob_setup(c)
    # print("send h0:"+str(h0))
    socket.send_string(str(h0))
    # print("have sent h0"+str(h0))

    c1 = socket.recv()
    c1 = int(c1)
    # print("c1:"+str(c1))
    e0 = socket.recv()
    # print("receive e0:"+str(e0))
    e1 = socket.recv()
    # print("receive e1:" + str(e1))
    mb = bob_.bob_decode(c1, e0, e1)
    return mb


# b = 0
# print(bob(b))
