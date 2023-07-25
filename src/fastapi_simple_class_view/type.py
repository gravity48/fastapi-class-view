from typing import NewType, TypeVar

from pydantic import BaseModel

PyModel = NewType("PyModel", BaseModel)

UserModel = NewType("UserModel", BaseModel)

SlugField = TypeVar('SlugField')
