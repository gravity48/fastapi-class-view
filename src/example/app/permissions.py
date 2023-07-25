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


def is_customer(creds=Depends(HTTPBearer())):
    """
    Check CustomerUser by credentials
    :param creds:
    :return:
    """
    return User('user', False)
