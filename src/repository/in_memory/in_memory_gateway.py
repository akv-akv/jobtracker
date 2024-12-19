from collections.abc import Callable
from copy import deepcopy
from datetime import datetime
from typing import Any
from uuid import UUID

from src.domain.base.exceptions import AlreadyExists, Conflict, DoesNotExist
from src.repository.base.filter import Filter
from src.repository.base.gateway import Gateway
from src.repository.base.pagination import PageOptions


class InMemoryGateway(Gateway):
    def __init__(self, data: list[dict[str, Any]]):
        self.data = {x["id"]: deepcopy(x) for x in data}

    def _get_next_id(self) -> int:
        if len(self.data) == 0:
            return 1
        else:
            return max(self.data) + 1

    def _paginate(
        self, objs: list[dict[str, Any]], params: PageOptions
    ) -> list[dict[str, Any]]:
        objs = sorted(
            objs,
            key=lambda x: (x.get(params.order_by) is None, x.get(params.order_by)),
            reverse=not params.ascending,
        )
        return objs[params.offset : params.offset + params.limit]

    async def filter(
        self, filters: list[Filter], params: PageOptions | None = None
    ) -> list[dict[str, Any]]:
        result = []
        for x in self.data.values():
            for filter in filters:
                if x.get(filter.field) not in filter.values:
                    break
            else:
                result.append(deepcopy(x))
        if params is not None:
            result = self._paginate(result, params)
        return result

    async def add(self, item: dict[str, Any]) -> dict[str, Any]:
        item = item.copy()
        id_ = item.pop("id", None)
        # autoincrement (like SQL does)
        if id_ is None:
            id_ = self._get_next_id()
        elif id_ in self.data:
            raise AlreadyExists(id_)

        self.data[id_] = {"id": id_, **item}
        return deepcopy(self.data[id_])

    async def update(
        self, item: dict[str, Any], if_unmodified_since: datetime | None = None
    ) -> dict[str, Any]:
        _id = item.get("id")
        if _id is None or _id not in self.data:
            raise DoesNotExist("item", _id)
        existing = self.data[_id]
        if if_unmodified_since and existing.get("updated_at") != if_unmodified_since:
            raise Conflict()
        existing.update(item)
        return deepcopy(existing)

    async def remove(self, id: UUID) -> bool:
        if id not in self.data:
            return False
        del self.data[id]
        return True

    async def update_transactional(
        self, id: UUID, func: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> dict[str, Any]:
        existing = await self.get(id)
        if existing is None:
            raise DoesNotExist("record", id)
        return await self.update(
            func(existing), if_unmodified_since=existing["updated_at"]
        )
