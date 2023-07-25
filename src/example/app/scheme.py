from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str


class UserCreateUpdate(BaseModel):
    username: str
    first_name: str
    last_name: str
