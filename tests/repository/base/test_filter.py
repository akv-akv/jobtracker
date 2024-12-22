from datetime import datetime
from uuid import uuid4

import pytest

from src.core.repository.base.filter import ComparisonFilter, ComparisonOperator, Filter


# Test for Filter class
def test_filter_creation():
    filter_instance = Filter(field="name", values=["Alice", "Bob"])
    assert filter_instance.field == "name"
    assert filter_instance.values == ["Alice", "Bob"]


def test_filter_for_id():
    test_id = uuid4()
    filter_instance = Filter.for_id(test_id)
    assert filter_instance.field == "id"
    assert filter_instance.values == [test_id]


# Test for ComparisonFilter class
@pytest.mark.parametrize(
    "field, values, operator",
    [
        ("age", [30], ComparisonOperator.GT),
        ("score", [50], ComparisonOperator.LT),
        ("created_at", [datetime(2023, 1, 1)], ComparisonOperator.GE),
    ],
)
def test_comparison_filter_creation(field, values, operator):
    filter_instance = ComparisonFilter(field=field, values=values, operator=operator)
    assert filter_instance.field == field
    assert filter_instance.values == values
    assert filter_instance.operator == operator


@pytest.mark.parametrize(
    "values, raises_error",
    [
        ([30], False),
        ([30, 40], True),
    ],
)
def test_comparison_filter_verify_values(values, raises_error):
    filter_instance = ComparisonFilter(
        field="age", values=values, operator=ComparisonOperator.GT
    )
    if raises_error:
        with pytest.raises(
            ValueError, match="ComparisonFilter needs to have exactly one value"
        ):
            filter_instance.verify_no_operator_for_multiple_values()
    else:
        assert (
            filter_instance.verify_no_operator_for_multiple_values() == filter_instance
        )


# Test ComparisonOperator
@pytest.mark.parametrize(
    "operator, expected_value",
    [
        (ComparisonOperator.LT, "lt"),
        (ComparisonOperator.GE, "ge"),
        (ComparisonOperator.EQ, "eq"),
    ],
)
def test_comparison_operator(operator, expected_value):
    assert operator == expected_value
