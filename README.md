# Class based view in FastApi

This package gives you convenient access for writing and maintaining class based
controllers in FastAPI framework

## Install package

```shell
pip install gspot-fastapi-auth
```

## Quickstart

### Typical app structure

An example of a typical application structure, you can redefine it at your discretion

```bash
.
├── app
│   ├── __init__.py
│   ├── permissions.py
│   ├── scheme.py
│   ├── service.py
│   ├── urls.py
│   └── view.py
```

### view.py

Simple writing of CRUD operation for user model  
It includes:

* permissions - Dict (checking for rights to a specific endpoint)
* py_model - Dict (the specific Pydantic schema to be used in the response or request)
* service - service class object (the service that will be used to make requests to the database)
* slug_field_type - Type (the type of slug field, used for the correct operation of the swagger)

```python
from fastapi_class_view.base import APIView
from fastapi_class_view.mixins import GenericView
from collections import defaultdict

from .permissions import is_superuser, is_customer
from .scheme import UserSchema, UserCreateUpdate
from .service import user_service


class UsersView(GenericView, APIView):
    py_model = defaultdict(lambda: UserSchema, {
        'create': UserCreateUpdate,
        'update': UserCreateUpdate,
    })
    permissions = defaultdict(lambda: is_superuser, {
        'list': is_customer,
    })
    service = user_service
    slug_field_type = int
```

### urls.py

```python
from example.app.view import UsersView
from fastapi_class_view.controller import APIController

app_router = APIController()

app_router.controller_register('/users/', UsersView())
```

### service.py

Service that uses the sqlalchemy model

```python
from example.database import UsersModel, Database
from fastapi_class_view.base import BaseService


class UserService(BaseService):
    model = UsersModel


user_service = UserService(Database().session)
```

### Result

Compact recording will allow you to automatically create crud operations with the model

![alt text](https://imageup.ru/img296/4446211/screenshot-from-2023-07-25-15-19-05.png)

<details>
<summary>Detailed view of the remaining application files</summary>

### permissions.py

Simple example is the creation of permits based on class HttpBearer

```python
from dataclasses import dataclass
from fastapi import Depends
from fastapi.security import HTTPBearer


@dataclass
class User:
    username: str
    is_superuser: bool


def is_superuser(creds=Depends(HTTPBearer())):
    """
    Check SuperUser by credentials
    :param creds:
    :return: UserModel
    """
    return User('admin', True)
```

### scheme.py

Pydantic Scheme

```python
from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str
```

SqlAlchemy model example

```python

class UsersModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(50))
    first_name = Column(VARCHAR(100))
    last_name = Column(VARCHAR(100))
```

###

</details>
