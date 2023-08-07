from collections import defaultdict

from fastapi_simple_class_view.base import APIView
from fastapi_simple_class_view.mixins import GenericView
from fastapi_simple_class_view.type import PyModel, UserModel

from .permissions import is_customer, is_superuser
from .scheme import UserCreateUpdate, UserSchema
from .service import user_service


class UsersView(GenericView, APIView):
    py_model = defaultdict(
        lambda: UserSchema,
        {
            'retrieve': UserCreateUpdate,
            'create': UserCreateUpdate,
            'update': UserCreateUpdate,
        },
    )
    permissions = defaultdict(
        lambda: is_superuser,
        {
            'list': is_customer,
        },
    )
    service = user_service
    slug_field_type = int

    def custom_endpoint(self, user: UserModel, q: int) -> PyModel:
        return {
            'id': 10,
            'username': 'custom_endpoint_username',
        }
