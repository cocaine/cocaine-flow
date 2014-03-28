import json
import time

from Crypto.Cipher import AES
from Crypto import Random


key = b'Sixteen byte key'

TOKEN_LIFETIME = 3600


class Token(object):
    def dumps(self, data):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        msg = iv + cipher.encrypt(data)
        return msg.encode("hex")

    def loads(self, raw):
        data = raw.decode("hex")
        if len(data) < AES.block_size:
            raise ValueError("Too short to be decrypted, %d" % len(data))

        iv = data[:AES.block_size]
        value = data[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CFB, iv)
        return cipher.decrypt(value)

    def pack_user(self, user_info):
        return self.dumps(json.dumps(user_info))

    def unpack_user(self, packed_user_info):
        return json.loads(self.loads(packed_user_info))

    def is_valid(self, token):
        pass


if __name__ == "__main__":
    import sys
    incoming = sys.argv[1]
    t = Token()
    assert incoming == t.loads(t.dumps(incoming)), "Something wrong"
