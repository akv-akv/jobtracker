from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from src.domain.base.exceptions import DoesNotExist
from src.domain.base.value_object import ValueObject
from src.repository.base.filter import Filter
from src.repository.base.gateway import Gateway
from src.repository.base.pagination import Page, PageOptions

# Type variable to represent the entity type (bound to ValueObject)
T = TypeVar("T", bound=ValueObject)


class Repository(Generic[T]):
    entity: type[T]  # The entity type this repository manages

    def __init__(self, gateway: Gateway):
        self.gateway = gateway

    def __init_subclass__(cls) -> None:
        # Dynamically bind the entity type to the subclass
        (base,) = cls.__orig_bases__  # type: ignore
        (entity,) = base.__args__
        super().__init_subclass__()
        cls.entity = entity

    async def all(self, params: PageOptions | None = None) -> Page[T]:
        # Fetch all records with optional pagination
        return await self.filter([], params=params)

    async def by(
        self, key: str, value: Any, params: PageOptions | None = None
    ) -> Page[T]:
        # Fetch records by a specific field and value
        return await self.filter([Filter(field=key, values=[value])], params=params)

    async def filter(
        self, filters: list[Filter], params: PageOptions | None = None
    ) -> Page[T]:
        # Apply filters and fetch paginated records
        records = await self.gateway.filter(filters, params=params)
        total = len(records)

        # Adjust total count for pagination if necessary
        if params is not None and not (params.offset == 0 and total < params.limit):
            total = await self.count(filters)

        return Page(
            total=total,
            limit=params.limit if params else None,
            offset=params.offset if params else None,
            items=[self.entity(**x) for x in records],
        )

    async def get(self, id: UUID) -> T:
        # Fetch a single record by ID
        res = await self.gateway.get(id)
        if res is None:
            raise DoesNotExist("object", id)
        return self.entity(**res)

    async def add(self, item: T | dict[str, Any]) -> T:
        # Add a new record to the database
        if isinstance(item, dict):
            item = self.entity.create(**item)  # Convert dict to entity
        created = await self.gateway.add(
            vars(item)
        )  # Use vars() to dump entity to dict
        return self.entity(**created)

    async def update(
        self, id: UUID, values: dict[str, Any], optimistic: bool = True
    ) -> T:
        # Update an existing record with optional optimistic locking
        if not values:
            return await self.get(id)
        if optimistic:
            existing = await self.get(id)
            updated_at = getattr(existing, "updated_at", None)
            if not isinstance(updated_at, datetime):
                raise ValueError(
                    "Can't use optimistic locking on object without updated_at datetime"
                )
            updated = await self.gateway.update(
                vars(existing.update(**values)), if_unmodified_since=updated_at
            )
        else:
            updated = await self.gateway.update_transactional(
                id, lambda x: vars(self.entity(**x).update(**values))
            )
        return self.entity(**updated)

    async def upsert(self, item: T) -> T:
        # Insert or update a record
        values = vars(item)  # Convert entity to dict
        upserted = await self.gateway.upsert(values)
        return self.entity(**upserted)

    async def remove(self, id: UUID) -> bool:
        # Remove a record by ID
        return await self.gateway.remove(id)

    async def count(self, filters: list[Filter]) -> int:
        # Count records matching the given filters
        return await self.gateway.count(filters)

    async def exists(self, filters: list[Filter]) -> bool:
        # Check if any records match the given filters
        return await self.gateway.exists(filters)
