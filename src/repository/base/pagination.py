from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PageOptions:
    limit: int
    offset: int = 0
    order_by: str = "created_at"
    ascending: bool = False
    cursor: datetime | None = None


@dataclass
class Page(Generic[T]):
    total: int
    items: Sequence[T]
    limit: int | None = None
    offset: int | None = None
