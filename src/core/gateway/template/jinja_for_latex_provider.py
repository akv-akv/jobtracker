import re
from typing import Any, Callable, Dict

from src.core.gateway.template.jinja_provider import JinjaProvider


class JinjaForLatexProvider(JinjaProvider):
    """Jinja-based template rendering provider tailored for LaTeX."""

    def __init__(self):
        # J2_ARGS customized for LaTeX
        JINJA_ENV_ARGS = {
            "block_start_string": "block{",
            "block_end_string": "}endblock",
            "variable_start_string": "var{",
            "variable_end_string": "}endvar",
            "comment_start_string": r"comment{",
            "comment_end_string": r"}endcomment",
            "line_statement_prefix": r"\%-",
            "line_comment_prefix": r"\%#",
            "trim_blocks": True,
            "autoescape": False,
        }
        super().__init__(JINJA_ENV_ARGS)

    @staticmethod
    def escape_latex_str_if_str(value: Any) -> Any:
        """Escape LaTeX special characters in strings."""
        if isinstance(value, str):
            # Reorder so backslashes are replaced first
            latex_special_chars = {
                "\\": r"\textbackslash{}",
                "%": r"\%",
                "&": r"\&",
                "$": r"\$",
                "#": r"\#",
                "_": r"\_",
                "{": r"\{",
                "}": r"\}",
                "~": r"\textasciitilde{}",
                "^": r"\textasciicircum{}",
            }
            pattern = re.compile(r"(\\|%|&|\$|#|_|{|}|~|\^)")

            def replacer(match):
                original = match.group()
                replaced = latex_special_chars[original]
                print(f"Replacing '{original}' with '{replaced}'")  # Debugging output
                return replaced

            return pattern.sub(replacer, value)
        return value

    @staticmethod
    def recursive_apply(data: Any, func: Callable[[Any], Any]) -> Any:
        return {k: func(v) for k, v in data.items()}

    def render(self, template: str, context: Dict[str, Any]) -> str:
        """Render a LaTeX template with context."""
        # Preprocess the context for LaTeX compatibility
        sanitized_context = self.recursive_apply(context, self.escape_latex_str_if_str)
        return super().render(template, sanitized_context)
