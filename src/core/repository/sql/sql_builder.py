from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Executable,
    Table,
    and_,
    asc,
    delete,
    desc,
    func,
    select,
    true,
    update,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import ColumnElement, ColumnOperators, false

from src.core.domain.context import ctx
from src.core.repository.base.filter import ComparisonFilter, ComparisonOperator, Filter
from src.core.repository.base.pagination import PageOptions


def _regular_filter_to_sql(column: ColumnElement, filter: Filter) -> ColumnElement:
    if len(filter.values) == 0:
        return false()
    elif len(filter.values) == 1:
        return column == filter.values[0]
    else:
        return column.in_(filter.values)


# Maps our operators to SQLAlchemy operators
comparitor_map = {
    ComparisonOperator.EQ: ColumnOperators.__eq__,
    ComparisonOperator.NE: ColumnOperators.__ne__,
    ComparisonOperator.LT: ColumnOperators.__lt__,
    ComparisonOperator.LE: ColumnOperators.__le__,
    ComparisonOperator.GT: ColumnOperators.__gt__,
    ComparisonOperator.GE: ColumnOperators.__ge__,
}


def _comparison_filter_to_sql(
    column: ColumnElement, filter: ComparisonFilter
) -> ColumnElement:
    return column.operate(comparitor_map[filter.operator], filter.values[0])


class SQLBuilder:
    def __init__(self, table: Table, multitenant: bool = False):
        if multitenant and not hasattr(table.c, "tenant"):
            raise ValueError("Can't use a multitenant SQLBuilder without tenant column")
        self.table = table
        self.multitenant = multitenant

    @property
    def current_tenant(self) -> UUID | None:
        if not self.multitenant:
            return None
        if ctx.tenant is None:
            raise RuntimeError(f"{self.__class__} requires a tenant in the context")
        return ctx.tenant.id

    def _filter_to_sql(self, filter: Filter) -> ColumnElement:
        try:
            column = getattr(self.table.c, filter.field)
        except AttributeError:
            return false()
        if isinstance(filter, ComparisonFilter):
            return _comparison_filter_to_sql(column, filter)
        else:
            return _regular_filter_to_sql(column, filter)

    def _filters_to_sql(self, filters: list[Filter]) -> ColumnElement:
        qs = [self._filter_to_sql(x) for x in filters]
        if self.multitenant:
            qs.append(self.table.c.tenant == self.current_tenant)
        return and_(true(), *qs)

    def _id_filter_to_sql(self, id: UUID) -> ColumnElement:
        return self._filters_to_sql([Filter(field="id", values=[id])])

    def _santize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        known = {c.key for c in self.table.c}
        result = {k: item[k] for k in item.keys() if k in known}
        if "id" in result and result["id"] is None:
            del result["id"]
        if self.multitenant:
            result["tenant"] = self.current_tenant
        return result

    def select(
        self,
        filters: list[Filter],
        params: PageOptions | None = None,
        for_update: bool = False,
    ) -> Executable:
        query = select(self.table)
        if for_update:
            query = query.with_for_update()
        query = query.where(self._filters_to_sql(filters))
        if params is not None:
            sort = asc(params.order_by) if params.ascending else desc(params.order_by)
            query = query.order_by(sort).limit(params.limit).offset(params.offset)
        return query

    def insert(self, item: dict[str, Any]) -> Executable:
        return (
            insert(self.table).values(**self._santize_item(item)).returning(self.table)
        )

    def upsert(self, item: dict[str, Any]) -> Executable:
        item = self._santize_item(item)
        return (
            insert(self.table)
            .values(**item)
            .on_conflict_do_update(
                index_elements=["id", "tenant"] if self.multitenant else ["id"],
                set_=item,
            )
            .returning(self.table)
        )

    def update(
        self, id: UUID, item: dict[str, Any], if_unmodified_since: datetime | None
    ):
        q = self._id_filter_to_sql(id)
        if if_unmodified_since is not None:
            q &= self.table.c.updated_at == if_unmodified_since
        return (
            update(self.table)
            .where(q)
            .values(**self._santize_item(item))
            .returning(self.table)
        )

    def delete(self, id: UUID) -> Executable:
        return (
            delete(self.table)
            .where(self._id_filter_to_sql(id))
            .returning(self.table.c.id)
        )

    def count(self, filters: list[Filter]) -> Executable:
        return (
            select(func.count().label("count"))
            .select_from(self.table)
            .where(self._filters_to_sql(filters))
        )

    def exists(self, filters: list[Filter]) -> Executable:
        return (
            select(true().label("exists"))
            .select_from(self.table)
            .where(self._filters_to_sql(filters))
            .limit(1)
        )
