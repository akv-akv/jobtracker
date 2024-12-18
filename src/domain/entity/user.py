from dataclasses import dataclass

from src.domain.base.root_entity import RootEntity


@dataclass(frozen=True)
class User(RootEntity):
    name: str
    email: str
