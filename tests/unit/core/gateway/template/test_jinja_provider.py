import pytest
from jinja2 import TemplateSyntaxError, UndefinedError

from src.core.gateway.template.jinja_provider import JinjaProvider


@pytest.fixture
def jinja_provider():
    """Fixture to provide a Jinja provider instance."""
    return JinjaProvider()


@pytest.mark.parametrize(
    "template, context, expected_result",
    [
        # Basic rendering
        ("Hello, {{ name }}!", {"name": "John"}, "Hello, John!"),
        # Empty template
        ("", {}, ""),
        # Empty context
        ("Hello, {{ name }}!", {}, UndefinedError),
        # Special characters
        (r"Path: C:\\Users\\{{ user }}", {"user": "john"}, r"Path: C:\\Users\\john"),
        # Nested loops
        (
            "{% for user in users %}{{ user.name }} {% endfor %}",
            {"users": [{"name": "John"}, {"name": "Doe"}]},
            "John Doe ",
        ),
        # Escaping
        ("{{ '<script>' }}", {}, "<script>"),
        # Large input
        ("{{ 'a' * 10000 }}", {}, "a" * 10000),
        # Missing keys with default filter
        ("{{ name|default('Guest') }}", {}, "Guest"),
        # Custom filter (assuming a custom filter 'reverse' is registered)
        ("{{ 'hello'|reverse }}", {}, "olleh"),
        # Whitespace control
        ("{% for i in range(3) -%}{{ i }} {%- endfor %}", {"range": range}, "012"),
        # Non-string context values
        ("The number is {{ number }}.", {"number": 42}, "The number is 42."),
    ],
)
def test_render_templates(jinja_provider, template, context, expected_result):
    """Test rendering templates with various edge cases."""
    if isinstance(expected_result, type) and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            jinja_provider.render(template, context)
    else:
        result = jinja_provider.render(template, context)
        assert result == expected_result


@pytest.mark.parametrize(
    "template, context, expected_exception",
    [
        # Invalid syntax
        ("{% if name %}", {"name": "John"}, TemplateSyntaxError),
        # Missing keys without default
        ("Hello, {{ name }}!", {}, UndefinedError),
    ],
)
def test_render_exceptions(jinja_provider, template, context, expected_exception):
    """Test rendering templates that raise exceptions."""
    with pytest.raises(expected_exception):
        jinja_provider.render(template, context)


def test_render_custom_filter_registration(jinja_provider):
    """Test custom filter registration in the provider."""

    def reverse_filter(value):
        return value[::-1]

    jinja_provider.environment.filters["reverse"] = reverse_filter

    template = "{{ 'hello'|reverse }}"
    context = {}
    expected_result = "olleh"

    result = jinja_provider.render(template, context)
    assert result == expected_result


def test_render_large_context(jinja_provider):
    """Test rendering with a large context."""
    large_context = {f"key_{i}": f"value_{i}" for i in range(1000)}
    template = "{{ key_999 }}"
    result = jinja_provider.render(template, large_context)
    assert result == "value_999"


def test_render_nested_conditions(jinja_provider):
    """Test rendering with deeply nested conditions."""
    template = """
    {% if user %}
        {% if user.name %}
            Hello, {{ user.name }}!
        {% endif %}
    {% endif %}
    """
    context = {"user": {"name": "John"}}
    expected_result = "Hello, John!"
    result = jinja_provider.render(template, context)
    assert result.strip() == expected_result
