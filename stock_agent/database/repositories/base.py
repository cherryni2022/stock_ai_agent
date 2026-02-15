"""Generic async repository base class with common CRUD operations."""

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from stock_agent.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """通用 Repository 基类 — 封装常见 CRUD 操作.

    子类只需指定 `model` 类属性即可复用全部方法。

    Usage:
        class MyRepo(BaseRepository[MyModel]):
            model = MyModel
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---- Create ----

    async def add(self, entity: ModelT) -> ModelT:
        """Insert a single entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def add_many(self, entities: list[ModelT]) -> list[ModelT]:
        """Insert multiple entities."""
        self.session.add_all(entities)
        await self.session.flush()
        return entities

    # ---- Read ----

    async def get_by_id(self, pk: Any) -> ModelT | None:
        """Get a single entity by primary key."""
        return await self.session.get(self.model, pk)

    async def get_all(self, limit: int = 500, offset: int = 0) -> list[ModelT]:
        """Get all entities with pagination."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_filter(self, limit: int = 500, **filters: Any) -> list[ModelT]:
        """Get entities matching keyword filters.

        Usage:
            await repo.get_by_filter(ticker="AAPL", limit=100)
        """
        stmt = select(self.model)
        for col_name, value in filters.items():
            column = getattr(self.model, col_name, None)
            if column is not None:
                stmt = stmt.where(column == value)
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        """Count entities matching optional filters."""
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        for col_name, value in filters.items():
            column = getattr(self.model, col_name, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    # ---- Update ----

    async def update_by_id(self, pk: Any, **values: Any) -> None:
        """Update an entity by primary key."""
        # Determine PK column(s)
        pk_cols = [c for c in self.model.__table__.primary_key.columns]
        if len(pk_cols) == 1:
            stmt = update(self.model).where(pk_cols[0] == pk).values(**values)
        else:
            raise ValueError("update_by_id only supports single-column primary keys")
        await self.session.execute(stmt)

    # ---- Delete ----

    async def delete_by_id(self, pk: Any) -> None:
        """Delete an entity by primary key."""
        entity = await self.get_by_id(pk)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()

    async def delete_by_filter(self, **filters: Any) -> int:
        """Delete entities matching filters. Returns count of deleted rows."""
        stmt = delete(self.model)
        for col_name, value in filters.items():
            column = getattr(self.model, col_name, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
