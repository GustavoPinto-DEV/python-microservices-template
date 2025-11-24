"""
Setup for repositorio_lib - Shared library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="repositorio_lib",
    version="1.0.0",
    description="Shared library for ecosystem projects",
    author="Gustavo Pinto",
    author_email="gpintov2001@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy==2.0.41",
        "asyncpg==0.30.0",
        "psycopg2-binary==2.9.10",
        "pydantic==2.11.7",
        "pydantic-settings==2.7.1",
        "python-jose[cryptography]==3.4.0",
        "passlib[bcrypt]==1.7.4",
        "httpx==0.28.1",
        "rut-chile==2.0.1",
    ],
    python_requires=">=3.12",
)
