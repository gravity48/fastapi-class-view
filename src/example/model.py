from sqlalchemy import VARCHAR, Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UsersModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(VARCHAR(50))
    first_name = Column(VARCHAR(100))
    last_name = Column(VARCHAR(100))
