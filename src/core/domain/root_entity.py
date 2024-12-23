from __future__ import annotations  # For Python 3.8-3.9 compatibility with annotations

import uuid
from datetime import datetime, timezone
from typing import Type, TypeVar
from uuid import UUID

from pydantic import Field

from src.core.domain.value_object import ValueObject

T = TypeVar("T", bound="RootEntity")


def now():
    return datetime.now(timezone.utc)


class RootEntity(ValueObject):
    """
    Types that have an identity.
    All attributes of an instance may change,
    but the instance is still the same.
    Entities have an id and default fields
    associated with state changes (created_at, updated_at).
    """

    id: UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)

    @classmethod
    def create(cls: Type[T], **values) -> T:
        """
        Factory method to create a new instance of the entity.
        Ensures defaults for `id`, `created_at`, and `updated_at`.
        """
        values.setdefault("id", uuid.uuid4())
        values.setdefault("created_at", now())
        values.setdefault("updated_at", values["created_at"])
        return super().create(**values)

    def update(self: T, **values) -> T:
        """
        Updates the entity with new values.
        Enforces immutability by returning a new instance.
        """
        if "id" in values and values["id"] != self.id:
            raise ValueError("Cannot change the id of an entity")
        if "created_at" in values:
            raise ValueError("Cannot change the created_at timestamp")
        values.setdefault("updated_at", now())
        return super().update(**values)

    def __hash__(self):
        """
        Custom hash function to ensure the entity
        can be used in sets or as a dictionary key.
        """
        return hash(self.__class__) + hash(self.id)
