

def CookiesTranslate(avs: str, __cflb: str, ipcountry: str, ipm5: str):

    cookies_dict = {
        "AVS": avs,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5
    }
    return SimpleCookie(cookies_dict)
