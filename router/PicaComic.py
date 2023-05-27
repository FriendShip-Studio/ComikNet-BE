from fastapi import APIRouter, Response, Cookie

from core.PicacgRequests import PicacgRequests
from models.user import Login_Form, Pica_Register_Form
from models.requests import StandardResponse
from models.sort import PicaSortRule
from models.album import PicaComicInfo, TinyComicInfo, Origin


router = APIRouter(prefix="/pica")


@router.post("/login", response_model=StandardResponse)
async def pica_login(body: Login_Form, response: Response):
    # 登录
    req = PicacgRequests()
    res = await req.post(
        "/auth/sign-in", {"email": body.username, "password": body.password}
    )

    if res.status_code == 200:
        assert res.data is not None
        req.setCookies(response, {"pica_token": res.data["token"]})
    await req.close()
    return res


@router.post("/register", response_model=StandardResponse)
async def pica_register(body: Pica_Register_Form):
    # 注册
    req = PicacgRequests()
    res = await req.post(
        "/auth/register",
        {
            "email": body.email,
            "password": body.password,
            "name": body.name,
            "birthday": body.birthday,
            "gender": body.gender,
            "answer1": body.answer1,
            "answer2": body.answer2,
            "answer3": body.answer3,
            "question1": body.question1,
            "question2": body.question2,
            "question3": body.question3,
        },
    )
    await req.close()

    # 与FSC通讯存储用户信息
    if body.isAccepted:
        pass
    else:
        pass
    return res


@router.get("/profile", response_model=StandardResponse)
async def pica_getProfile(pica_token: str = Cookie(default="")):
    # 获取用户信息
    req = PicacgRequests(pica_token)
    res = await req.get("/users/profile")
    await req.close()
    return res


@router.post("/punch", response_model=StandardResponse)
async def pica_punchIn(pica_token: str = Cookie(default="")):
    # 签到
    req = PicacgRequests(pica_token)
    res = await req.post("/users/punch-in", {})
    await req.close()
    return res


@router.get("/favor", response_model=StandardResponse)
async def pica_getFavor(
    page: int = 1,
    sort: PicaSortRule = PicaSortRule.Time,
    pica_token: str = Cookie(default=""),
):
    # 收藏夹
    req = PicacgRequests(pica_token)
    res = await req.get("/users/favourite", {"s": sort.value, "page": page})
    await req.close()
    try:
        assert res.data is not None
        fav_list = list()
        for item in res.data["comics"]["docs"]:
            fav_list.append(
                TinyComicInfo(
                    album_id=item["_id"],
                    name=item["title"],
                    author=[item["author"]],
                    categories=item["categories"],
                    origin=Origin.Picacomic,
                    cover=f"{item['thumb']['fileServer']}/static/{item['thumb']['path']}",
                ).__dict__()
            )
        return StandardResponse(status_code=res.status_code, data=fav_list)
    except AssertionError:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)


@router.post("/favor/{album_id}", response_model=StandardResponse)
async def pica_addFavor(album_id: str, pica_token: str = Cookie(default="")):
    # 添加收藏
    req = PicacgRequests(pica_token)
    res = await req.post(f"/comics/{album_id}/favourite", {})
    await req.close()
    return res


@router.get("/album", response_model=StandardResponse)
async def pica_getAlbum(album_id: str, pica_token: str = Cookie(default="")):
    # 漫画信息
    req = PicacgRequests(pica_token)
    res = await req.get(f"/comics/{album_id}")
    await req.close()

    try:
        assert res.data is not None
        album_info = PicaComicInfo(
            album_id=res.data["comic"]["_id"],
            name=res.data["comic"]["title"],
            description=res.data["comic"]["description"],
            author=[res.data["comic"]["author"]],
            cover=f"{res.data['comic']['thumb']['fileServer']}/static/{res.data['comic']['thumb']['path']}",
            categories=res.data["comic"]["categories"],
            is_favor=res.data["comic"]["isFavourite"],
            tags=res.data["comic"]["tags"],
            is_liked=res.data["comic"]["isLiked"],
            total_likes=res.data["comic"]["totalLikes"],
            translator=res.data["comic"]["chineseTeam"],
            isFinished=res.data["comic"]["finished"],
            updated_at=res.data["comic"]["updated_at"],
            created_at=res.data["comic"]["created_at"],
            allowComment=res.data["comic"]["allowComment"],
            total_comments=res.data["comic"]["totalComments"],
            total_views=res.data["comic"]["totalViews"],
        )
        return StandardResponse(status_code=res.status_code, data=album_info.__dict__())
    except AssertionError:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)


@router.get("/comments/album", response_model=StandardResponse)
async def pica_getAlbumComments(
    album_id: str, page: int = 1, pica_token: str = Cookie(default="")
):
    # 漫画评论
    req = PicacgRequests(pica_token)
    res = await req.get(f"/comics/{album_id}/comments", {"page": page})
    await req.close()
    return res


@router.get("/comments/user", response_model=StandardResponse)
async def pica_getUserComments(
    user_id: str, page: int = 1, pica_token: str = Cookie(default="")
):
    # 用户评论
    req = PicacgRequests(pica_token)
    res = await req.get(f"/users/my-comments", {"page": page})
    await req.close()
    return res


@router.get("/comments/album/{comment_id}", response_model=StandardResponse)
async def pica_getSubComments(
    comment_id: str, page: int = 1, pica_token: str = Cookie(default="")
):
    # 获取子评论
    req = PicacgRequests(pica_token)
    res = await req.get(f"/comments/{comment_id}/childrens", {"page": page})
    await req.close()
    return res


@router.get("/album/chapters", response_model=StandardResponse)
async def pica_getAlbumChapter(
    album_id: str, page: int = 1, pica_token: str = Cookie(default="")
):
    # 漫画章节列表
    req = PicacgRequests(pica_token)
    res = await req.get(f"/comics/{album_id}/eps", {"page": page})
    await req.close()
    return res


@router.get("/comic", response_model=StandardResponse)
async def pica_getComic(
    album_id: str, chapter_id: str, page: int = 1, pica_token: str = Cookie(default="")
):
    # 漫画图片信息
    req = PicacgRequests(pica_token)
    res = await req.get(f"/comics/{album_id}/order/{chapter_id}/pages", {"page": page})
    await req.close()
    return res


@router.get("/related", response_model=StandardResponse)
async def pica_getRelated(album_id: str, pica_token: str = Cookie(default="")):
    # 相关推荐
    req = PicacgRequests(pica_token)
    res = await req.get(f"/comics/{album_id}/recommendation")
    await req.close()

    try:
        assert res.data is not None
        related_list = list()
        for item in res.data["comics"]:
            related_list.append(
                TinyComicInfo(
                    album_id=item["_id"],
                    name=item["title"],
                    author=[item["author"]],
                    categories=item["categories"],
                    origin=Origin.Picacomic,
                    cover=f"{item['thumb']['fileServer']}/static/{item['thumb']['path']}",
                ).__dict__()
            )
        return StandardResponse(status_code=res.status_code, data=related_list)
    except AssertionError:
        return StandardResponse(status_code=res.status_code, error_msg=res.error_msg)
