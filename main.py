from fastapi import FastAPI, Cookie, Response, Header
from fastapi.responses import StreamingResponse
import requests
from requests import utils
from bs4 import BeautifulSoup
import time

# 类型库
from src.models.body import Login_Body, Cookies, Reg_Body
from src.models.headers import Headers
from src.config.mirror import mirror, JMTT_Mirror

app = FastAPI()


@app.get("/mirror-status")
async def ping_mirror():
    server_result = {}
    for server in JMTT_Mirror:

        try:
            start_time = time.perf_counter()
            req = requests.get(f"https://{server.value}/",
                               timeout=10000, allow_redirects=False)

            if(req.status_code == 301):
                server_result[server.value] = f"Connection Redirected! Target: {req._next.url}"
                continue
            used_time = time.perf_counter()-start_time

            server_result[server.value] = used_time

        except Exception as e:
            server_result[server.value] = "Connection Dead!"

    return {
        "data": server_result
    }


@app.get("/captcha")
async def captcha(response: Response, user_agent: str = Header(default="")):

    req = requests.get(f"https://{mirror}/signup", headers=Headers(
        mirror, user_agent
    ).headers)

    signup_cookies = req.cookies
    cookies_dict = signup_cookies.get_dict()

    req = requests.get(f"https://{mirror}/captcha", headers=Headers(
        mirror, user_agent
    ).headers, cookies=signup_cookies)

    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    return StreamingResponse(req.iter_content(), media_type="image/jpeg", headers=response.headers)


@app.post("/register")
async def reg(body: Reg_Body, user_agent: str = Header(default=""), AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
              ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default="")):

    cookies_dict = Cookies(AVS, __cflb, ipcountry, ipm5).__dict__()

    reg_form = {
        "username": body.username,
        "password": body.password,
        "password_confirm": body.password,
        "email": body.email,
        "verification": body.captcha,
        "gender": body.gender,
        "age": "on",
        "terms": "on",
        "submit_signup": ""
    }

    req = requests.post(f"https://{mirror}/signup", data=reg_form, headers=Headers(
        mirror, user_agent, "signup"
    ).headers_post, allow_redirects=False, cookies=utils.cookiejar_from_dict(cookies_dict))

    # 即将改动
    return{
        "data": req.text
    }


@app.post("/login")
async def login(body: Login_Body, response: Response, user_agent: str = Header(default="")):

    login_form = {
        "username": body.username,
        "password": body.password,
        "submit_login": ""
    }

    if(body.isRemember):
        login_form["login_remember"] = "on"

    req = requests.post(
        f"https://{mirror}/login", data=login_form, headers=Headers(
            mirror, user_agent, "login"
        ).headers_post,
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
        headers=Headers(mirror).headers
    )

    document = BeautifulSoup(req.content, "lxml")

    elem = document.find(
        name="img", class_="header-personal-avatar")

    if(elem):
        user_avatar = "https://"+mirror+elem.attrs["src"]
        elem = document.find_all(name="div", class_="header-info-profile")
        user_history = dict()
        for e in elem:
            if e.text.strip().startswith("戰鬥力"):
                history_lst: list = e.text.strip().replace(
                    "\n\n\n", "\n").split("\n")[2:]
                for i in range(0, len(history_lst), 2):
                    user_history[history_lst[i+1]] = history_lst[i]

        return{
            "status_code": req.status_code,
            "data": {
                "user_avatar": user_avatar,
                "user_history": user_history
            }
        }
    else:
        return{
            "status_code": req.status_code,
            "msg": "用户未登录"
        }


@app.get("/favourite")
async def get_self_fav(username: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                       ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies_dict = Cookies(AVS, __cflb, ipcountry, ipm5, remember).__dict__()

    req = requests.get(
        f"https://{mirror}/user/{username}/favorite/albums?page={page}", cookies=utils.cookiejar_from_dict(cookies_dict),
        headers=Headers(mirror).headers
    )

    document = BeautifulSoup(req.content, "lxml")

    elem = document.find(
        name="div", class_="col-md-6").find(name="div", class_="row")

    if(elem):
        fav_comic = int(document.find(
            "div", class_="pull-left m-l-20").text.strip()[5:].removesuffix("/ 400"))

        comic_list = document.find_all(
            name="div", class_="col-xs-6 col-sm-3 col-md-3 m-b-15 list-col")
        comic_list = [{
            "serial": "JM"+comic.find(name="a").attrs["href"].removeprefix("/album/").removesuffix("/"),
            "cover": f"https://{mirror}"+comic.find(name="a").find("div", class_="thumb-overlay").find("img").attrs["src"].removesuffix("?v="),
            "title": comic.find(name="a").find("div", class_="video-title title-truncate").text.strip()
        } for comic in comic_list]

        if(fav_comic/20 <= 1):
            return{
                "status_code": req.status_code,
                "data": comic_list
            }
        else:
            return{
                "status_code": req.status_code,
                "data": comic_list,
                "page": page
            }
    else:
        return{
            "status_code": req.status_code,
            "msg": "用户未登录"
        }


@app.get("/search")
async def search(query: str, main_tag: int = 0, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies_dict = Cookies(AVS, __cflb, ipcountry, ipm5, remember).__dict__()

    req = requests.get(f"https://{mirror}/search/photos", params={
        "main_tag": main_tag,
        "search_query": query,
        "page": page
    }, cookies=utils.cookiejar_from_dict(cookies_dict))

    document = BeautifulSoup(req.content, "lxml")

    elem = document.find_all("div", class_="p-b-15")

    comic_list = []

    for comic in elem:
        comic_list.append({
            "title": comic.find("span", class_="video-title title-truncate m-t-5").text.strip(),
            "author": [author.text.strip() for author in comic.find("div", class_="title-truncate").find_all("a")],
            "serial": "JM"+comic.find("a").attrs["href"].removeprefix("/album/")[:6],
            "cover": comic.find("img", class_="lazy_img img-responsive img-rounded").attrs["data-original"],
            "tags": [tag.text.strip() for tag in comic.find("div", class_="title-truncate tags p-b-5").find_all("a", class_="tag")]
        })

    if(document.find("ul", class_="pagination")):
        return{
            "status_code": req.status_code,
            "data": comic_list,
            "page": page
        }
    else:
        return {
            "status_code": req.status_code,
            "data": comic_list
        }
