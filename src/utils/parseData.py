import hashlib
from Cryptodome.Cipher import AES
import base64
import json


def ParseData(time: int, data: str) -> dict:
    param = f"{time}18comicAPPContent"
    key = hashlib.md5(param.encode("utf-8")).hexdigest()
    aes = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    byteData = base64.b64decode(data.encode("utf-8"))
    result = aes.decrypt(byteData)

    result2 = result[0:-result[-1]]
    newData = result2.decode()
    return json.loads(newData)
