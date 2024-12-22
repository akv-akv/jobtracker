from datetime import datetime, timedelta

import pytest

from src.core.repository.base.pagination import Page, PageOptions


# Test PageOptions
@pytest.mark.parametrize(
    "limit, offset, order_by, ascending, cursor",
    [
        (10, 0, "updated_at", False, None),
        (20, 5, "created_at", True, datetime(2023, 1, 1, 12, 0, 0)),
    ],
)
def test_page_options_initialization(limit, offset, order_by, ascending, cursor):
    options = PageOptions(
        limit=limit,
        offset=offset,
        order_by=order_by,
        ascending=ascending,
        cursor=cursor,
    )

    assert options.limit == limit
    assert options.offset == offset
    assert options.order_by == order_by
    assert options.ascending == ascending
    assert options.cursor == cursor


def test_page_options_defaults():
    options = PageOptions(limit=10)

    assert options.limit == 10
    assert options.offset == 0
    assert options.order_by == "created_at"
    assert options.ascending is True
    assert options.cursor is None


# Test Page
@pytest.mark.parametrize(
    "total, items, limit, offset",
    [
        (100, ["item1", "item2"], 10, 0),
        (50, ["itemA", "itemB", "itemC"], 20, 5),
    ],
)
def test_page_initialization(total, items, limit, offset):
    page = Page(total=total, items=items, limit=limit, offset=offset)

    assert page.total == total
    assert page.items == items
    assert page.limit == limit
    assert page.offset == offset


def test_page_defaults():
    page = Page(total=0, items=[])

    assert page.total == 0
    assert page.items == []
    assert page.limit is None
    assert page.offset is None


# Test PageOptions with datetime cursor
def test_page_options_cursor():
    now = datetime.now()
    options = PageOptions(limit=10, cursor=now)

    assert options.cursor == now

    # Simulate moving the cursor forward
    new_cursor = now + timedelta(days=1)
    options.cursor = new_cursor
    assert options.cursor == new_cursor
