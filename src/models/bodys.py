from pydantic import BaseModel


class LoginBody(BaseModel):
    username: str
    password: str


class SignupBody(BaseModel):
    username: str
    password: str
    email: str
    captcha: str
    sex: str


class FavorBody(BaseModel):
    aid: str
