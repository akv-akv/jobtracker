from typing import Any, Dict

from jinja2 import Environment, StrictUndefined, Template


class JinjaProvider:
    """Jinja-based template rendering provider."""

    def __init__(self):
        self.environment = Environment(undefined=StrictUndefined)

    def render(self, template: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 template with the provided context."""
        compiled_template: Template = self.environment.from_string(template)
        return compiled_template.render(context)
