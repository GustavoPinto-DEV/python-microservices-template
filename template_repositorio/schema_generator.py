"""
Automated Schema Generator for Pydantic Schemas from SQLAlchemy Models

This script generates all schema-related files automatically from the SQLAlchemy
models defined in repositorio_lib.model.models:

- base_schema.py: Base Pydantic schemas with all model fields
- complete_schema.py: Extended schemas including relationship fields
- relationships.py: Relationship definitions for each model
- model_map.py: Mapping dictionary for dynamic model/schema lookups using dataclasses

Usage:
    python schema_generator.py

This should be run after regenerating models with sqlacodegen to keep schemas in sync.
"""

import inspect
from typing import get_args, get_origin
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import RelationshipProperty
from repositorio_lib.model.models import Base


def get_python_type_annotation(column):
    """Convert SQLAlchemy column type to Python type annotation string"""
    python_type = column.type.python_type

    # Handle Optional types
    if column.nullable:
        type_name = python_type.__name__

        # Special handling for common types
        if type_name == "Decimal":
            return "Optional[Decimal]"
        elif type_name == "datetime":
            return "Optional[datetime]"
        elif type_name == "list":
            return "Optional[list]"
        else:
            return f"Optional[{type_name}]"
    else:
        # Non-nullable types
        type_name = python_type.__name__

        if type_name == "Decimal":
            return "Decimal"
        elif type_name == "datetime":
            return "datetime"
        elif type_name == "list":
            return "list"
        else:
            return type_name


def get_model_name_to_schema_name(model_name):
    """Convert model name to schema name (e.g., TblUsuario -> TblUsuarioSchema)"""
    return f"{model_name}Schema"


def get_model_to_complete_schema_name(model_name):
    """Convert model name to complete schema name without Tbl/Nub prefix"""
    # Remove Tbl or Nub prefix
    if model_name.startswith("Tbl"):
        clean_name = model_name[3:]
    elif model_name.startswith("Nub"):
        clean_name = model_name[3:]
    else:
        clean_name = model_name

    return f"{clean_name}Schema"


def generate_base_schema():
    """Generate base_schema.py file with all base Pydantic schemas"""

    # Get all models from Base
    models = []
    for name, obj in inspect.getmembers(inspect.getmodule(Base)):
        if inspect.isclass(obj) and issubclass(obj, Base) and obj != Base:
            models.append((name, obj))

    # Start building the file content
    lines = [
        "# dates",
        "from datetime import datetime, time, date",
        "",
        "# other",
        "from pydantic import BaseModel, ConfigDict",
        "from typing import Optional",
        "from decimal import Decimal",
        "",
        "",
        "class BaseSchema(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
        "",
    ]

    # Generate schema for each model
    for model_name, model_class in sorted(models, key=lambda x: x[0]):
        schema_name = get_model_name_to_schema_name(model_name)
        lines.append(f"class {schema_name}(BaseSchema):")

        # Get model inspector
        mapper = sa_inspect(model_class)

        # Add all column fields
        has_fields = False
        for column in mapper.columns:
            field_name = column.name
            type_annotation = get_python_type_annotation(column)

            # Add default value for optional fields
            if column.nullable and not column.primary_key:
                lines.append(f"    {field_name}: {type_annotation} = None")
            else:
                lines.append(f"    {field_name}: {type_annotation}")

            has_fields = True

        # If no fields, add pass
        if not has_fields:
            lines.append("    pass")

        lines.append("")
        lines.append("")

    return "\n".join(lines)


def generate_relationships():
    """Generate relationships.py file with relationship definitions"""

    # Get all models from Base
    models = []
    for name, obj in inspect.getmembers(inspect.getmodule(Base)):
        if inspect.isclass(obj) and issubclass(obj, Base) and obj != Base:
            models.append((name, obj))

    # Start building the file content
    lines = [
        "from repositorio_lib.model.models import *",
        "",
    ]

    # Generate relationships for each model
    for model_name, model_class in sorted(models, key=lambda x: x[0]):
        mapper = sa_inspect(model_class)

        # Get all relationships
        relationships = []
        for prop in mapper.relationships:
            relationships.append(f"{model_class.__name__}.{prop.key}")

        # Generate variable name (convert to snake_case style)
        # TblUsuario -> tbl_usuario_relationships
        var_name = "".join(
            ["_" + c.lower() if c.isupper() else c for c in model_name]
        ).lstrip("_")
        var_name = f"{var_name}_relationships"

        # Add relationships list
        if relationships:
            lines.append(f"{var_name} = [")
            for rel in relationships:
                lines.append(f"    {rel},")
            lines.append("]")
        else:
            lines.append(f"{var_name} = []")

        lines.append("")

    return "\n".join(lines)


def generate_complete_schema():
    """Generate complete_schema.py file with extended schemas including relationships"""

    # Get all models from Base
    models = []
    for name, obj in inspect.getmembers(inspect.getmodule(Base)):
        if inspect.isclass(obj) and issubclass(obj, Base) and obj != Base:
            models.append((name, obj))

    # Start building the file content
    lines = [
        "# other",
        "from pydantic import Field",
        "from typing import Optional, List",
        "",
        "# schema",
        "from repositorio_lib.schema.base_schema import *",
        "",
        "",
    ]

    # Generate complete schema for each model
    for model_name, model_class in sorted(models, key=lambda x: x[0]):
        base_schema_name = get_model_name_to_schema_name(model_name)
        complete_schema_name = get_model_to_complete_schema_name(model_name)

        lines.append(f"class {complete_schema_name}({base_schema_name}):")

        # Get model inspector
        mapper = sa_inspect(model_class)

        # Add all relationship fields
        has_relationships = False
        for prop in mapper.relationships:
            has_relationships = True
            rel_key = prop.key

            # Get the related model class
            related_class = prop.mapper.class_
            related_schema = get_model_name_to_schema_name(related_class.__name__)

            # Determine if it's a list or single relationship
            # Check if it's a collection (one-to-many or many-to-many)
            if prop.uselist:
                # It's a list relationship
                lines.append(
                    f"    {rel_key}: List[{related_schema}] = Field(default_factory=list)"
                )
            else:
                # It's a single relationship
                # Check if nullable (optional)
                # Most foreign key relationships are optional unless specifically required
                nullable = True
                for column in mapper.columns:
                    for fk in column.foreign_keys:
                        if fk.column.table == prop.mapper.local_table:
                            nullable = column.nullable
                            break

                if nullable:
                    lines.append(f"    {rel_key}: Optional[{related_schema}] = None")
                else:
                    lines.append(f"    {rel_key}: {related_schema}")

        # If no relationships, add pass
        if not has_relationships:
            lines.append("    pass")

        lines.append("")
        lines.append("")

    return "\n".join(lines)


def get_model_map_key(model_name):
    """Convert model name to model_map key (snake_case without prefix)"""
    # Remove Tbl or Nub prefix
    if model_name.startswith("Tbl"):
        clean_name = model_name[3:]
    elif model_name.startswith("Nub"):
        clean_name = model_name[3:]
    else:
        clean_name = model_name

    # Convert to snake_case
    snake_case = "".join(
        ["_" + c.lower() if c.isupper() else c for c in clean_name]
    ).lstrip("_")
    return snake_case


def generate_model_map():
    """Generate model_map.py file with model mappings using dataclasses"""

    # Get all models from Base
    models = []
    for name, obj in inspect.getmembers(inspect.getmodule(Base)):
        if inspect.isclass(obj) and issubclass(obj, Base) and obj != Base:
            models.append((name, obj))

    # Start building the file content
    lines = [
        '"""',
        "Model Map: Dynamic mapping of models to schemas and relationships",
        "",
        "Uses dataclass for better structure and type safety.",
        '"""',
        "",
        "from dataclasses import dataclass",
        "from typing import Type, List, Any",
        "",
        "# model",
        "from repositorio_lib.model.models import *",
        "",
        "# schema",
        "from repositorio_lib.schema.base_schema import *",
        "from repositorio_lib.schema.complete_schema import *",
        "from repositorio_lib.schema.relationships import *",
        "",
        "# project",
        "from repositorio_lib.core.crud_helpers import get_pk_name",
        "",
        "",
        "@dataclass",
        "class ModelMapEntry:",
        '    """Structure for model map entries"""',
        "    pk_name: str",
        "    model: Type[Any]",
        "    base_schema: Type[BaseSchema]",
        "    complete_schema: Type[BaseSchema]",
        "    relationships: List[Any]",
        "",
        "    def get_schema(self, with_rels=True):",
        "        return self.complete_schema if with_rels else self.base_schema",
        "",
        "    def get_rels(self, with_rels=True):",
        "        return self.relationships if with_rels else []",
        "",
        "",
        "model_map: dict[str, ModelMapEntry] = {",
    ]

    # Generate model_map entries for each model
    for model_name, model_class in sorted(models, key=lambda x: x[0]):
        map_key = get_model_map_key(model_name)
        complete_schema_name = get_model_to_complete_schema_name(model_name)

        # Generate base schema name (model name + Schema)
        base_schema_name = f"{model_name}Schema"

        # Generate relationship variable names
        var_name = "".join(
            ["_" + c.lower() if c.isupper() else c for c in model_name]
        ).lstrip("_")
        relationships_var = f"{var_name}_relationships"

        lines.append(f'    "{map_key}": ModelMapEntry(')
        lines.append(f"        pk_name=get_pk_name({model_name}),")
        lines.append(f"        model={model_name},")
        lines.append(f"        base_schema={base_schema_name},")
        lines.append(f"        complete_schema={complete_schema_name},")
        lines.append(f"        relationships={relationships_var},")
        lines.append("    ),")

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main function to generate all schema files"""
    print("=" * 70)
    print("SCHEMA GENERATOR - Automated Pydantic Schema Generation")
    print("=" * 70)
    print("\nStarting schema generation...")

    # Generate base_schema.py
    print("\n[1/4] Generating base_schema.py...")
    base_schema_content = generate_base_schema()
    with open("repositorio_lib/schema/base_schema.py", "w", encoding="utf-8") as f:
        f.write(base_schema_content)
    print("      [OK] base_schema.py generated")

    # Generate relationships.py
    print("\n[2/4] Generating relationships.py...")
    relationships_content = generate_relationships()
    with open("repositorio_lib/schema/relationships.py", "w", encoding="utf-8") as f:
        f.write(relationships_content)
    print("      [OK] relationships.py generated")

    # Generate complete_schema.py
    print("\n[3/4] Generating complete_schema.py...")
    complete_schema_content = generate_complete_schema()
    with open("repositorio_lib/schema/complete_schema.py", "w", encoding="utf-8") as f:
        f.write(complete_schema_content)
    print("      [OK] complete_schema.py generated")

    # Generate model_map.py
    print("\n[4/4] Generating model_map.py...")
    model_map_content = generate_model_map()
    with open("repositorio_lib/schema/model_map.py", "w", encoding="utf-8") as f:
        f.write(model_map_content)
    print("      [OK] model_map.py generated")

    print("\n" + "=" * 70)
    print("[SUCCESS] All schema files generated successfully!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  1. repositorio_lib/schema/base_schema.py")
    print("  2. repositorio_lib/schema/relationships.py")
    print("  3. repositorio_lib/schema/complete_schema.py")
    print("  4. repositorio_lib/schema/model_map.py")
    print("\nModelMapEntry dataclass structure:")
    print("  - pk_name: str                 # Primary key field name")
    print("  - model: Type[Any]             # SQLAlchemy model")
    print("  - base_schema: Type            # Base schema without relationships")
    print("  - complete_schema: Type        # Schema with all relationships")
    print("  - relationships: List[Any]     # All relationships list")
    print("\nModelMapEntry methods:")
    print(
        "  - get_schema(with_rels=False)  # Returns complete_schema if True, else base_schema"
    )
    print("  - get_rels(with_rels=False)    # Returns relationships if True, else []")
    print("\nUsage:")
    print("  entry = model_map['paciente']")
    print("  entry.pk_name                  # 'pac_id'")
    print("  entry.model                    # TblPaciente")
    print("  entry.get_schema()             # TblPacienteSchema (base)")
    print("  entry.get_schema(with_rels=True)  # PacienteSchema (complete)")
    print("  entry.get_rels(with_rels=True)    # [relationships list]")
    print("=" * 70)


if __name__ == "__main__":
    main()
