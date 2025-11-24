# starlette
from starlette import status

# sqlalchemy
from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase, joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

# other
from typing import Type
from pydantic import BaseModel

# schema
from repositorio_lib.schema import Result

# logging
from repositorio_lib.core import logger


def get_pk_name(model: Type[DeclarativeBase]) -> str:
    """Get the primary key name from a database model"""
    pk_column = list(model.__table__.primary_key)[0]
    return pk_column.name


async def get_all_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    response_model: Type[BaseModel],
    relationships: list = None,
    use_selectinload: bool = False,
) -> Result:
    """
    Get all records with optional relationship loading.

    Args:
        db: Database session
        model: SQLAlchemy model class
        response_model: Pydantic schema for response
        relationships: List of relationships to eager load
        use_selectinload: If True, use selectinload (better for collections),
                         if False, use joinedload (better for single relationships)
    """
    try:
        stmt = select(model)
        if relationships:
            loader = selectinload if use_selectinload else joinedload
            for rel in relationships:
                stmt = stmt.options(loader(rel))
        result = await db.execute(stmt)
        data = result.scalars().unique().all()
    except Exception as e:
        logger.error(
            f"Error in get_all_async for model {model.__name__}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error retrieving records",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return Result(
            data=[response_model.model_validate(item) for item in data],
            message="Success",
            status=status.HTTP_200_OK,
        )


async def get_one_by_id_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    response_model: Type[BaseModel],
    id: int,
    relationships: list = None,
) -> Result:
    """
    Get one record by ID with optional relationship loading.

    Args:
        db: Database session
        model: SQLAlchemy model class
        response_model: Pydantic schema for response
        id: Primary key value
        relationships: List of relationships to eager load
    """
    try:
        pk_column = list(model.__table__.primary_key)[0]
        stmt = select(model).where(pk_column == id)
        if relationships:
            for rel in relationships:
                stmt = stmt.options(joinedload(rel))
        result = await db.execute(stmt)
        instance = result.unique().scalar_one_or_none()
        if not instance:
            return Result(
                message=f"Record with ID {id} not found",
                status=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        logger.error(
            f"Error in get_one_by_id_async for model {model.__name__} with id {id}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error retrieving ID {id}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return Result(
            data=response_model.model_validate(instance),
            message="Success",
            status=status.HTTP_200_OK,
        )


async def create_data_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    data: BaseModel,
    response_model: Type[BaseModel],
) -> Result:
    """
    Create a single record.

    Args:
        db: Database session
        model: SQLAlchemy model class
        data: Pydantic schema with data to create
        response_model: Pydantic schema for response
    """
    try:
        instance = model(**data.model_dump(exclude_unset=True))
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error in create_data_async for model {model.__name__}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error creating record",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return Result(
            data=response_model.model_validate(instance),
            status=status.HTTP_201_CREATED,
            message="Success",
        )


async def update_data_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    id: int,
    data: BaseModel,
    response_model: Type[BaseModel],
    relationships: list = None,
) -> Result:
    """
    Update a single record by ID.

    Args:
        db: Database session
        model: SQLAlchemy model class
        id: Primary key value
        data: Pydantic schema with data to update
        response_model: Pydantic schema for response
        relationships: List of relationships to eager load in response
    """
    try:
        instance = await db.get(model, id)
        if not instance:
            return Result(
                message=f"Record with ID {id} not found",
                status=status.HTTP_404_NOT_FOUND,
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)

        await db.commit()

        if relationships:
            pk_column = list(model.__table__.primary_key)[0]
            stmt = select(model).where(pk_column == id)
            for rel in relationships:
                stmt = stmt.options(joinedload(rel))
            result = await db.execute(stmt)
            instance = result.unique().scalar_one_or_none()
        else:
            await db.refresh(instance)

    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error in update_data_async for model {model.__name__} with id {id}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error updating record",
            status=status.HTTP_400_BAD_REQUEST,
        )
    else:
        return Result(
            data=response_model.model_validate(instance),
            message="Success",
            status=status.HTTP_200_OK,
        )


async def delete_data_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    id: int,
) -> Result:
    """
    Delete a single record by ID.

    Args:
        db: Database session
        model: SQLAlchemy model class
        id: Primary key value
    """
    try:
        instance = await db.get(model, id)
        if not instance:
            return Result(
                message=f"Record with ID {id} not found",
                status=status.HTTP_404_NOT_FOUND,
            )
        await db.delete(instance)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error in delete_data_async for model {model.__name__} with id {id}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error deleting record",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return Result(
            message=f"Record with ID {id} deleted successfully",
            status=status.HTTP_200_OK,
        )


async def bulk_create_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    data_list: list[BaseModel],
    response_model: Type[BaseModel],
) -> Result:
    """
    Bulk create multiple records in a single transaction.
    Much faster than multiple individual inserts.

    Args:
        db: Database session
        model: SQLAlchemy model class
        data_list: List of Pydantic schemas to create
        response_model: Pydantic schema for response

    Returns:
        Result with list of created instances
    """
    try:
        if not data_list:
            return Result(
                message="No records to create",
                status=status.HTTP_400_BAD_REQUEST,
            )

        instances = [model(**item.model_dump(exclude_unset=True)) for item in data_list]
        db.add_all(instances)
        await db.commit()

        pk_name = get_pk_name(model)
        ids = [getattr(inst, pk_name) for inst in instances]
        pk_column = getattr(model, pk_name)

        stmt = select(model).where(pk_column.in_(ids))
        result = await db.execute(stmt)
        refreshed_instances = result.scalars().all()

    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error in bulk_create_async for model {model.__name__}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error bulk creating records",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return Result(
            data=[response_model.model_validate(item) for item in refreshed_instances],
            status=status.HTTP_201_CREATED,
            message=f"{len(refreshed_instances)} records created successfully",
        )


async def bulk_update_async(
    db: AsyncSession,
    model: Type[DeclarativeBase],
    updates: list[dict],
) -> Result:
    """
    Bulk update multiple records efficiently using SQLAlchemy Core.
    Much faster than ORM-based updates for large datasets.

    Args:
        db: Database session
        model: SQLAlchemy model class
        updates: List of dicts with primary key and fields to update
                Example: [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Mary'}]

    Returns:
        Result with count of updated records
    """
    try:
        if not updates:
            return Result(
                message="No records to update",
                status=status.HTTP_400_BAD_REQUEST,
            )

        pk_name = get_pk_name(model)
        pk_column = getattr(model, pk_name)
        updated_count = 0

        for update_data in updates:
            record_id = update_data.pop(pk_name, None)
            if not record_id or not update_data:
                continue

            valid_updates = {
                key: value
                for key, value in update_data.items()
                if hasattr(model, key) and value is not None
            }

            if not valid_updates:
                continue

            stmt = update(model).where(pk_column == record_id).values(**valid_updates)
            result = await db.execute(stmt)
            updated_count += result.rowcount

        await db.commit()

    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error in bulk_update_async for model {model.__name__}: {str(e)}",
            exc_info=True,
        )
        return Result(
            message=f"Error bulk updating records",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        return Result(
            message=f"{updated_count} records updated successfully",
            status=status.HTTP_200_OK,
        )
