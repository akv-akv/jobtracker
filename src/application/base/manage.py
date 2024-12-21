from typing import Any, Generic, List, TypeVar
from uuid import UUID

import backoff

from src.domain.base.exceptions import Conflict
from src.domain.base.root_entity import RootEntity
from src.repository.base.filter import Filter
from src.repository.base.pagination import Page, PageOptions
from src.repository.base.repository import Repository

T = TypeVar("T", bound=RootEntity)


class Manage(Generic[T]):
    repo: Repository[T]
    entity: type[T]

    def __init__(self, repo: Repository[T] | None = None):
        assert repo is not None
        self.repo = repo

    def __init_subclass__(cls) -> None:
        (base,) = cls.__orig_bases__  # type: ignore
        (entity,) = base.__args__
        assert issubclass(entity, RootEntity)
        super().__init_subclass__()
        cls.entity = entity

    async def retrieve(self, id: UUID) -> T:
        return await self.repo.get(id)

    async def create(self, values: dict[str, Any]) -> T:
        """Accepts values that should match entity attribute types"""
        return await self.repo.add(values)

    async def update(
        self, id: UUID, values: dict[str, Any], retry_on_conflict: bool = True
    ) -> T:
        """This update has a built-in retry function that can be switched off.

        This because some gateways (SQLGateway, ApiGateway) may raise Conflict
        errors in case there are concurrency issues. The backoff strategy assumes that
        we can retry immediately (because the conflict is gone immediately), but it
        does add some jitter between 0 and 200 ms to avoUUID many competing processes.

        If the repo.update is not UUIDempotent (which is atypical), retries should be
        switched off.
        """
        if retry_on_conflict:
            return await self._update_with_retries(id, values)
        else:
            return await self.repo.update(id, values)

    @backoff.on_exception(backoff.constant, Conflict, max_tries=10, interval=0.2)
    async def _update_with_retries(self, id: UUID, values: dict[str, Any]) -> T:
        return await self.repo.update(id, values)

    async def destroy(self, id: UUID) -> bool:
        return await self.repo.remove(id)

    async def list(self, params: PageOptions | None = None) -> Page[T]:
        return await self.repo.all(params)

    async def by(
        self, key: str, value: Any, params: PageOptions | None = None
    ) -> Page[T]:
        return await self.repo.by(key, value, params=params)

    async def filter(
        self, filters: List[Filter], params: PageOptions | None = None
    ) -> Page[T]:
        return await self.repo.filter(filters, params=params)

    async def count(self, filters: List[Filter]) -> int:
        return await self.repo.count(filters)

    async def exists(self, filters: List[Filter]) -> bool:
        return await self.repo.exists(filters)
