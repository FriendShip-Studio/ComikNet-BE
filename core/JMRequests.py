from typing import Optional
from Crypto.Cipher import AES
from fastapi import HTTPException

import time
import base64
import hashlib
import json

from core.AsyncRequests import AsyncRequests
from models.requests import StandardResponse


class JMToolUtils:

    @staticmethod
    def dataDecrypt(time: int, data: str) -> dict:
        param = f"{time}18comicAPPContent"
        key = hashlib.md5(param.encode("utf-8")).hexdigest()
        aes = AES.new(key.encode("utf-8"), AES.MODE_ECB)
        byteData = base64.b64decode(data.encode("utf-8"))
        result = aes.decrypt(byteData)

        result2 = result[0:-result[-1]]
        newData = result2.decode()
        return json.loads(newData)

    @staticmethod
    def AuthorStr2List(authorStr: str) -> list:
        return authorStr.split(" ")


class JMRequests(AsyncRequests):

    def __init__(self, base_url: str, cookies: Optional[dict] = None, conn_timeout: int = 15, read_timeout: int = 45) -> None:
        super().__init__(base_url, cookies, conn_timeout, read_timeout)

    async def get(self, url: str, params: Optional[dict] = None) -> StandardResponse:

        req_time = int(time.time())
        headers = JMHeaders(req_time, "GET").headers

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                try:
                    res = json.loads(await response.read())
                except json.JSONDecodeError:
                    raise HTTPException(
                        502, "Upstream server responded incorrectly")
        except Exception as e:
            raise HTTPException(500, e.__str__())

        try:
            if res["code"] == 200:
                return StandardResponse(status_code=response.status, data=JMToolUtils.dataDecrypt(req_time, res["data"]))
            else:
                return StandardResponse(status_code=response.status, error_msg=res["errorMsg"])
        except:
            raise HTTPException(
                502, "Unable to decode upstream server response")

    async def getContent(self, url: str, params: Optional[dict] = None) -> StandardResponse:

        req_time = int(time.time())
        headers = JMHeaders(req_time, "GET", True).headers

        try:
            async with self.session.post(url, headers=headers, params=params) as response:

                res = await response.read()

                if response.status == 200:
                    return StandardResponse(status_code=response.status, data=res)
                else:
                    raise HTTPException(
                        502, "Upstream server responded incorrectly")
        except:
            raise HTTPException(
                500, "Unable to get response from upstream server")

    async def post(self, url: str, data: Optional[dict] = None) -> StandardResponse:

        req_time = int(time.time())
        headers = JMHeaders(req_time, "POST").headers

        try:
            async with self.session.post(url, headers=headers, data=data) as response:
                try:
                    res = json.loads(await response.read())
                except json.JSONDecodeError:
                    raise HTTPException(
                        502, "Upstream server responded incorrectly")
        except Exception as e:
            raise HTTPException(500, e.__str__())

        try:
            if res["code"] == 200:
                return StandardResponse(status_code=response.status, data=JMToolUtils.dataDecrypt(req_time, res["data"]))
            else:
                return StandardResponse(status_code=response.status, error_msg=res["errorMsg"])
        except:
            raise HTTPException(
                502, "Unable to decode upstream server response")

    async def postContent(self, url: str, data: Optional[dict] = None) -> StandardResponse:

        req_time = int(time.time())
        headers = JMHeaders(req_time, "POST").headers

        try:
            async with self.session.post(url, headers=headers, data=data) as response:

                res = await response.read()

                if response.status == 200:
                    return StandardResponse(status_code=response.status, data=res)
                else:
                    raise HTTPException(
                        502, "Upstream server responded incorrectly")
        except:
            raise HTTPException(
                500, "Unable to get response from upstream server")


class JMHeaders():

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.12.1",
    }

    def __init__(self, time: int, method: str, isContent: bool = False) -> None:

        if(isContent):
            param = f"{time}18comicAPPContent"
        else:
            param = f"{time}18comicAPP"
        token = hashlib.md5(param.encode("utf-8")).hexdigest()

        self.headers["tokenparam"] = f"{time},1.4.7"
        self.headers["token"] = token

        if(method == "POST"):
            self.headers["Content-Type"] = "application/x-www-form-urlencoded"

        elif(method == "TEST"):
            self.headers['cache-control'] = 'no-cache'
            self.headers['expires'] = '0'
            self.headers['pragma'] = 'no-cache'
            self.headers["authorization"] = ""
