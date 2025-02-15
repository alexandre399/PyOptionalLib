import pytest

from optional import MissingValueError, Optional, optional


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

    assert optional.filter(lambda x: x < 5).map(lambda x: x * 2).get(default=42) == 42


def test_exception() -> None:
    optional: Optional = Optional()
    with pytest.raises(MissingValueError):
        optional.get()

    class CustomMissingValueError(MissingValueError):
        pass

    with pytest.raises(CustomMissingValueError):
        optional.map(lambda x: x * 2).get(exception=CustomMissingValueError)

    with pytest.raises(CustomMissingValueError):
        optional.get(exception=CustomMissingValueError)


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

    parent._value = -1

    assert optional.map(lambda x: x**2).get() == 4

    optional = Optional(2).filter(lambda x: x > 5).cache()
    assert optional.map(lambda x: x**2).is_empty()
    assert optional.map(lambda x: x**2).is_empty()


def test_bool() -> None:
    assert Optional(42)
    assert not Optional()


def test_null_value() -> None:
    assert Optional(42, is_empty=lambda x: x == 42).is_empty()
    assert not Optional(is_empty=lambda x: x == 42).is_empty()

    assert Optional(42, is_empty=lambda x: x == 42).get(default=10) == 10

    with pytest.raises(MissingValueError):
        Optional(42, is_empty=lambda x: x == 42).get()

    assert Optional(is_empty=lambda x: x == 42).get() is None

    assert Optional(21, is_empty=lambda x: x == 42).map(lambda x: x * 2).is_empty()
    assert (
        Optional(21, is_empty=lambda x: x == 42).map(lambda x: x * 2).get(default=0) == 0
    )


def test_reduce() -> None:
    assert Optional(10).reduce(Optional(20), lambda a, b: a).get() == 10
    assert Optional(10).reduce(Optional(20), lambda a, b: b).get() == 20
    Optional(10).reduce(Optional(20), lambda a, b: b)

    assert (
        Optional(10).map(lambda x: x + 1).reduce(Optional(20), lambda a, b: a).get() == 11
    )
    assert (
        Optional(10).reduce(Optional(20).map(lambda x: x + 1), lambda a, b: b).get() == 21
    )

    with pytest.raises(MissingValueError):
        assert Optional().reduce(Optional(20), lambda a, b: a).get()

    with pytest.raises(MissingValueError):
        assert Optional(10).reduce(Optional(), lambda a, b: a).get()


def test_decorator() -> None:
    @optional()
    def example_empty():
        return None

    @optional()
    def example():
        return 42

    @optional(catch=True)
    def example_raise():
        raise KeyError

    @optional()
    def example_raise2():
        raise KeyError

    result = example_empty()
    assert isinstance(result, Optional)
    assert result.is_empty()

    result = example()
    assert isinstance(result, Optional)
    assert result.get() == 42

    result = example_raise()
    assert isinstance(result, Optional)
    assert result.is_empty()
    assert isinstance(result.err, KeyError)  # type: ignore[attr-defined]

    with pytest.raises(KeyError):
        example_raise2()


def test_aithmetic() -> None:
    assert Optional(3) + Optional(2) == 5
    assert Optional(3) - Optional(2) == 1
    assert Optional(3) * Optional(2) == 6
    assert Optional(3) / Optional(2) == 1.5
    assert Optional(3) // Optional(2) == 1
    assert Optional(3) % Optional(2) == 1
    assert Optional(3) ** Optional(2) == 9


def test_cast() -> None:
    assert int(Optional(3.0)) == 3
    assert float(Optional(3.0)) == 3.0
    assert str(Optional(3.0)) == "3.0"


def test_eq() -> None:
    assert Optional(3) == Optional(2 + 1)
    assert Optional(3) == 3
    assert Optional(3) != Optional(2)
    assert Optional() != Optional(2)


def test_lt() -> None:
    assert Optional(3) < Optional(4)
    assert Optional(3) < 4
    assert Optional(3) <= Optional(3)
    assert Optional(3) <= 3
    assert not Optional(3) < Optional(2)
    assert not Optional(3) <= Optional(2)


def test_gt() -> None:
    assert Optional(3) > Optional(2)
    assert Optional(3) > 2
    assert Optional(3) >= Optional(3)
    assert Optional(3) >= 3
    assert not Optional(3) > Optional(4)
    assert not Optional(3) >= Optional(4)


def test_call() -> None:
    assert Optional(3)(lambda x: x * 2)(lambda x: x + 1) == 7
    assert not Optional(3, is_empty=lambda x: x is False)(lambda x: x * 2)(
        lambda x: x + 1
    )(lambda x: x != 7)


def test_chained_methods() -> None:
    # Chaining multiple methods
    result: int = (
        Optional(10)
        .map(lambda x: x * 2)  # Multiply by 2 -> 20
        .filter(lambda x: x > 15)  # Passes filter -> 20
        .flat_map(lambda x: Optional(x + 10))  # Add 10 -> 30
        .peek(print)  # Print value -> 30
        .cache()
        .reduce(Optional(20), lambda a, b: a)
        .get_or_else(lambda: 0)
    )  # Get value or else 0 -> 30

    assert result == 30
