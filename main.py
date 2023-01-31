import sys
import time
import re
import requests
import asyncio
if sys.platform != "win32":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    
from fastapi import FastAPI, Response, Cookie
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup


from src.utils.asyncRequests import AsyncRequests
from src.models.headers import GetHeaders
from src.models.bodys import LoginBody, SignupBody
from src.models.sort import sortBy
from src.models.mirrors import PicList, ApiList, WebList
from src.utils.parseData import AuthorStr2List
from src.utils.parseDate import parseDate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/captcha")
async def get_captcha(response: Response):

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

    cookies_dict["signup_url"] = avail_url

    for cookie in cookies_dict:
        response.set_cookie(cookie, cookies_dict[cookie])

    req = requests.get(f"https://{url}/captcha",
                       cookies=cookies, verify=False)

    return StreamingResponse(req.iter_content(), media_type="image/jpeg", headers=response.headers)


@app.post("/register")
async def register(body: SignupBody, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                   ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), signup_url: str = Cookie(default="jmcomic1.onl")):

    req_time = int(time.time())

    req = AsyncRequests(signup_url, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

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

    res = req.post("/signup", headers=GetHeaders(
        req_time, "POST").headers, data=req_body)
    await req.close()

    msg_list = []
    try:
        document = BeautifulSoup(res["data"], "lxml")
    except:
        return res

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
        "status_code": res["status_code"],
        "data": msg_list
    }


@app.post("/login")
async def login(body: LoginBody, response: Response, api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    login_form = {
        "username": body.username,
        "password": body.password,
        "login_remember": "on",
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": None
    }

    req = AsyncRequests(api_mirror)
    res = await req.post("/login", req_time, headers=GetHeaders(
        req_time, "POST").headers, data=login_form)

    req.setCookies(response)

    await req.close()

    return res


@app.get("/logout")
async def logout(response: Response, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default="")):

    cookies = {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    }
    for cookie in cookies:
        response.set_cookie(cookie, "")

    return {
        "status_code": 200,
        "data": "已登出"
    }


@app.get("/favorite")
async def get_fav(response: Response, page: int = 1, sort=sortBy.Time.value, fid: str = "0", AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                  ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    if(sort not in [sortBy.Time.value, sortBy.Images.value]):
        # 此处按图片排序代指按更新时间排序
        # time代表按收藏时间排序
        sort = sortBy.Time.value

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "page": page,
        "folder_id": fid,
        "o": sort
    }

    res = await req.get("/favorite", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    try:
        for item in res["data"]["list"]:
            item["author"] = AuthorStr2List(item["author"])
        return res
    except:
        return res


@app.get("/search")
async def search(query: str, page: int = 1, sort=sortBy.Time.value, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                 ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "search_query": query,
        "page": page,
        "o": sort
    }

    res = await req.get("/search", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    try:
        for item in res["data"]["content"]:
            item["author"] = AuthorStr2List(item["author"])
        return res
    except:
        return res


@app.get("/album")
async def get_album_info(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                         ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "id": id
    }

    res = await req.get("/album", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    try:
        for item in res["data"]["related_list"]:
            item["author"] = AuthorStr2List(item["author"])
        return res
    except:
        return res


@app.get("/chapter")
async def get_chapter_info(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                           ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):
    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "skip": "",
        "id": id
    }

    res = await req.get("/chapter", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    return res


@app.get("/img_list")
async def get_img_list(id: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                       ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "id": id,
        "mode": "vertical",
        "page": 0,
        "app_img_shunt": "NaN"
    }

    res = await req.getContent("/chapter_view_template", headers=GetHeaders(
        req_time, "GET", True).headers, params=req_body)
    await req.close()

    try:
        document = BeautifulSoup(res["data"], "lxml")
    except:
        return res

    img_list = []
    for container in document.find_all("div", class_="center scramble-page"):
        img_list.append(container.attrs["id"])

    scramble_id = 220980
    try:
        mo = re.search(r"(?<=var scramble_id = )\w+",
                       res["data"].decode("utf-8"))
        scramble_id = int(mo.group())
    except Exception as e:
        print(e)

    return {
        "status_code": res["status_code"],
        "data": {
            "scramble_id": scramble_id,
            "img_list": img_list
        }
    }


@app.get("/comment/comic")
async def get_comment(id: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                      ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "mode": "manhua",
        "aid": id,
        "page": page
    }

    res = await req.get("/forum", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    try:
        return {
            "status_code": res["status_code"],
            "data": {
                "list": parseDate(res["data"]["list"]),
                "total": res["data"]["total"]
            }
        }
    except:
        return res


@app.get("/comment/user")
async def get_self_comment(uid: str, page: int = 1, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                           ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "mode": "undefined",
        "uid": uid,
        "page": page
    }

    res = await req.get("/forum", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    try:
        return {
            "status_code": res["status_code"],
            "data": {
                "list": parseDate(res["data"]["list"]),
                "total": res["data"]["total"]
            }
        }
    except:
        return res


@app.post("/comment")
async def send_comment(id: str, content: str, AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                       ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comment": content,
        "aid": id
    }

    res = await req.post("/comment", req_time, headers=GetHeaders(
        req_time, "POST").headers, data=req_body)
    await req.close()

    return res


@app.get("/tags")
async def get_tags(AVS: str = Cookie(default=""), __cflb: str = Cookie(default=""),
                   ipcountry: str = Cookie(default=""), ipm5: str = Cookie(default=""), remember: str = Cookie(default=""), api_mirror: str = Cookie(default=ApiList[0])):

    req_time = int(time.time())

    req = AsyncRequests(api_mirror, {
        "AVS": AVS,
        "__cflb": __cflb,
        "ipcountry": ipcountry,
        "ipm5": ipm5,
        "remember": remember
    })

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null"
    }

    res = await req.get("/categories", req_time, headers=GetHeaders(
        req_time, "GET").headers, params=req_body)
    await req.close()

    return res


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

        req = AsyncRequests(url, conn_timeout=5, read_timeout=13)
        req_time = int(time.time())

        start_time = time.perf_counter()
        try:
            res = await req.get("/latest", req_time, params=req_body, headers=GetHeaders(
                req_time, "TEST").headers)
            await req.close()
        except Exception as e:
            print(e)
            spend_time.append({
                "url": url,
                "time": -1
            })
            continue
        if(res["status_code"] != 200):
            spend_time.append({
                "url": url,
                "time": -1
            })
            continue
        spend_time.append({
            "url": url,
            "time": int((time.perf_counter()-start_time)*1000)
        })

    return {
        "status_code": 200,
        "data": spend_time
    }


@app.get("/speed/pic")
async def get_picMirrorList():
    return {
        "status_code": 200,
        "data": PicList
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
