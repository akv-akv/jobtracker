from unittest.mock import MagicMock

import pytest

from src.core.gateway.template.template_gateway import TemplateGateway


@pytest.fixture
def mock_provider():
    """Fixture to mock a template provider."""
    return MagicMock()


@pytest.fixture
def template_gateway(mock_provider):
    """Fixture to provide a TemplateGateway with a mocked provider."""
    return TemplateGateway(mock_provider)


def test_render_calls_provider(template_gateway, mock_provider):
    """Test that the gateway delegates rendering to the provider."""
    template = "Hello, {{ name }}!"
    context = {"name": "John"}
    mock_provider.render.return_value = "Hello, John!"

    result = template_gateway.render(template, context)

    mock_provider.render.assert_called_once_with(template, context)
    assert result == "Hello, John!"


def test_render_handles_provider_exception(template_gateway, mock_provider):
    """Test that the gateway handles exceptions raised by the provider."""
    template = "Invalid template"
    context = {}
    mock_provider.render.side_effect = ValueError("Rendering failed")

    with pytest.raises(ValueError, match="Rendering failed"):
        template_gateway.render(template, context)
