from typing import Callable

from fastapi import APIRouter

from fastapi_class_view.base import APIView


class APIController(APIRouter):
    def controller_register(self, base_path, controller: APIView):
        if hasattr(controller, 'list'):
            self.add_endpoint(base_path, getattr(controller, 'list'), 'GET')
        if hasattr(controller, 'create'):
            self.add_endpoint(base_path, getattr(controller, 'create'), 'POST', status_code=201)
        if hasattr(controller, 'retrieve'):
            self.add_endpoint(base_path + '{pk}/', getattr(controller, 'retrieve'), 'GET')
        if hasattr(controller, 'update'):
            self.add_endpoint(base_path + '{pk}/', getattr(controller, 'update'), 'PUT')
        if hasattr(controller, 'delete'):
            self.add_endpoint(
                base_path + '{pk}/',
                getattr(controller, 'delete'),
                'DELETE',
                status_code=204,
            )

    def add_endpoint(self, path: str, view_func: Callable, method: str, status_code=200):
        self.add_api_route(path, view_func, methods=[method], status_code=status_code)
