"""Schema Result para respuestas estandarizadas"""
from pydantic import BaseModel
from typing import Any, Optional

class Result(BaseModel):
    """Wrapper estándar para respuestas"""
    data: Optional[Any] = None
    message: str = "Éxito"
    status: int = 200

    class Config:
        arbitrary_types_allowed = True
