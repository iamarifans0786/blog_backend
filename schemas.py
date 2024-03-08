from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile


# pydentic models for blog
class Base(BaseModel):
    title: str
    subtitle: str
    desc: str
    # image: UploadFile


# pydentic models for showing blog
class Blog(Base):
    title: str
    subtitle: str
    desc: str
    image: str

    class Config:
        orm_mode = True


class UpdateBlog(Base):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    desc: Optional[str] = None
    image: Optional[str] = None

    class Config:
        orm_mode = True


# responce models for show users with all blog list
class ShowUser(BaseModel):
    name: str
    email: str
    blogs: List[Blog] = []

    class Config:
        orm_mode = True


# responce models for show users comments with all blog list
class ShowUser(BaseModel):
    id: int
    name: str
    email: str
    # blogs: List[Blog] = []

    class Config:
        orm_mode = True


# new
class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    creator: ShowUser
    # blog_id: int

    class Config:
        orm_mode = True


# pydentic models for user
class User(BaseModel):
    name: str
    email: str
    password: str


# responce models for show users with all blog list
class UpdateUser(BaseModel):
    name: str
    password: Optional[str] = None

    class Config:
        orm_mode = True


# pydentic models for showing user(creator)
class ShowCreator(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


# responce models for show blog with user(creator)
class ShowBlog(BaseModel):
    title: str
    desc: str
    subtitle: str
    image: str
    id: int
    creator: ShowCreator
    comments: List[Comment] = []

    class Config:
        orm_mode = True


# for the FastApi Swagger UI Login
# class Login(BaseModel):
#     username: str
#     password: str


# for the react app login
class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class DeleteResponse(BaseModel):
    message: str
    status: bool
