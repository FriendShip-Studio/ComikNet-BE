from fastapi import FastAPI, Cookie
from fastapi.middleware.cors import CORSMiddleware


from core.PicacgRequests import PicacgRequests
from core.JMRequests import JMRequests, JMToolUtils
from models.mirrors import ApiList
from models.requests import SearchInfo, StandardResponse, SearchMode
from models.sort import PicaSortRule, JMSortRule
from models.album import TinyComicInfo, Origin
from router import JMComic, PicaComic, FSCDatabase

app = FastAPI(title="ComikNet-BE")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(JMComic.router)
app.include_router(PicaComic.router)
app.include_router(FSCDatabase.router)


@app.post("/search", response_model=StandardResponse)
async def search(
    search_query: SearchInfo,
    pica_token: str = Cookie(default=""),
    AVS: str = Cookie(default=""),
    remember: str = Cookie(default=""),
    api_mirror: str = Cookie(default=ApiList[0]),
):
    # 搜索
    if search_query.mode == SearchMode.JM:
        req = JMRequests(api_mirror, {"AVS": AVS, "remember": remember})

        req_body = {
            "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
            "view_mode_debug": 1,
            "view_mode": "null",
            "search_query": search_query.query,
            "page": search_query.page,
            "o": search_query.sort.value
            if search_query.sort is not None
            else JMSortRule.Time.value,
        }

        res = await req.get("/search", params=req_body)
        await req.close()
        search_res = {"total": 0, "result": list()}
        try:
            assert res.data is not None
            search_res["total"] = int(res.data["total"])

            for item in res.data["content"]:
                search_res["result"].append(
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
            return StandardResponse(status_code=res.status_code, data=search_res)
        except AssertionError:
            return StandardResponse(
                status_code=res.status_code, error_msg=res.error_msg
            )

    elif search_query.mode == SearchMode.Pica:
        req = PicacgRequests(pica_token)
        res = await req.post(
            "/comics/advanced-search",
            params={"page": search_query.page},
            data={
                "categories": search_query.append_query,
                "keyword": search_query.query,
                "sort": search_query.sort.value
                if search_query.sort is not None
                else PicaSortRule.Time.value,
            },
        )
        await req.close()
        search_res = {"total": 0, "result": list()}

        try:
            assert res.data is not None
            search_res["total"] = res.data["comics"]["total"]

            for item in res.data["comics"]["docs"]:
                search_res["result"].append(
                    TinyComicInfo(
                        album_id=item["_id"],
                        name=item["title"],
                        author=[item["author"]],
                        categories=item["categories"],
                        origin=Origin.Picacomic,
                        cover=f"{item['thumb']['fileServer']}/static/{item['thumb']['path']}",
                    ).__dict__()
                )
            return StandardResponse(status_code=res.status_code, data=search_res)
        except AssertionError:
            return StandardResponse(
                status_code=res.status_code, error_msg=res.error_msg
            )

    else:
        req = JMRequests(api_mirror, {"AVS": AVS, "remember": remember})

        req_body = {
            "key": "0b931a6f4b5ccc3f8d870839d07ae7b2",
            "view_mode_debug": 1,
            "view_mode": "null",
            "search_query": search_query.query,
            "page": search_query.page,
            "o": search_query.sort.value
            if search_query.sort is not None
            else JMSortRule.Time.value,
        }

        res = await req.get("/search", params=req_body)
        await req.close()
        search_res = {"total": 0, "result": list()}
        try:
            assert res.data is not None
            search_res["total"] = int(res.data["total"])

            for item in res.data["content"]:
                search_res["result"].append(
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
        except AssertionError:
            pass

        req = PicacgRequests(pica_token)
        res = await req.post(
            "/comics/advanced-search",
            params={"page": search_query.page},
            data={
                "categories": search_query.append_query,
                "keyword": search_query.query,
                "sort": search_query.sort.value
                if search_query.sort is not None
                else PicaSortRule.Time.value,
            },
        )
        await req.close()

        try:
            assert res.data is not None
            search_res["total"] += res.data["comics"]["total"]

            for item in res.data["comics"]["docs"]:
                search_res["result"].append(
                    TinyComicInfo(
                        album_id=item["_id"],
                        name=item["title"],
                        author=[item["author"]],
                        categories=item["categories"],
                        origin=Origin.Picacomic,
                        cover=f"{item['thumb']['fileServer']}/static/{item['thumb']['path']}",
                    ).__dict__()
                )
            return StandardResponse(status_code=res.status_code, data=search_res)
        except AssertionError:
            return StandardResponse(
                status_code=res.status_code, error_msg=res.error_msg
            )
