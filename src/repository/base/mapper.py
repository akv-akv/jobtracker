from typing import Any


class Mapper:
    def to_internal(self, external: Any) -> dict[str, Any]:
        return external

    def to_external(self, internal: dict[str, Any]) -> dict[str, Any]:
        return internal
