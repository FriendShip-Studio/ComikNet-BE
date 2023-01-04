import hashlib


class GetHeaders():

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
