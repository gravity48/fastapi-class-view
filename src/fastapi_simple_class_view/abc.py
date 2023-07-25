from typing import Callable, ContextManager, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from .type import PyModel, SlugField, UserModel


class AbstractService:
    model: DeclarativeMeta
    slug_field: SlugField

    def __init__(self, session: Callable[..., ContextManager[AsyncSession]]):
        self.session_factory = session

    async def list(self) -> List:
        raise NotImplementedError

    async def retrieve(self, pk: SlugField):
        raise NotImplementedError

    async def add(self, data: PyModel):
        raise NotImplementedError

    async def update(self, pk: SlugField, data: PyModel):
        raise NotImplementedError

    async def delete(self, pk: SlugField, data: PyModel):
        raise NotImplementedError


class AbstractGenericView:
    async def list(self) -> List[PyModel]:
        raise NotImplementedError()

    async def create(self, model: PyModel, user: UserModel) -> PyModel:
        raise NotImplementedError()

    async def update(self, pk: SlugField, model: PyModel, user: UserModel) -> PyModel:
        raise NotImplementedError()

    async def retrieve(self, pk: SlugField, user: UserModel) -> PyModel:
        raise NotImplementedError()

    async def delete(self, pk: SlugField, user: UserModel):
        raise NotImplementedError()
