from fastapi import FastAPI, Response, Cookie
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import time

from src.models.headers import GetHeaders
from src.models.body import LoginBody, SignupBody
from src.models.sort import sortBy
from src.utils.cookies import CookiesTranslate
from src.utils.parseData import ParseData

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mirror = "www.asjmapihost.cc"

web_url = "jmcomic2.onl"

img_mirror = "cdn-msp.jmapiproxy2.cc"


@app.get("/captcha")
async def get_captcha(response: Response):

    req = requests.get(f"https://{web_url}/login", verify=False)

    cookies = req.cookies
    cookies_dict = cookies.get_dict()

    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    req = requests.get(f"https://{web_url}/captcha",
                       cookies=cookies, verify=False)

    return StreamingResponse(req.iter_content(), media_type="image/jpeg", headers=response.headers)


@app.post("/register")
async def register(body: SignupBody, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                   ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "username": body.username,
        "password": body.password,
        "password_confirm": body.password,
        "email": body.email,
        "verification": body.captcha,
        "gender": body.sex,
        "age": "on",
        "terms": "on",
        "submit_signup": ""
    }

    req = requests.post(f"https://{web_url}/signup", data=req_body, headers=GetHeaders(
        req_time, "POST").headers, cookies=cookies, verify=False)

    msg_list = []
    document = BeautifulSoup(req.content, "lxml")
    for script in document.find_all("script"):
        if(script.text.startswith("toastr['error']")):
            msg_list.append({
                "type": "error",
                "msg": script.text.removeprefix("toastr['error']")[2:-2]
            })
        elif(script.text.startswith("toastr")):
            msg_list.append({
                "type": "default",
                "msg": script.text.removeprefix("toastr['success']")[2:-2]
            })

    return {
        "status_code": req.status_code,
        "data": msg_list
    }


@app.post("/login")
async def login(body: LoginBody, response: Response):

    req_time = int(time.time())

    login_form = {
        "username": body.username,
        "password": body.password,
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": None
    }

    req = requests.post(f"https://{mirror}/login", headers=GetHeaders(
        req_time, "POST").headers, data=login_form, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/logout")
async def logout(response: Response, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req = requests.get(f"https://{mirror}/logout",
                       cookies=cookies, verify=False)

    return {
        "status_code": req.status_code
    }


@app.get("/favorite")
async def get_fav(response: Response, page: int = 1, sort=sortBy.Time.value, fid: str = "0", AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                  ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    if(sort not in [sortBy.Time.value, sortBy.Images.value]):
        # 此处按图片排序代指按更新时间排序
        sort = sortBy.Time.value

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": None,
        "page": page,
        "folder_id": fid,
        "o": sort
    }

    req = requests.get(f"https://{mirror}/favorite/", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, verify=False, cookies=cookies)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
            "errorMsg": req.json()["errorMsg"]
        }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/search")
async def search(query: str, response: Response, page: int = 1, sort=sortBy.Time.value, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "search_query": query,
        "page": page,
        "o": sort
    }

    req = requests.get(f"https://{mirror}/search", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, verify=False, cookies=cookies)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/history")
async def get_history(page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                      ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "page": page
    }

    req = requests.get(f"https://{mirror}/watch_list", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/album")
async def get_album_info(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                         ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "id": id
    }

    req = requests.get(f"https://{mirror}/album", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/chapter")
async def get_chapter_info(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                           ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "skip": "",
        "id": id
    }

    req = requests.get(f"https://{mirror}/chapter", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/img_list")
async def get_img_list(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                       ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "id": id,
        "mode": "vertical",
        "page": 0,
        "app_img_shunt": "NaN"
    }

    req = requests.get(f"https://{mirror}/chapter_view_template", params=req_body, headers=GetHeaders(
        req_time, "GET", True).headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    document = BeautifulSoup(req.content, "lxml")

    img_list = []

    for container in document.find_all("div", class_="center scramble-page"):
        img_list.append(container.attrs["id"])

    return {
        "status_code": req.status_code,
        "data": img_list
    }


@app.get("/comment/comic")
async def get_comment(id: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                      ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "mode": "manhua",
        "aid": id,
        "page": page
    }

    req = requests.get(f"https://{mirror}/forum", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/comment/user")
async def get_self_comment(uid: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""), ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "mode": "undefined",
        "uid": uid,
        "page": page
    }

    req = requests.get(f"https://{mirror}/forum", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.post("/comment")
async def send_comment(id: str, content: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""), ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comment": content,
        "aid": id
    }

    req = requests.post(f"https://{mirror}/comment", data=req_body, headers=GetHeaders(
        req_time, "POST").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }


@app.get("/tags")
async def get_tags(AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""), ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5, remember)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null"
    }

    req = requests.get(f"https://{mirror}/categories", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        return {
            "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
        }

    return {
        "status_code": req.status_code,
        "data": ParseData(req_time, req.json()["data"])
    }
