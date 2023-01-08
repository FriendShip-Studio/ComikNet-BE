from fastapi import FastAPI, Response, Cookie
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import time
import re
import io

from src.models.headers import GetHeaders
from src.models.bodys import LoginBody, SignupBody
from src.models.sort import sortBy
from src.models.mirrors import PicList, ApiList, WebList
from src.utils.cookies import CookiesTranslate
from src.utils.parseData import ParseData
from src.utils.parsePic import SegmentationPicture

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/captcha")
async def get_captcha(response: Response):

    global avail_url
    avail_url = "jmcomic2.onl"

    for url in WebList:
        try:
            req = requests.get(
                f"https://{url}/login", verify=False, timeout=15000)
        except:
            continue
        if(req.status_code == 200):
            avail_url = url
            break
    cookies = req.cookies
    cookies_dict = cookies.get_dict()

    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    req = requests.get(f"https://{url}/captcha",
                       cookies=cookies, verify=False)

    return StreamingResponse(req.iter_content(), media_type="image/jpeg", headers=response.headers)


@app.post("/register")
async def register(body: SignupBody, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                   ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default="")):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

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

    req = requests.post(f"https://{avail_url}/signup", data=req_body, headers=GetHeaders(
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

    try:
        return {
            "status_code": req.status_code,
            "data": msg_list
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.post("/login")
async def login(body: LoginBody, response: Response, api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    login_form = {
        "username": body.username,
        "password": body.password,
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": None
    }

    req = requests.post(f"https://{api_mirror}/login", headers=GetHeaders(
        req_time, "POST").headers, data=login_form, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])
    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/logout")
async def logout(response: Response, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req = requests.get(f"https://{api_mirror}/logout",
                       cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    return {
        "status_code": req.status_code
    }


@app.get("/favorite")
async def get_fav(response: Response, page: int = 1, sort=sortBy.Time.value, fid: str = "0", AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                  ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

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

    req = requests.get(f"https://{api_mirror}/favorite/", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, verify=False, cookies=cookies)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/search")
async def search(query: str, response: Response, page: int = 1, sort=sortBy.Time.value, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "search_query": query,
        "page": page,
        "o": sort
    }

    req = requests.get(f"https://{api_mirror}/search", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, verify=False, cookies=cookies)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    cookies_dict = req.cookies.get_dict()
    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/history")
async def get_history(page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                      ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "page": page
    }

    req = requests.get(f"https://{api_mirror}/watch_list", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/album")
async def get_album_info(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                         ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "id": id
    }

    req = requests.get(f"https://{api_mirror}/album", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/chapter")
async def get_chapter_info(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                           ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "skip": "",
        "id": id
    }

    req = requests.get(f"https://{api_mirror}/chapter", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/img_list")
async def get_img_list(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                       ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "id": id,
        "mode": "vertical",
        "page": 0,
        "app_img_shunt": "NaN"
    }

    req = requests.get(f"https://{api_mirror}/chapter_view_template", params=req_body, headers=GetHeaders(
        req_time, "GET", True).headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    document = BeautifulSoup(req.content, "lxml")

    img_list = []

    for container in document.find_all("div", class_="center scramble-page"):
        img_list.append(container.attrs["id"])

    scramble_id = 220980
    try:
        mo = re.search(r"(?<=var scramble_id = )\w+", req.text)
        scramble_id = int(mo.group())
    except Exception as e:
        print(e)

    try:
        return {
            "status_code": req.status_code,
            "data": img_list,
            "scramble_id": scramble_id
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/img")
async def comic_img(id: str, page: str, scramble_id: str = "220980", pic_mirror: str = Cookie(default=PicList[0])):

    req = requests.get(
        f"https://{pic_mirror}/media/photos/{id}/{page}.webp", verify=False)

    decode_img = SegmentationPicture(req.content, id, scramble_id, page)

    return StreamingResponse(io.BytesIO(decode_img), media_type="image/webp")


@app.get("/comment/comic")
async def get_comment(id: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                      ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "mode": "manhua",
        "aid": id,
        "page": page
    }

    req = requests.get(f"https://{api_mirror}/forum", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/comment/user")
async def get_self_comment(uid: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                           ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "mode": "undefined",
        "uid": uid,
        "page": page
    }

    req = requests.get(f"https://{api_mirror}/forum", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }

    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.post("/comment")
async def send_comment(id: str, content: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                       ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comment": content,
        "aid": id
    }

    req = requests.post(f"https://{api_mirror}/comment", data=req_body, headers=GetHeaders(
        req_time, "POST").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }
    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/tags")
async def get_tags(AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                   ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    cookies = CookiesTranslate(AVS, __cflb, ipcountry, ipm5)

    req_time = int(time.time())

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null"
    }

    req = requests.get(f"https://{api_mirror}/categories", params=req_body, headers=GetHeaders(
        req_time, "GET").headers, cookies=cookies, verify=False)

    if(req.status_code != 200):
        try:
            return {
                "status_code": req.status_code,
                "errorMsg": req.json()["errorMsg"]
            }
        except:
            return {
                "status_code": req.status_code,
                "errorMsg": "Unknown Error"
            }
    try:
        return {
            "status_code": req.status_code,
            "data": ParseData(req_time, req.json()["data"])
        }
    except:
        return{
            "status_code": req.status_code,
            "data": "Data Error"
        }


@app.get("/speed/api")
async def speedtest_api():
    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "page": 0
    }
    spend_time = []

    for url in ApiList:
        req_time = int(time.time())

        start_time = time.perf_counter()
        try:
            req = requests.get(f"https://{url}/latest", params=req_body, headers=GetHeaders(
                req_time, "TEST").headers, verify=False)
        except Exception as e:
            print(e)
            spend_time.append({
                "url": url,
                "time": -1
            })
            continue
        if(req.status_code != 200):
            spend_time.append({
                "url": url,
                "time": -1
            })
        spend_time.append({
            "url": url,
            "time": int((time.perf_counter()-start_time)*1000)
        })

    return {
        "data": spend_time
    }


@app.get("/speed/pic")
async def speedtest_pic():

    spend_time = []

    for url in PicList:

        start_time = time.perf_counter()
        try:
            req = requests.get(
                f"https://{url}/media/photos/403567/00002.webp", verify=False, timeout=15000)
        except:
            spend_time.append({
                "url": url,
                "time": -1
            })
            continue
        if(req.status_code != 200):
            spend_time.append({
                "url": url,
                "time": -1
            })
        spend_time.append({
            "url": url,
            "time": int((time.perf_counter()-start_time)*1000)
        })

    return {
        "data": spend_time
    }


@app.get("/mirror")
async def set_mirror(response: Response, api: str = "", pic: str = ""):

    api_msg = ""
    pic_msg = ""

    if(api in ApiList):
        response.set_cookie(key="api_mirror", value=api)
        api_msg = f"你的API镜像已选择为{api}"
    else:
        response.set_cookie(key="api_mirror", value=ApiList[0])
        api_msg = f"你没有提供有效的选项，因此你的API镜像已默认为{ApiList[0]}"
    if(pic in PicList):
        response.set_cookie(key="pic_mirror", value=pic)
        pic_msg = f"你的图片镜像已选择为{pic}"
    else:
        response.set_cookie(key="pic_mirror", value=ApiList[0])
        pic_msg = f"你没有提供有效的选项，因此你的图片镜像已默认为{PicList[0]}"

    return{
        "api_msg": api_msg,
        "pic_msg": pic_msg
    }
