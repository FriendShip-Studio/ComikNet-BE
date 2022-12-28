import typing


class Headers():

    headers = {
        "Cache-Control": "max-age=0",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    def __init__(self, host: str, ua: str = "", ref: str = "") -> None:

        self.headers["Host"] = host
        self.headers["Origin"] = f"https://{host}"
        self.headers["Referer"] = f"https://{host}/{ref}"
        self.headers["User-Agent"] = ua

    @property
    def headers_post(self):
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"

        return self.headers
