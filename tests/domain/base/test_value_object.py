from dataclasses import dataclass

import pytest

from src.domain.base.value_object import ValueObject


@dataclass(frozen=True)
class Color(ValueObject):
    name: str


@pytest.fixture
def color():
    return Color(name="green")


def test_create_success():
    color = Color.create(name="green")
    assert isinstance(color, Color)
    assert color.name == "green"


def test_create_invalid_field():
    with pytest.raises(TypeError) as e:
        Color.create(name=123)  # Invalid type for `name`
    assert "Invalid type" in str(e.value)


def test_create_missing_field():
    with pytest.raises(TypeError) as e:
        Color.create()  # Missing required `name` field
    assert "missing 1 required positional argument: 'name'" in str(e.value)


def test_update(color):
    updated = color.update(name="red")

    assert color.name == "green"
    assert updated.name == "red"


def test_update_wrong_type(color):
    with pytest.raises(TypeError) as e:
        color.update(name=123)

    assert "Invalid type for field 'name'" in str(e.value)
    assert color.name == "green"


def test_hashable(color):
    assert len({color, color}) == 1


def test_eq(color):
    assert color == color


def test_neq(color):
    assert color != Color(name="red")
