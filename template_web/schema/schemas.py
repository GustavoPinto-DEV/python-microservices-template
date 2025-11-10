"""Schemas para Web"""
from pydantic import BaseModel

class LoginForm(BaseModel):
    username: str
    password: str

# TODO: Agregar más schemas
