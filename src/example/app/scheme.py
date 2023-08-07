from typing import Dict, List

from pydantic import BaseModel

from fastapi_simple_class_view.type import PyModel


class UserSchema(BaseModel):
    id: int
    username: str


class UserCreateUpdate(BaseModel):
    username: str
    first_name: str
    last_name: str


class PermissionsScheme(BaseModel):
    id: int
    code: str


class DefaultScheme(BaseModel):
    id: int
    model: List[Dict[int, PyModel]]
