from collections import defaultdict

from fastapi_simple_class_view.base import APIView
from fastapi_simple_class_view.mixins import GenericView
from fastapi_simple_class_view.type import PyModel, UserModel

from .permissions import is_customer, is_superuser
from .scheme import DefaultScheme, PermissionsScheme, UserCreateUpdate, UserSchema
from .service import permissions_service, user_service


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

    def custom_endpoint(self, user: UserModel, q: int) -> DefaultScheme:
        return {
            'id': 10,
            'username': 'custom_endpoint_username',
        }


class PermissionsView(GenericView, APIView):
    py_model = defaultdict(lambda: PermissionsScheme)
    permissions = defaultdict(
        lambda: is_superuser,
    )
    service = permissions_service
    slug_field_type = int
