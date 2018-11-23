
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018
import util                                 # xor_bytes, bits
from cryptography.fernet import Fernet
from random import SystemRandom

ENCRYPTED = True
AES_BASED = True

if ENCRYPTED:   # ____________________________________________________________
    # secure AES based encryption

    def encrypt(plain_txt, key):
        """

        :param plain_txt:   bytes
        :param key:         bytes
        :return:
        """
        if AES_BASED:
            return aes_encrypt(plain_txt, key)
        else:
            return xor_encrypt(plain_txt, key)

    def decrypt(cipher_txt, key):
        """

        :param cipher_txt:  bytes
        :param key:         bytes
        :return:
        """
        if AES_BASED:
            return aes_decrypt(cipher_txt, key)
        else:
            return xor_decrypt(cipher_txt, key)


    def aes_encrypt(plain_txt, key):
        f = Fernet(key)
        token = f.encrypt(plain_txt)
        return token

    def aes_decrypt(cipher_txt, key):
        f = Fernet(key)
        plain = f.decrypt(cipher_txt)
        return plain

    def xor_encrypt(plain_txt, key):
        """

        :param plain_txt:   bytes
        :param key:         bytes
        :return:
        """
        return b_xor(plain_txt, key)

    def xor_decrypt(cipher_txt, key):
        """

        :param cipher_txt:  bytes
        :param key:         bytes
        :return:
        """
        # return util.xor_bytes(cipher_txt, key)
        return b_xor(cipher_txt, key)

    def b_xor(b1, b2):
        """
        use xor for bytes
        :param b1: bytes
        :param b2: bytes
        :return: bytes b1 ^ b2
        """
        result = b""
        for b1, b2 in zip(b1, b2):
            result += bytes([b1 ^ b2])
        return result

else:   # ____________________________________________________________________
    # totally insecure key-less implementation

    def encrypt(plain_txt, key=0):
        return plain_txt

    def decrypt(cipher_txt, key=0):
        return cipher_txt

# ____________________________________________________________________________


# utilities __________________________________________________________________
# generate key pair
def key_pair():
    return {0: Fernet.generate_key(),
            1: Fernet.generate_key()}


# shuffle the list
# example: shuffle(l) the list is shuffled after execution
def shuffle(l):
    for i in range(len(l)-1, 0, -1):
        j = SystemRandom().randrange(i+1)
        l[i], l[j] = l[j], l[i]


# generate random 1 bit, return a int 0 or int 1
def random_1_bit():
    return SystemRandom().randrange(2)
