from optional import Optional
import pytest


def test_optional_with_value():
    optional = Optional(10)
    assert optional.get() == 10
    assert not optional.is_empty()
    assert optional.get_or_else(lambda: 0) == 10


def test_optional_without_value():
    optional = Optional()
    assert optional.is_empty()
    assert optional.get_or_else(lambda: 0) == 0
    with pytest.raises(ValueError):
        optional.get()


def test_map():
    assert Optional(10).map(lambda x: x * 2).get() == 20


def test_flat_map():
    assert Optional(10).flat_map(lambda x: Optional(x * 2)).get() == 20


def test_filter():
    optional = Optional(10)
    assert not optional.filter(lambda x: x > 5).is_empty()
    assert optional.filter(lambda x: x < 5).is_empty()


def test_peek():
    optional = Optional(10)
    called = []

    def callback(value):
        called.append(True)

    assert optional.peek(callback).get() == 10
    assert called


def test_if_present():
    optional = Optional(10)
    called = []

    def callback(value):
        called.append(True)

    optional.if_present(callback)
    assert called


def test_cache():
    parent = Optional(2)
    optional = parent.cache()

    assert optional.map(lambda x: x**2).get() == 4

    parent._value = -1

    assert optional.map(lambda x: x**2).get() == 4


def test_bool():
    assert Optional(42)
    assert not Optional()


def test_chained_methods():
    # Chaining multiple methods
    result = (
        Optional(10)
        .map(lambda x: x * 2)  # Multiply by 2 -> 20
        .filter(lambda x: x > 15)  # Passes filter -> 20
        .flat_map(lambda x: Optional(x + 10))  # Add 10 -> 30
        .peek(print)  # Print value -> 30
        .cache()  # Cache the value
        .get_or_else(lambda: 0)
    )  # Get value or else 0 -> 30

    assert result == 30
