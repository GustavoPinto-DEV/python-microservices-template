"""
Setup para repositorio_lib - Librería compartida
"""

from setuptools import setup, find_packages

setup(
    name="repositorio_lib",
    version="1.0.0",
    description="Librería compartida para proyectos del ecosistema",
    author="Tu Nombre",
    author_email="tu@email.com",
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
        "python-dotenv==1.0.1",
    ],
    python_requires=">=3.12",
)
