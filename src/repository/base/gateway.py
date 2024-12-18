from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from src.domain.base.exceptions import DoesNotExist
from src.repository.base.filter import Filter
from src.repository.base.pagination import PageOptions


class Gateway(ABC):
    @abstractmethod
    async def add(self, item: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    async def update(
        self, item: dict[str, Any], if_unmodified_since: datetime | None = None
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def remove(self, id: UUID) -> bool:
        pass

    @abstractmethod
    async def filter(
        self, filters: list[Filter], params: PageOptions | None = None
    ) -> list[dict[str, Any]]:
        pass

    async def get(self, id: UUID) -> dict[str, Any] | None:
        result = await self.filter([Filter(field="id", values=[id])], params=None)
        return result[0] if result else None

    async def upsert(self, item: dict[str, Any]) -> dict[str, Any]:
        try:
            return await self.update(item)
        except DoesNotExist:
            return await self.add(item)

    async def count(self, filters: list[Filter]) -> int:
        return len(await self.filter(filters, params=None))

    async def exists(self, filters: list[Filter]) -> bool:
        return len(await self.filter(filters, params=PageOptions(limit=1))) > 0

    async def update_transactional(
        self, id: UUID, func: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> dict[str, Any]:
        raise NotImplementedError(
            f"{self.__class__} does not implement pessimistic concurrency control"
        )
