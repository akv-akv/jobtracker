from typing import Any


class Mapper:
    async def to_internal(self, external: Any) -> dict[str, Any]:
        return external

    async def to_external(self, internal: dict[str, Any]) -> dict[str, Any]:
        return internal
