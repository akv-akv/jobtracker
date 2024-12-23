from typing import Optional

import pytest
from pydantic import ValidationError

from src.core.domain.value_object import ValueObject


class Color(ValueObject):
    name: str
    code: int
    is_primary: bool
    description: Optional[str] = None
    hex_code: Optional[str] = None


@pytest.fixture
def color():
    return Color(
        name="green",
        code=42,
        is_primary=True,
        description="A primary color",
        hex_code="#00FF00",
    )


@pytest.mark.parametrize(
    "input_values,expected_values",
    [
        (
            {
                "name": "green",
                "code": 42,
                "is_primary": True,
                "description": "A primary color",
                "hex_code": "#00FF00",
            },
            {
                "name": "green",
                "code": 42,
                "is_primary": True,
                "description": "A primary color",
                "hex_code": "#00FF00",
            },
        ),
        (
            {"name": "blue", "code": 100, "is_primary": False},
            {
                "name": "blue",
                "code": 100,
                "is_primary": False,
                "description": None,
                "hex_code": None,
            },
        ),
    ],
)
def test_create_success(input_values, expected_values):
    color = Color.create(**input_values)
    for field, value in expected_values.items():
        assert getattr(color, field) == value


@pytest.mark.parametrize(
    "invalid_input,error_message",
    [
        (
            {"name": "green", "code": "invalid", "is_primary": True},
            "1 validation error for Color\ncode\n  "
            "Input should be a valid integer, unable to parse string as an integer",
        ),
        (
            {"name": "green", "is_primary": True},
            "1 validation error for Color\ncode\n  Field required",
        ),
    ],
)
def test_create_invalid(invalid_input, error_message):
    with pytest.raises(ValidationError) as e:
        Color.create(**invalid_input)
    assert error_message in str(e.value)


def test_update_single_field(color):
    updated = color.update(name="blue")
    assert updated.name == "blue"
    assert updated.code == color.code
    assert updated.description == color.description


def test_update_multiple_fields(color):
    updated = color.update(
        name="blue", description="A secondary color", hex_code="#0000FF"
    )
    assert updated.name == "blue"
    assert updated.description == "A secondary color"
    assert updated.hex_code == "#0000FF"


def test_update_optional_field_to_none(color):
    updated = color.update(description=None)
    assert updated.description is None


@pytest.mark.parametrize(
    "field,invalid_value,expected_message",
    [
        ("name", 123, "Input should be a valid string"),
        ("code", "invalid", "Input should be a valid integer"),
        ("is_primary", "aaa", "Input should be a valid boolean"),
    ],
)
def test_update_wrong_type(color, field, invalid_value, expected_message):
    with pytest.raises(ValidationError) as e:
        color.update(**{field: invalid_value})
    assert expected_message in str(e.value)


def test_update_no_change(color):
    updated = color.update()
    assert updated == color


def test_hashable(color):
    updated = color.update(name="blue")
    assert len({color, updated}) == 2


def test_eq(color):
    assert color == Color(
        name="green",
        code=42,
        is_primary=True,
        description="A primary color",
        hex_code="#00FF00",
    )


def test_neq(color):
    assert color != Color(
        name="blue",
        code=42,
        is_primary=True,
        description="A primary color",
        hex_code="#00FF00",
    )
