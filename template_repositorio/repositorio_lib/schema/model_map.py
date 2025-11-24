"""
Model Map: Dynamic mapping of models to schemas and relationships

Uses dataclass for better structure and type safety.
"""

from dataclasses import dataclass
from typing import Type, List, Any

# model
from repositorio_lib.model.models import *

# schema
from repositorio_lib.schema.base_schema import *
from repositorio_lib.schema.complete_schema import *
from repositorio_lib.schema.relationships import *

# project
from repositorio_lib.core.crud_helpers import get_pk_name


@dataclass
class ModelMapEntry:
    """Structure for model map entries"""
    pk_name: str
    model: Type[Any]
    base_schema: Type[BaseSchema]
    complete_schema: Type[BaseSchema]
    relationships: List[Any]

    def get_schema(self, with_rels=True):
        return self.complete_schema if with_rels else self.base_schema

    def get_rels(self, with_rels=True):
        return self.relationships if with_rels else []


model_map: dict[str, ModelMapEntry] = {
    "base": ModelMapEntry(
        pk_name=get_pk_name(TblBase),
        model=TblBase,
        base_schema=TblBaseSchema,
        complete_schema=BaseSchema,
        relationships=tbl_base_relationships,
    ),
}
