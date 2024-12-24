from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel

# Generic type variables
T = TypeVar("T", bound="ValueObject")


class ValidationError(TypeError):
    """Raised when validation fails for a ValueObject."""


class ValueObject(BaseModel):
    """
    Types that have no identity (these are just complex values like a datetime).
    """

    @classmethod
    def create(cls: Type[T], **values: Any) -> T:
        """
        Factory method to create a ValueObject
        """
        return cls(**values)

    def update(self: T, **values: Dict[str, Any]) -> T:
        """
        Updates the ValueObject by returning a new instance with modified values.
        Performs validation on the updated values.
        """
        # Merge the current instance's data with the updates
        updated_data = {**self.model_dump(), **values}
        # Validate and create a new instance
        return self.__class__(**updated_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ValueObject to a dictionary."""
        return self.model_dump()

    def __hash__(self):
        """Allow ValueObject to be used in sets or as dict keys."""
        return hash(self.__class__) + hash(tuple(self.dict().values()))
