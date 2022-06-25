from datetime import datetime
from typing import Union
from sqlmodel import Field, Relationship, SQLModel
# from sqlalchemy import UniqueConstraint

class Url(SQLModel, table=True):
  short_url: int
  original_url: str = Field(default=..., primary_key=True)

class Hero(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Union[int, None] = Field(default=None, index=True)

class User(SQLModel, table=True):
  id: Union[int, None] = Field(default=None, primary_key=True)
  username: str

  exercises: list["Exercise"] = Relationship(back_populates="user")

class Exercise(SQLModel, table=True):
  id: Union[int, None] = Field(default=None, primary_key=True)
  description: Union[str, None]
  duration: Union[int, None] = 0
  date: str

  user_id: int | None = Field(default=None, foreign_key="user.id")
  user: User | None = Relationship(back_populates="exercises")