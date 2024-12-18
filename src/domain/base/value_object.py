from dataclasses import dataclass, replace
from typing import Any, Dict, TypeVar

# Generic type variables
T = TypeVar("T", bound="ValueObject")


@dataclass
class ValueObject:
    """
    Types that have no identity (these are just complex values like a datetime).
    """

    @classmethod
    def create(cls: type[T], **values: Any) -> T:
        """
        Factory method to create a ValueObject
        """
        try:
            return cls(**values)
        except TypeError as e:
            raise Exception(f"Invalid fields: {e}")

    def update(self: T, **values: Dict[str, Any]) -> T:
        """
        Updates the ValueObject by returning a new instance with modified values.
        """
        return replace(self, **values)
