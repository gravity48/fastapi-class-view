from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from .abc import AbstractGenericView
from .type import PyModel, SlugField, UserModel


class GenericView(AbstractGenericView):
    async def list(self, user: UserModel) -> List[PyModel]:
        return await self.service.list()

    async def retrieve(self, pk: SlugField, user: UserModel) -> PyModel:
        try:
            return await self.service.retrieve(pk)
        except NoResultFound:
            raise HTTPException(status_code=404)

    async def create(self, model: PyModel, user: UserModel) -> PyModel:
        return await self.service.add(model.model_dump())

    async def update(self, pk: SlugField, model: PyModel, user: UserModel) -> PyModel:
        return await self.service.update(pk, model.model_dump())

    async def delete(self, pk: SlugField, user: UserModel):
        return await self.service.delete(pk)
