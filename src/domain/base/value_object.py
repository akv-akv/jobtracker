from dataclasses import dataclass, replace
from typing import Any, Dict, TypeVar, get_type_hints

# Generic type variables
T = TypeVar("T", bound="ValueObject")


class ValidationError(TypeError):
    """Raised when validation fails for a ValueObject."""


@dataclass(frozen=True)
class ValueObject:
    """
    Types that have no identity (these are just complex values like a datetime).
    """

    @classmethod
    def _validate_types(cls, values: Dict[str, Any]) -> None:
        """
        Validates the types of provided values against the type annotations.
        """
        annotations = get_type_hints(cls)  # More robust than __annotations__
        for field_name, field_value in values.items():
            if field_name in annotations and not isinstance(
                field_value, annotations[field_name]
            ):
                raise ValidationError(
                    f"Invalid type for field '{field_name}': "
                    f"Expected {annotations[field_name]}, got {type(field_value)}"
                )

    @classmethod
    def create(cls: type[T], **values: Any) -> T:
        """
        Factory method to create a ValueObject
        """
        try:
            cls._validate_types(values)
            return cls(**values)
        except TypeError as e:
            raise ValidationError(f"Invalid fields or missing arguments: {e}") from e

    def update(self: T, **values: Dict[str, Any]) -> T:
        """
        Updates the ValueObject by returning a new instance with modified values.
        """
        if not values:  # No updates provided
            return self

        self._validate_types(values)
        return replace(self, **values)
