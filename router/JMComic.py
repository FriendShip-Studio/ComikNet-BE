from fastapi import APIRouter, Cookie, Response
from bs4 import BeautifulSoup
import re

from core.JMRequests import JMRequests, JMToolUtils
from models.mirrors import ApiList
from models.user import Login_Form
from models.requests import SearchInfo, StandardResponse
from models.sort import JMSortRule
from models.album import JMComicInfo, TinyComicInfo, Origin


router = APIRouter(prefix="/jm")


@router.post("/login", response_model=StandardResponse)
async def jm_login(
    body: Login_Form, response: Response, api_mirror: str = Cookie(default=ApiList[0])
):
    # 登录
    login_form = {
        "username": body.username,
        "password": body.password,
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "login_remember": "on",
        "view_mode_debug": 1,
        "view_mode": None,
    }

    req = JMRequests(api_mirror)
    res = await req.post("/login", data=login_form)

    req.setCookies(response, except_cookies=["__cflb", "ipcountry", "ipm5"])
    await req.close()

    return res


@router.get("/album", response_model=StandardResponse)
async def jm_getAlbum(
    album_id: str,
    AVS: str = Cookie(default=""),
    remember: str = Cookie(default=""),
    api_mirror: str = Cookie(default=ApiList[0]),
):
    # 漫画信息
    req = JMRequests(api_mirror, {"AVS": AVS, "remember": remember})

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "id": album_id,
    }

    res = await req.get("/album", params=req_body)
    await req.close()

    try:
        assert res.data is not None

        album_info = JMComicInfo(
            album_id=res.data["id"],
            name=res.data["name"],
            author=res.data["author"],
            cover=f"/media/albums/{res.data['id']}_3x4.jpg",
            description=res.data["description"],
            total_views=res.data["total_views"],
            total_likes=res.data["likes"],
            total_comments=res.data["comment_total"],
            series=res.data["series"],
            tags=res.data["tags"],
            is_favor=res.data["is_favorite"],
            is_liked=res.data["liked"],
            related_list=[
                TinyComicInfo(
                    item["id"],
                    name=item["name"],
                    author=JMToolUtils.AuthorStr2List(item["author"]),
                    cover=f"/media/albums/{item['id']}_3x4.jpg",
                    origin=Origin.JMComic,
                ).__dict__()
                for item in res.data["related_list"]
            ],
            series_id=res.data["series_id"],
            works=res.data["works"],
            actors=res.data["actors"],
        ).__dict__()
        return StandardResponse(status_code=200, data=album_info)
    except AssertionError:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)


@router.get("/album/chapter", response_model=StandardResponse)
async def jm_getChapters(
    album_id: str,
    AVS: str = Cookie(default=""),
    remember: str = Cookie(default=""),
    api_mirror: str = Cookie(default=ApiList[0]),
):
    # 章节信息
    req = JMRequests(api_mirror, {"AVS": AVS, "remember": remember})

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "comicName": "",
        "skip": "",
        "id": album_id,
    }

    res = await req.get("/chapters", params=req_body)
    await req.close()

    try:
        assert res.data is not None
        if res.data["series"] == []:
            return StandardResponse(status_code=200, data=[album_id])
        else:
            return StandardResponse(
                status_code=200,
                data=[item["id"] for item in res.data["series"]],
            )
    except AssertionError:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)


@router.get("/comic", response_model=StandardResponse)
async def jm_getComic(
    chapter_id: str,
    AVS: str = Cookie(default=""),
    remember: str = Cookie(default=""),
    api_mirror: str = Cookie(default=ApiList[0]),
):
    # 图片列表
    req = JMRequests(api_mirror, {"AVS": AVS, "remember": remember})

    req_body = {"id": chapter_id, "mode": "vertical", "page": 0, "app_img_shunt": "NaN"}

    res = await req.getContent("/chapter_view_template", params=req_body)
    await req.close()

    try:
        assert res.data is not None
        document = BeautifulSoup(res.data, "lxml")
        img_list = []
        for container in document.find_all("div", class_="center scramble-page"):
            img_list.append(container.attrs["id"])

        mo = re.search(r"(?<=var scramble_id = )\w+", res.data.decode("utf-8"))
        if mo is None:
            scramble_id = 220980
        else:
            scramble_id = int(mo.group())
        return StandardResponse(
            status_code=200, data={"scramble_id": scramble_id, "img_list": img_list}
        )
    except AssertionError:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)


@router.get("/logout", response_model=StandardResponse)
async def jm_logout(response: Response):
    # 登出
    cookies = {"AVS": "", "remember": ""}
    for cookie in cookies:
        response.set_cookie(cookie, "")

    return StandardResponse(status_code=200, data="Success")


@router.get("/favor", response_model=StandardResponse)
async def jm_getFavor(
    page: int = 1,
    sort: JMSortRule = JMSortRule.Time,
    fid: str = "0",
    AVS: str = Cookie(default=""),
    remember: str = Cookie(default=""),
    api_mirror: str = Cookie(default=ApiList[0]),
):
    # 获取收藏夹
    req = JMRequests(
        api_mirror,
        {
            "AVS": AVS,
            "remember": remember,
        },
    )

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "page": page,
        "folder_id": fid,
        "o": sort,
    }

    res = await req.get("/favorite", params=req_body)
    await req.close()

    try:
        assert res.data is not None
        fav_list = list()
        for item in res.data["list"]:
            fav_list.append(
                TinyComicInfo(
                    album_id=item["id"],
                    name=item["name"],
                    origin=Origin.JMComic,
                    categories=TinyComicInfo.JM_categories_formatter(
                        [item["category"], item["category_sub"]]
                    ),
                    cover=f"/media/albums/{item['id']}_3x4.jpg",
                    author=JMToolUtils.AuthorStr2List(item["author"]),
                ).__dict__()
            )
        return StandardResponse(status_code=res.status_code, data=fav_list)
    except:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)


@router.post("/favor/{album_id}", response_model=StandardResponse)
async def jm_addFavor(
    album_id: str,
    AVS: str = Cookie(default=""),
    remember: str = Cookie(default=""),
    api_mirror: str = Cookie(default=ApiList[0]),
):
    # 添加收藏
    req = JMRequests(api_mirror, {"AVS": AVS, "remember": remember})

    req_body = {
        "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
        "view_mode_debug": 1,
        "view_mode": "null",
        "aid": album_id,
    }

    res = await req.post("/favorite", data=req_body)
    await req.close()

    return res
