from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True


class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdateSchema(BaseModel):
    username: str
    password: str
