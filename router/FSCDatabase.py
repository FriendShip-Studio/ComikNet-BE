import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from binascii import b2a_hex, a2b_hex
from fastapi import APIRouter, Response

from core.ComikNetDB import AsyncMySQL
from models.requests import StandardResponse
from models.album import Origin
from models.user import UserHistory, Login_Form, Cloud_Reigister_Form

router = APIRouter(prefix="/cloud")


@router.on_event("startup")
async def startup():
    global db
    db = AsyncMySQL()
    await db.init()


@router.on_event("shutdown")
async def shutdown():
    await db.close()


@router.post("/login")
async def user_login(body: Login_Form):
    res = await db.search(
        "UID, Password",
        "user",
        f'Username="{body.username}"',
        "1",
    )

    if res == ():
        return StandardResponse(status_code=401, error_msg="User not found")

    if bcrypt.checkpw(body.password.encode(), res[0]["Password"].encode()):
        return StandardResponse(status_code=200, data={"UID": res[0]["UID"]})
    else:
        return StandardResponse(status_code=401, error_msg="Wrong password")


@router.post("/register")
async def user_register(body: Cloud_Reigister_Form):
    cloud_hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    aes = AES.new(pad(body.password.encode(), 32), AES.MODE_ECB)
    jm_encrypted_pwd = b2a_hex(
        aes.encrypt(pad(body.jm_form.password.encode(), 32))
    ).decode()
    pica_encrypted_pwd = b2a_hex(
        aes.encrypt(pad(body.pica_form.password.encode(), 32))
    ).decode()

    await db.insert(
        "user",
        "Username, Password, JM_Username, JM_Password, Pica_Username, Pica_Password",
        f'"{body.username}","{cloud_hashed}","{body.jm_form.username}","{jm_encrypted_pwd}","{body.pica_form.username}","{pica_encrypted_pwd}"',
    )

    return Response(status_code=201)


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
        "*",
        "history",
        f'UID={uid} AND Origin="{origin.value}" AND AID={aid}',
        "1",
        "update_time DESC",
    )

    if res == ():
        await db.insert(
            "history",
            "UID, Origin, AID, CID, Update_Time",
            f'{uid},"{origin.value}",{aid},{cid},NOW()',
        )
    else:
        await db.update(
            "history",
            f'CID={cid} AND Origin="{origin.value}", update_time=NOW()',
            f"UID={uid} AND AID={aid}",
        )

    return Response(status_code=201)
