from example.app.view import PermissionsView, UsersView
from fastapi_simple_class_view.controller import APIController

app_router = APIController()

app_router.controller_register('/users/', UsersView())

app_router.add_endpoint('/users/custom_endpoint/', UsersView().custom_endpoint, method='POST')

app_router.controller_register('/perm/', PermissionsView())
