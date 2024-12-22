from dataclasses import dataclass

from src.core.domain.root_entity import RootEntity


@dataclass(frozen=True)
class User(RootEntity):
    name: str
