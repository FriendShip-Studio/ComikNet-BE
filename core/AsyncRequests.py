from typing import List, Optional
import aiohttp

from fastapi.responses import Response


class AsyncRequests:
    """
    AsyncRequests Class
    ~~~~~~~~~~~~~~~~~~~~~
    AsyncRequests is a packaged web requests class which based on aiohttp.

    This class does not contain any request methods, it only provide some session control utilities.
    """

    def __init__(self, base_url: str, cookies: Optional[dict] = None, conn_timeout: int = 15, read_timeout: int = 45) -> None:
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            base_url=f"https://{base_url}",
            cookies=cookies,
            conn_timeout=conn_timeout,
            read_timeout=read_timeout,
            connector=aiohttp.TCPConnector(verify_ssl=False, force_close=True)
        )

    async def close(self) -> None:
        await self.session.close()

    def setCookies(self, res: Response, append_cookies: Optional[dict] = None, except_cookies: Optional[List[str]] = None) -> None:
        if append_cookies is not None:
            for cookie in append_cookies:
                res.set_cookie(key=cookie, value=append_cookies[cookie])

        if dict(
                self.session.cookie_jar._cookies[self.base_url]) != {}:  # type: ignore
            cookies_dict = dict(
                self.session.cookie_jar._cookies[self.base_url])  # type: ignore
        else:
            cookies_dict = dict(
                self.session.cookie_jar._cookies[(self.base_url, "/")])  # type: ignore
        for cookie in cookies_dict:
            if except_cookies is not None and cookie in except_cookies:
                continue
            res.set_cookie(key=cookie, value=cookies_dict[cookie].value,
                           expires=cookies_dict[cookie]["expires"],
                           path=cookies_dict[cookie]["path"])

    def getCookies(self) -> dict:
        cookies_dict = dict(
            self.session.cookie_jar._cookies[f"{self.base_url}"])  # type: ignore
        cookies = {}
        for cookie in cookies_dict:
            cookies[cookie] = cookies_dict[cookie].value
        return cookies
