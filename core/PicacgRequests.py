from hashlib import sha256
from fastapi.exceptions import HTTPException

import hmac
import json
import time
import uuid

from typing import Optional
from core.AsyncRequests import AsyncRequests
from models.requests import StandardResponse
from models.error_code import PicaError


class PicaToolUtils:

    @ staticmethod
    def ConFromNative(datas):
        # 以下是IDA PRO反编译的混淆代码
        key = ""

        # v6 = datas[0]
        v37 = str(datas[1])
        v7 = str(datas[2])
        v35 = str(datas[3])
        v36 = str(datas[4])
        v8 = str(datas[5])
        # v9 = datas[6]
        # v10 = datas[7]
        # v33 = v9
        # v34 = v6

        key += v37
        key += v7
        key += v35
        key += v36
        key += v8
        return key

    @ staticmethod
    def SigFromNative():
        return '~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn'

    @ staticmethod
    def HashKey(src, key):
        appsecret = key.encode('utf-8')  # 秘钥
        data = src.lower().encode('utf-8')  # 数据
        signature = hmac.new(appsecret, data, digestmod=sha256).hexdigest()
        return signature

    @staticmethod
    def ParamsCombine(params: Optional[dict]) -> str:
        if params is None:
            return ""
        else:
            return "?" + "&".join([f"{key}={value}" for key, value in params.items()])


class PicacgRequests(AsyncRequests):

    def __init__(self, token: Optional[str] = None, cookies: Optional[dict] = None, base_url: Optional[str] = None,
                 conn_timeout: int = 15, read_timeout: int = 45) -> None:
        self.token = token
        super().__init__("picaapi.picacomic.com" if base_url is None else base_url,
                         cookies, conn_timeout, read_timeout)

    def getHeaders(self, url: str, method: str) -> dict:

        req_time = str(int(time.time()))
        nonce = str(uuid.uuid1()).replace("-", "")
        datas = [
            f"https://{self.base_url}/",
            url[1:],
            req_time,
            nonce,
            method,
            "C69BAF41DA5ABD1FFEDC6D2FEA56B",  # ApiKey
            "2.2.1.3.3.4",  # Version
            "45"  # BuildVersion
        ]

        src = PicaToolUtils.ConFromNative(datas)
        sigKey = PicaToolUtils.SigFromNative()
        sign = PicaToolUtils.HashKey(src, sigKey)

        headers = {
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate, br",
            "api-key": datas[5],
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "3",
            "time": req_time,
            "nonce": nonce,
            "app-uuid": "defaultUuid",
            "signature": sign,
            "app-version": datas[6],
            "app-build-version": datas[7],
            "app-platform": "android",
            "user-agent": "okhttp/3.8.1",
            "version": "v1.4.1",
            "image-quality": "original",
        }

        if self.token is not None:
            headers["Authorization"] = self.token

        if (method == "POST" or method == "PUT"):
            headers["Content-Type"] = "application/json; charset=UTF-8"

        return headers

    async def post(self, url: str, data: dict, params: Optional[dict] = None) -> StandardResponse:

        try:
            async with self.session.post(url, headers=self.getHeaders(url + PicaToolUtils.ParamsCombine(params), "POST"), data=json.dumps(data), params=params) as response:
                try:
                    res = await response.json()
                except json.JSONDecodeError:
                    raise HTTPException(
                        502, "Upstream server responded incorrectly")
        except Exception as e:
            raise HTTPException(500, e.__str__())

        if res["code"] != 200:
            return StandardResponse(status_code=response.status, error_msg=res["error"])
        else:
            return StandardResponse(status_code=response.status, data=res["data"])

    async def get(self, url: str, params: Optional[dict] = None) -> StandardResponse:

        try:
            async with self.session.get(url, headers=self.getHeaders(
                    url + PicaToolUtils.ParamsCombine(params), "GET"), params=params) as response:
                try:
                    res = await response.json()
                except json.JSONDecodeError:
                    raise HTTPException(
                        502, "Upstream server responded incorrectly")
        except Exception as e:
            raise HTTPException(500, e)

        if res["code"] != 200:
            return StandardResponse(status_code=response.status, error_msg=res["error"])
        else:
            return StandardResponse(status_code=response.status, data=res["data"])
