from fastapi import APIRouter, Response

from core.ComikNetDB import AsyncMySQL
from models.requests import StandardResponse
from models.album import Origin
from models.user import UserHistory

router = APIRouter(prefix="/cloud")


@router.on_event("startup")
async def startup():
    global db
    db = AsyncMySQL()
    await db.init()


@router.on_event("shutdown")
async def shutdown():
    await db.close()


@router.get("/history/user")
async def get_history(
    uid: str, page: int = 1, isReverse: bool = False
) -> StandardResponse:
    res = await db.search(
        "Origin, AID, CID, Update_Time",
        "history",
        f"UID={uid}",
        f"{(page-1)*20},{page*20}",
        f"Update_Time {'ASC' if isReverse else 'DESC'}",
    )

    ret_list = [UserHistory(**item).dict() for item in res]

    return StandardResponse(status_code=200, data=ret_list)


@router.delete("/history")
async def delete_history(uid: str):
    await db.delete("history", f"UID={uid}")
    return Response(status_code=200)


@router.post("/record")
async def update_history(uid: str, origin: Origin, aid: int, cid: int):
    res = await db.search(
        "*", "history", f"UID={uid} AND Origin=\"{origin.value}\" AND AID={aid}", "1", "update_time DESC"
    )

    if res == ():
        await db.insert(
            "history",
            "UID, Origin, AID, CID, Update_Time",
            f"{uid},\"{origin.value}\",{aid},{cid},NOW()",
        )
    else:
        await db.update(
            "history", f"CID={cid} AND Origin=\"{origin.value}\", update_time=NOW()", f"UID={uid} AND AID={aid}"
        )

    return Response(status_code=201)
