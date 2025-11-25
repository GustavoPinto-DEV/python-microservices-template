"""Repository - Data access layer"""

from starlette import status
from repositorio_lib.schema.result import Result
from repositorio_lib.core import (
    get_db_context,
    log_performance,
)
from repositorio_lib.utils import (
    get_all_async,
    get_one_by_id_async,
    bulk_create_async,
    bulk_update_async,
)
from repositorio_lib.schema.model_map import model_map
from repositorio_lib.config import cache, logger


class v1Repository:
    """Main repository with generic CRUD operations"""

    # region Generic Functions
    async def get_all(
        self,
        model_name: str,
        use_relationships: bool = True,
        use_cache: bool = False,
        ttl_seconds: int = 300,
    ) -> Result:
        """
        Get all records for a model.

        Args:
            model_name: Model name key in model_map (e.g., "users", "products")
            use_relationships: If True, includes related models in response
            use_cache: If True, uses cache for faster repeated queries
            ttl_seconds: Cache time-to-live in seconds (default: 300)

        Returns:
            Result: Object with data, message and status
        """
        cache_key = f"get_all:{model_name}"

        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_result
            logger.debug(f"Cache MISS: {cache_key}")

        if model_name not in model_map:
            return Result(
                message=f"Model '{model_name}' is not registered.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cfg = model_map[model_name]
        model = cfg.model
        schema = cfg.get_schema(use_relationships)
        rels = cfg.get_rels(use_relationships)

        with log_performance(
            logger, f"DB Query: get_all({model_name})", threshold_ms=500
        ):
            async with get_db_context() as db:
                result = await get_all_async(db, model, schema, rels)

        if use_cache and result.status == status.HTTP_200_OK:
            cache.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl_seconds}s)")
        return result

    async def get_one_by_id(
        self,
        model_name: str,
        id: int,
        use_relationships: bool = True,
        use_cache: bool = False,
        ttl_seconds: int = 300,
    ) -> Result:
        """
        Get one record by ID.

        Args:
            model_name: Model name key in model_map
            id: Primary key value
            use_relationships: If True, includes related models in response
            use_cache: If True, uses cache for faster repeated queries
            ttl_seconds: Cache time-to-live in seconds (default: 300)

        Returns:
            Result: Object with data, message and status
        """
        cache_key = f"get_one:{model_name}:{id}"

        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_result
            logger.debug(f"Cache MISS: {cache_key}")

        if model_name not in model_map:
            return Result(
                message=f"Model '{model_name}' is not registered.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cfg = model_map[model_name]
        model = cfg.model
        schema = cfg.get_schema(use_relationships)
        rels = cfg.get_rels(use_relationships)

        with log_performance(
            logger, f"DB Query: get_one({model_name}, id={id})", threshold_ms=200
        ):
            async with get_db_context() as db:
                result = await get_one_by_id_async(db, model, schema, id, rels)

        if use_cache and result.status == status.HTTP_200_OK:
            cache.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl_seconds}s)")

        return result

    async def bulk_create(self, model_name: str, data_list: list) -> Result:
        """
        Bulk create multiple records efficiently.

        Args:
            model_name: Model name key in model_map
            data_list: List of dictionaries or Pydantic models to create

        Returns:
            Result: Object with created records, message and status
        """
        if model_name not in model_map:
            return Result(
                message=f"Model '{model_name}' is not registered.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cfg = model_map[model_name]
        model = cfg.model
        base_schema = cfg.base_schema

        record_count = len(data_list)
        with log_performance(
            logger,
            f"DB Bulk Create: {model_name} ({record_count} records)",
            threshold_ms=1000,
        ):
            async with get_db_context() as db:
                result = await bulk_create_async(db, model, data_list, base_schema)

        return result

    async def bulk_update(self, model_name: str, updates: list[dict]) -> Result:
        """
        Bulk update multiple records efficiently.

        Args:
            model_name: Model name key in model_map
            updates: List of dicts with primary key and fields to update
                    Example: [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Mary'}]

        Returns:
            Result: Object with update count, message and status
        """

        if model_name not in model_map:
            return Result(
                message=f"Model '{model_name}' is not registered.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cfg = model_map[model_name]
        model = cfg.model

        update_count = len(updates)
        with log_performance(
            logger,
            f"DB Bulk Update: {model_name} ({update_count} records)",
            threshold_ms=1000,
        ):
            async with get_db_context() as db:
                result = await bulk_update_async(db, model, updates)

        return result

    # endregion
