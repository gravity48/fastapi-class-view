from example.app.view import UsersView
from fastapi_class_view.controller import APIController

app_router = APIController()

app_router.controller_register('/users/', UsersView())
