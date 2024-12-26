from typing import Any, Dict


class TemplateGateway:
    def __init__(
        self,
        provider: Any,
    ):
        self.provider = provider

    def render(self, template: str, context: Dict[str, Any]) -> str:
        return self.provider.render(template, context)
