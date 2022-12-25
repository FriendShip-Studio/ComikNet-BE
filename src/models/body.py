from pydantic import BaseModel


class Login_Body(BaseModel):
    username: str
    password: str
    isRemember: bool = False


class Cookies():

    def __init__(self, avs: str, __cflb: str, ipcountry: str, ipm5: str, remember: str = ""):
        self.avs = avs
        self.__cflb = __cflb
        self.ipcountry = ipcountry
        self.ipm5 = ipm5
        self.remember = ""

    def __dict__(self) -> dict:

        cookies_dict = {
            "AVS": self.avs,
            "__cflb": self.__cflb,
            "ipcountry": self.ipcountry,
            "ipm5": self.ipm5
        }
        if(self.remember != ""):
            cookies_dict["remember"] = self.remember

        return cookies_dict
