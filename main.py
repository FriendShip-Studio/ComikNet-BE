from fastapi import FastAPI, Cookie, Response, Header
import requests
from requests import utils
from bs4 import BeautifulSoup

# 类型库
from src.models.body import Login_Body, Cookies
from src.models.mirrors import JMTT_Mirror
from src.models.headers import Headers

app = FastAPI()

# 后续由前端指定后端通讯的镜像源
mirror = JMTT_Mirror.MainLand_Mirror_1


@app.post("/login")
async def login(body: Login_Body, response: Response, user_agent: str = Header(default="")) -> dict:

    login_form = {
        "username": body.username,
        "password": body.password,
        "submit_login": ""
    }

    if(body.isRemember):
        login_form["login_remember"] = "on"

    req = requests.post(
        f"https://{mirror}/login", data=login_form,
        headers=Headers(
            mirror, user_agent, "login"
        ).headers,
        allow_redirects=False)

    cookies_dict = req.cookies.get_dict()

    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    return {
        "status_code": req.status_code,
        "username": body.username
    }


@app.get("/profile")
async def get_self_profile(AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                           ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies_dict = Cookies(AVS, __cflb, ipcountry, ipm5, remember).__dict__()

    req = requests.get(
        f"https://{mirror}/user", cookies=utils.cookiejar_from_dict(cookies_dict),
        headers=Headers(
            mirror).headers
    )

    document = BeautifulSoup(req.content, "lxml")

    elem = document.find(
        name="img", class_="header-personal-avatar")

    if(elem):
        user_avatar = "https://"+mirror+elem.attrs["src"]
        return{
            "status_code": req.status_code,
            "data": {
                "user_avatar": user_avatar
            }
        }
    else:
        return{
            "status_code": req.status_code,
            "msg": "用户未登录"
        }
