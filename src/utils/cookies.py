from requests.utils import cookiejar_from_dict
from requests.cookies import RequestsCookieJar


def CookiesTranslate(avs: str, __cflb: str, ipcountry: str, ipm5: str) -> RequestsCookieJar:

    cookies_dict = {
        "AVS": avs,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5
    }

    return cookiejar_from_dict(cookies_dict)
