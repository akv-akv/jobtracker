from __future__ import annotations  # For Python 3.8-3.9 compatibility with annotations

import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Type, TypeVar
from uuid import UUID

from src.domain.base.value_object import ValueObject

T = TypeVar("T", bound="RootEntity")


def now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class RootEntity(ValueObject):
    """
    Types that have an identity.
    All attributes of an instance may change,
    but the instance is still the same.
    Entities have an id and default fields
    associated with state changes (created_at, updated_at).
    """

    id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls: Type[T], **values) -> T:
        """
        Factory method to create a new instance of the entity.
        Ensures defaults for `id`, `created_at`, and `updated_at`.
        """
        if "id" not in values or values["id"] is None:
            values["id"] = uuid.uuid4()
        values.setdefault("created_at", now())
        values.setdefault("updated_at", values["created_at"])
        cls._validate_types(values)
        return cls(**values)

    def update(self: T, **values) -> T:
        """
        Updates the entity with new values.
        Enforces immutability by returning a new instance.
        """
        if "id" in values and self.id is not None and values["id"] != self.id:
            raise Exception("Cannot change the id of an entity")
        if "created_at" in values:
            raise Exception("Cannot change the created_at timestamp")
        values.setdefault("updated_at", now())
        self._validate_types(values)
        return replace(self, **values)

    def __hash__(self):
        """
        Custom hash function to ensure the entity
        can be used in sets or as a dictionary key.
        """
        assert self.id is not None, "id must be set before hashing"
        return hash(self.__class__) + hash(self.id)
