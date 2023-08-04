import asyncio
import os

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config
from starlette.testclient import TestClient

from example.database import Database
from example.main import app
from example.settings import database_settings


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def run_sql_migrations():
    os.environ['DB_PATH'] = f'{database_settings.PATH}_test'
    Database().setup_database(f'{database_settings.PATH}_test')
    await Database().create_database(f'{database_settings.PATH}_test')
    migrations_dir = os.path.join(os.path.dirname(__file__), '../migrations')
    config_file = os.path.join(os.path.dirname(__file__), '../alembic.ini')
    config = Config(file_=config_file)
    config.set_main_option("script_location", migrations_dir)
    upgrade(config, "head")
    yield
    await Database().drop_database(f'{database_settings.PATH}_test')


@pytest_asyncio.fixture
async def client(run_sql_migrations):
    os.environ['DEBUG'] = 'True'
    await Database()._engine.dispose()
    yield TestClient(app, headers={"Authorization": "Bearer 123"})


@pytest.mark.asyncio()
async def test_01_list(client):
    response = client.get('/users/')
    assert response.status_code == 200


@pytest.mark.asyncio()
async def test_001_create(client):
    response = client.post(
        '/users/',
        json={"username": "string", "first_name": "string", "last_name": "string"},
    )
    assert response.status_code == 201


#
# def test_retrieve(client, monkeypatch):
#     async def patch(self, pk):
#         return UsersModel(id=pk, username='first_user')
#
#     monkeypatch.setattr(BaseService, "retrieve", patch)
#     response = client.get('/users/1/')
#     assert response.status_code == 200
#     data = json.loads(response.content)
#     assert data['username'] == 'first_user'
