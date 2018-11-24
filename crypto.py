
# yao garbled circuit evaluation v1. simple version based on smart
# yicong chen, dept of computing, imperial college, november 2018
import util                                 # xor_bytes, bits
from cryptography.fernet import Fernet
from random import SystemRandom

ENCRYPTED = True
AES_BASED = True

if ENCRYPTED:   # ____________________________________________________________
    # secure AES based encryption

    def encrypt(plain_txt, key0, key1=None):
        """
        example0: encrypt(p, k0, k1)    returns Ek0(Ek1(p))
        example1: encrypt(p, k0)        returns Ek0(p)
        :param plain_txt:   bytes
        :param key0:        bytes
        :param key1:        bytes
        :return:
        """
        if key1 is None:
            if AES_BASED:
                return aes_encrypt(plain_txt, key0)
            else:
                return xor_encrypt(plain_txt, key0)
        else:
            if AES_BASED:
                return aes_encrypt(aes_encrypt(plain_txt, key1), key0)
            else:
                return xor_encrypt(xor_encrypt(plain_txt, key1), key0)


    def decrypt(cipher_txt, key0, key1=None):
        """
        example0: decrypt(c, k0, k1)    c = Ek0(Ek1(p)) return p
        example1: decrypt(c, k0)        c = Ek0(p) return p
        :param cipher_txt:  bytes
        :param key0:        bytes
        :param key1:        bytes
        :return:
        """
        if key1 is None:
            if AES_BASED:
                return aes_decrypt(cipher_txt, key0)
            else:
                return xor_decrypt(cipher_txt, key0)
        else:
            if AES_BASED:
                return aes_decrypt(aes_decrypt(cipher_txt, key0), key1)
            else:
                return xor_decrypt(xor_decrypt(cipher_txt, key0), key1)


    def aes_encrypt(plain_txt, key):
        f = Fernet(key)
        token = f.encrypt(plain_txt)
        return token

    def aes_decrypt(cipher_txt, key):
        f = Fernet(key)
        util.log(cipher_txt)
        util.log(key)
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

    # generate key pair
    def key_pair():
        return {0: Fernet.generate_key(),
                1: Fernet.generate_key()}

else:   # ____________________________________________________________________
    # totally insecure key-less implementation

    def encrypt(plain_txt, key=0):
        return plain_txt

    def decrypt(cipher_txt, key=0):
        return cipher_txt

    # generate key pair
    def key_pair():
        return {0: Fernet.generate_key(),
                1: Fernet.generate_key()}

# ____________________________________________________________________________


# utilities __________________________________________________________________
# shuffle the list
# example: shuffle(l) the list is shuffled after execution
def shuffle(l):
    for i in range(len(l)-1, 0, -1):
        j = SystemRandom().randrange(i+1)
        l[i], l[j] = l[j], l[i]


# generate random 1 bit, return a int 0 or int 1
def random_1_bit():
    return SystemRandom().randrange(2)


def find_key_pair_index(pair, search_key):
    return [idx for idx, key_val in pair.items() if key_val == search_key][0]
