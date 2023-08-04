from typing import Callable, Dict, List, Type

from pydantic import BaseModel
from sqlalchemy import delete, select, update

from .abc import AbstractService
from .meta import DynamicParamMeta
from .type import SlugField


class APIView(metaclass=DynamicParamMeta):
    py_model: Dict[str, Type[BaseModel]]
    permissions: Dict[str, Type[Callable]]
    service: AbstractService
    slug_field_type: SlugField


class BaseService(AbstractService):
    async def list(self):
        async with self.session_factory() as session:
            query = select(self.model)
            result = await session.scalars(query)
            result = result.all()
            return result

    async def retrieve(self, pk: SlugField):
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.id == pk)
            result = await session.scalars(query)
            return result.one()

    async def add(self, data: Dict):
        async with self.session_factory() as session:
            instance = self.model(**data)
            session.add(instance)
            await session.flush()
            return instance

    async def update(self, pk: SlugField, data: Dict):
        async with self.session_factory() as session:
            query = update(self.model).where(self.model.id == pk).values(**data)
            await session.execute(query)
            await session.commit()
            return data

    async def delete(self, pk: SlugField):
        async with self.session_factory() as session:
            query = delete(self.model).where(self.model.id == pk)
            await session.execute(query)
            await session.commit()
