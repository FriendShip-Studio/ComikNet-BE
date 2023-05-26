from pydantic import BaseModel
from datetime import datetime

from models.album import Origin


class Login_Form(BaseModel):
    username: str
    password: str


class FSC_UserDeposit(BaseModel):
    isAccepted: bool


class Pica_Register_Form(FSC_UserDeposit, BaseModel):
    # 哔咔注册不再需要真实的邮箱和邮箱验证，用户忘记密码将直接导致账户遗失
    email: str
    password: str
    name: str
    birthday: str
    gender: str  # m, f, bot
    answer1: str
    answer2: str
    answer3: str
    question1: str
    question2: str
    question3: str


class UserHistory(BaseModel):
    """
    User History Class
    ~~~~~~~~~~~~~~~~~~~~~
    User History Class contains the user's reading history which is stored in the fsc's database.
    """

    UID: int
    Origin: Origin
    AID: int
    CID: int
    Update_Time: datetime
