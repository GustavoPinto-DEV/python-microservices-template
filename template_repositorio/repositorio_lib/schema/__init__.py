"""
Schema module for repositorio_lib.

Contains Pydantic schemas, result objects, and model mappings.
"""

# result
from .result import Result, ServicesResult

__all__ = ["Result", "ServicesResult"]
