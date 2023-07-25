import json

import pytest
from starlette.testclient import TestClient

from example.app.service import UserService
from example.database import UsersModel
from example.main import app
from fastapi_class_view.base import BaseService


@pytest.fixture
def client():
    yield TestClient(app)


def test_list(client, monkeypatch):
    async def patch(self):
        return [UsersModel(id=1, username='first_user'), UsersModel(id=2, username='second_user')]

    monkeypatch.setattr(UserService, "list", patch)
    response = client.get('/users/')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) == 2


def test_retrieve(client, monkeypatch):
    async def patch(self, pk):
        return UsersModel(id=pk, username='first_user')

    monkeypatch.setattr(BaseService, "retrieve", patch)
    response = client.get('/users/1/')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['username'] == 'first_user'
