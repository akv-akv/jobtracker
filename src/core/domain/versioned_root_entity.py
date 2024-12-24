from __future__ import annotations  # For Python 3.8-3.9 compatibility with annotations

from datetime import datetime, timezone
from typing import Type, TypeVar

from pydantic import Field

from src.core.domain.root_entity import RootEntity

T = TypeVar("T", bound="VersionedRootEntity")


def now():
    return datetime.now(timezone.utc)


class VersionedRootEntity(RootEntity):
    version: int = Field(default=1)

    @classmethod
    def create(cls: Type[T], **values) -> T:
        """
        Factory method to create a new instance of the entity.
        Extends `RootEntity.create` to include versioning.
        """
        values.setdefault("version", 1)  # Default version to 1
        return super().create(**values)  # Call parent method

    def update(self: T, **values) -> T:
        """
        Updates the entity with new values.
        Extends `RootEntity.update` to handle version incrementing.
        """
        if "id" in values and values["id"] != self.id:
            raise ValueError("Cannot change the id of an entity")
        if "created_at" in values:
            raise ValueError("Cannot change the created_at timestamp")
        values["version"] = self.version + 1
        # Use parent `update` to handle common behavior, extend with version
        return super().update(**values)

    def __hash__(self):
        """
        Custom hash function to ensure the entity
        can be used in sets or as a dictionary key.
        """
        return hash(self.__class__) + hash(self.id)
