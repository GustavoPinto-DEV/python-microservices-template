"""Schemas for Web"""
from pydantic import BaseModel

class LoginForm(BaseModel):
    username: str
    password: str

# TODO: Add more schemas
