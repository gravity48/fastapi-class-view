from example.database import Database, UsersModel
from fastapi_class_view.base import BaseService


class UserService(BaseService):
    model = UsersModel


user_service = UserService(Database().session)
