from enum import Enum
from typing import Any
from uuid import UUID

from src.core.domain.value_object import ValueObject


class Filter(ValueObject):
    field: str
    values: list[Any]

    @classmethod
    def for_id(cls, id: UUID) -> "Filter":
        return cls(field="id", values=[id])


class ComparisonOperator(str, Enum):
    LT = "lt"
    LE = "le"
    GE = "ge"
    GT = "gt"
    EQ = "eq"
    NE = "ne"


class ComparisonFilter(Filter):
    operator: ComparisonOperator

    def verify_no_operator_for_multiple_values(self):
        if len(self.values) != 1:
            raise ValueError("ComparisonFilter needs to have exactly one value")
        return self
