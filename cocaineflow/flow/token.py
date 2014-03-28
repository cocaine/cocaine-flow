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
        # set timestamp
        user_info['time'] = int(time.time())
        return self.dumps(json.dumps(user_info))

    def unpack_user(self, token):
        return json.loads(self.loads(token))

    def is_valid(self, token):
        user_info = self.unpack_user(token)
        return int(time.time()) - user_info['time'] < TOKEN_LIFETIME


if __name__ == "__main__":
    import sys
    incoming = sys.argv[1]
    t = Token()
    assert incoming == t.loads(t.dumps(incoming)), "Something wrong"

    d = {"name": "user",
         "password": "pass"}

    token = t.pack_user(d)
    print token

    d['time'] = 100000
    token2 = t.dumps(json.dumps(d))
    print token2

    print t.is_valid(token)
    print t.is_valid(token2)
