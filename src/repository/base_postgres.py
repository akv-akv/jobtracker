from typing import Callable, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")  # Type for ORM model
D = TypeVar("D")  # Type for Domain entity


class BasePostgresRepository(Generic[T, D]):
    """Base repository with common database operations and conversion."""

    def __init__(
        self,
        session: Session,
        model: Type[T],
        to_domain: Callable[[T], D],
        from_domain: Callable[[D], T],
    ):
        self.session = session
        self.model = model
        self.to_domain = to_domain  # Function to convert ORM model to domain entity
        self.from_domain = from_domain  # Function to convert domain entity to ORM model

    def create(self, obj: D) -> None:
        """Insert a new object into the database."""
        orm_obj = self.from_domain(obj)  # Convert domain entity to ORM model
        self.session.add(orm_obj)
        self.session.commit()

    def read(self, obj_id) -> Optional[D]:
        """Retrieve an object by its ID."""
        orm_obj = self.session.query(self.model).filter_by(id=obj_id).first()
        return self.to_domain(orm_obj) if orm_obj else None

    def delete(self, obj_id) -> bool:
        """Delete an object by its ID."""
        orm_obj = self.session.query(self.model).filter_by(id=obj_id).first()
        if not orm_obj:
            return False
        self.session.delete(orm_obj)
        self.session.commit()
        return True

    def list(self, filters: Optional[dict] = None) -> List[D]:
        """Retrieve a list of objects with optional filters."""
        query = self.session.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return [self.to_domain(orm_obj) for orm_obj in query.all()]

    def update(self, obj_id, data) -> Optional[D]:
        """Update an existing object."""
        orm_obj = self.session.query(self.model).filter_by(id=obj_id).first()
        if not orm_obj:
            return None

        for key, value in data.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        self.session.commit()

        return self.to_domain(orm_obj)
