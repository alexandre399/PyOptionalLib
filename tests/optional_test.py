import pytest

from optional import MissingValueError, Optional


def test_optional_with_value() -> None:
    optional = Optional(10)
    assert optional.get() == 10
    assert not optional.is_empty()
    assert optional.get_or_else(lambda: 0) == 10


def test_optional_without_value() -> None:
    optional: Optional = Optional()
    assert optional.is_empty()
    assert optional.get_or_else(lambda: 0) == 0
    assert optional.get(default=42) == 42
    with pytest.raises(MissingValueError):
        optional.get()


def test_map() -> None:
    assert Optional(10).map(lambda x: x * 2).get() == 20


def test_flat_map() -> None:
    assert Optional(10).flat_map(lambda x: Optional(x * 2)).get() == 20


def test_filter() -> None:
    optional = Optional(10)
    assert not optional.filter(lambda x: x > 5).is_empty()
    assert optional.filter(lambda x: x < 5).is_empty()


def test_peek() -> None:
    optional = Optional(10)
    called = []

    def callback(value) -> None:
        called.append(True)

    assert optional.peek(callback).get() == 10
    assert called


def test_if_present() -> None:
    optional = Optional(10)
    called = []

    def callback(value) -> None:
        called.append(value)

    optional.filter(lambda x: x > 20).if_present(callback)
    assert not called

    optional.if_present(callback)
    assert called


def test_cache() -> None:
    parent = Optional(2)
    optional = parent.cache()

    assert optional.map(lambda x: x**2).get() == 4

    parent._value = -1  # noqa: SLF001

    assert optional.map(lambda x: x**2).get() == 4

    optional = Optional(2).filter(lambda x: x > 5).cache()
    assert optional.map(lambda x: x**2).is_empty()
    assert optional.map(lambda x: x**2).is_empty()


def test_bool() -> None:
    assert Optional(42)
    assert not Optional()


def test_null_value() -> None:
    assert Optional(42, null_value=42).is_empty()
    assert Optional(21, null_value=42).map(lambda x: x * 2).is_empty()
    assert Optional(21, null_value=42).map(lambda x: x * 2).get(default=0) == 0


def test_chained_methods() -> None:
    # Chaining multiple methods
    result: int = (
        Optional(10)
        .map(lambda x: x * 2)  # Multiply by 2 -> 20
        .filter(lambda x: x > 15)  # Passes filter -> 20
        .flat_map(lambda x: Optional(x + 10))  # Add 10 -> 30
        .peek(print)  # Print value -> 30
        .cache()  # Cache the value
        .get_or_else(lambda: 0)
    )  # Get value or else 0 -> 30

    assert result == 30
