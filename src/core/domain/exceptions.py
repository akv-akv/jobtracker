from typing import Any
from uuid import UUID


class DoesNotExist(Exception):
    def __init__(self, name: str, id: UUID | None = None):
        super().__init__()
        self.name = name
        self.id = id

    def __str__(self):
        if self.id:
            return f"does not exist: {self.name} with id={self.id}"
        else:
            return f"does not exist: {self.name}"


class Conflict(Exception):
    def __init__(self, msg: str | None = None):
        super().__init__(msg)


class AlreadyExists(Exception):
    def __init__(self, value: Any = None, key: str = "id"):
        super().__init__(f"record with {key}={value} already exists")
