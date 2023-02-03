import json
import aiohttp
from src.utils.parseData import ParseData
from fastapi.responses import Response


class AsyncRequests:

    def __init__(self, base_url: str, cookies: dict = None, conn_timeout: int = 15, read_timeout: int = 45):
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            base_url=f"https://{base_url}",
            cookies=cookies,
            conn_timeout=conn_timeout,
            read_timeout=read_timeout
        )

    async def close(self) -> None:
        await self.session.close()

    def setCookies(self, res: Response, append_cookies: dict = None) -> None:
        if append_cookies is not None:
            for cookie in append_cookies:
                res.set_cookie(key=cookie, value=append_cookies[cookie])

        cookies_dict = dict(
            self.session.cookie_jar._cookies[f"{self.base_url}"])
        for cookie in cookies_dict:
            res.set_cookie(key=cookie, value=cookies_dict[cookie].value,
                           expires=cookies_dict[cookie]["expires"],
                           path=cookies_dict[cookie]["path"], secure=cookies_dict[cookie]["secure"],
                           httponly=cookies_dict[cookie]["httponly"],
                           samesite="none" if(cookies_dict[cookie]["samesite"] == "") else cookies_dict[cookie]["samesite"])

    def getCookies(self) -> dict:
        cookies_dict = dict(
            self.session.cookie_jar._cookies[f"{self.base_url}"])
        cookies = {}
        for cookie in cookies_dict:
            cookies[cookie] = cookies_dict[cookie].value
        return cookies

    async def get(self, url: str, req_time: int, headers: dict = None, params: dict = None) -> dict:

        async with self.session.get(url, headers=headers, params=params) as response:
            try:
                res = json.loads((await response.content.read()))
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试与源服务器通讯时出现错误!"
                }

            try:
                if(res["code"] == 200):
                    return {
                        "status_code": response.status,
                        "data": ParseData(req_time, res["data"])
                    }
                else:
                    return {
                        "status_code": response.status,
                        "errorMsg": res["errorMsg"]
                    }
            except:
                try:
                    return {
                        "status_code": response.status,
                        "errorMsg": res["errorMsg"]
                    }
                except:
                    return {
                        "status_code": response.status,
                        "errorMsg": "尝试解析源服务器数据时出现错误!"
                    }

    async def getContent(self, url: str, headers: dict = None, params: dict = None) -> dict:

        async with self.session.get(url, headers=headers, params=params) as response:
            try:
                res = await response.content.read()
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试与源服务器通讯时出现错误!"
                }

            try:
                return {
                    "status_code": response.status,
                    "data": res
                }
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试解析源服务器数据时出现错误!"
                }

    async def post(self, url: str, req_time: int, headers: dict = None, data: dict = None) -> dict:

        async with self.session.post(url, headers=headers, data=data) as response:
            try:
                res = json.loads((await response.content.read()))
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试与源服务器通讯时出现错误!"
                }

            try:
                if(res["status_code"] == 200):
                    return {
                        "status_code": response.status,
                        "data": ParseData(req_time, res["data"])
                    }
                else:
                    return {
                        "status_code": response.status,
                        "errorMsg": res["errorMsg"]
                    }
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试解析源服务器数据时出现错误!"
                }

    async def postContent(self, url: str, headers: dict = None, data: dict = None) -> dict:

        async with self.session.post(url, headers=headers, data=data) as response:
            try:
                res = await response.content.read()
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试与源服务器通讯时出现错误!"
                }

            try:
                if(response.status == 200):
                    return {
                        "status_code": response.status,
                        "data": res
                    }
                else:
                    return {
                        "status_code": response.status,
                        "errorMsg": json.loads(res)["errorMsg"]
                    }
            except:
                return {
                    "status_code": response.status,
                    "errorMsg": "尝试解析源服务器数据时出现错误!"
                }
