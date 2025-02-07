"""Optional module."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Generic, TypeVar

R = TypeVar("R")
T = TypeVar("T")

__all__ = ["Optional"]


class MissingValueError(ValueError):
    def __init__(self) -> None:
        super().__init__("Optional is empty")


class Optional(Generic[T]):
    """A class representing an optional value, which may or may not contain a value.

    Attributes:
        _value (T | None): The optional value.
        _parent (Optional): The parent optional value.
        _null_value (T | None): Null value.

    """

    _value: T | None
    _null_value: T | None
    _parent: "Optional[Any]"

    def __init__(self, value: T | None = None, null_value: T | None = None) -> None:
        """Initialize the Optional instance with a value.

        Args:
            value (T | None): The initial value, default=None.
            null_value (T | None): Null value, default=None.

        """
        self._value = value
        self._null_value = null_value
        self._parent = object.__new__(Optional)

    @property
    def value(self) -> T | None:
        """Get the value of the Optional instance.

        Returns:
            T | None: The value of the Optional instance.

        """
        return self._value

    def map(self, callback: Callable[[T], R]) -> "Optional[R]":
        """Apply a transformation to the value and return a new Optional instance.

        Args:
            callback (Callable[[T], R]): The transformation function.

        Returns:
            Optional[R]: A new Optional instance with the transformed value.

        """
        return OptionalTransformMap[T, R](parent=self, callback=callback)

    def flat_map(self, callback: Callable[[T], "Optional[R]"]) -> "Optional[R]":
        """Apply a transformation to the value and flatten the result.

        Args:
            callback (Callable[[T], R]): The transformation function.

        Returns:
            Optional[R]: A new Optional instance with the transformed and flattened value.

        """
        return OptionalTransformMap[T, R](parent=self, callback=lambda x: callback(x).get())

    def filter(self, callback: Callable[[T], bool]) -> "Optional[T]":
        """Filter the value based on a predicate and return a new Optional instance.

        Args:
            callback (Callable[[T], bool]): The predicate function.

        Returns:
            Optional[T]: A new Optional instance with the filtered value.

        """
        return OptionalTransformFilter[T](parent=self, callback=callback)  # type: ignore [arg-type]

    def cache(self) -> "Optional[T]":
        """Cache the value and return a new Optional instance.

        Returns:
            Optional[T]: A new Optional instance with the cached value.

        """
        return OptionalTransformCache[T](parent=self)

    def peek(self, callback: Callable[[T], None]) -> "Optional[T]":
        """Apply a function to the value without transforming it and return a new Optional instance.

        Args:
            callback (Callable[[T], None]): The function to apply.

        Returns:
            Optional[T]: A new Optional instance with the same value.

        """
        return OptionalTransformPeek[T](parent=self, callback=callback)  # type: ignore [arg-type]

    def if_present(self, callback: Callable[[T], None]) -> None:
        """Apply a function to the value if it is present.

        Args:
            callback (Callable[[T], None]): The function to apply.

        """
        try:
            value: T = self.get()
            callback(value)
        except MissingValueError:
            pass

    def is_empty(self) -> bool:
        """Check if the Optional instance is empty.

        Returns:
            bool: True if the Optional instance is empty, False otherwise.

        """
        try:
            self.get(default=self._get_null_value())
        except MissingValueError:
            return True
        else:
            return False

    def __bool__(self) -> bool:
        """Check if the Optional instance is not empty.

        Returns:
            bool: True if the Optional instance is not empty, False otherwise.

        """
        return not self.is_empty()

    def _get_null_value(self) -> T | None:
        """Get the null value of the Optional instance.

        Returns:
            T | None: The null value of the Optional instance.

        """
        return self._null_value

    def _get_value(self) -> T | None:
        """Get the value of the Optional instance.

        Returns:
            T | None: The value of the Optional instance.

        """
        return self.value

    def get(self, default: T | None = None) -> T:
        """Get the value of the Optional instance, or a default value if not present.

        Args:
            default (T | None): The default value.

        Returns:
            T: The value of the Optional instance, or the default value.

        Raises:
            MissingValueError: If the value is not present and no default value is provided.

        """
        value: T | None = self._get_value()
        null_value: T | None = self._get_null_value()
        if value == null_value:
            value = default
        if value == null_value:
            raise MissingValueError
        return value  # type: ignore [return-value]

    def get_or_else(self, callback: Callable[[], T]) -> T:
        """Get the value of the Optional instance, or a value provided by a function if not present.

        Args:
            callback (Callable[[], T]): The function to provide a value.

        Returns:
            T: The value of the Optional instance, or the value provided by the function.

        """
        try:
            return self.get()
        except MissingValueError:
            return callback()


class OptionalTransform(ABC, Generic[T, R], Optional[R]):
    """An abstract base class for transforming Optional values.

    Attributes:
        _callback (Callable[[T], R]): The transformation function.

    """

    _callback: Callable[[T], R] | None = None

    def __init__(self, parent: Optional[T], callback: Callable[[T], R] | None = None) -> None:
        """Initialize the OptionalTransform instance.

        Args:
            parent (Optional): The parent Optional instance.
            callback (Callable[[T], R]): The transformation function.

        """
        self._parent = parent
        self._callback = callback

    def _get_null_value(self) -> R | None:
        """Get the null value of the Optional instance.

        Returns:
            R | None: The null value of the Optional instance.

        """
        return self._parent._get_null_value()  # noqa: SLF001

    @abstractmethod
    def _get_value(self) -> R | None:
        """Get the transformed value of the Optional instance.

        Returns:
            R | None: The transformed value of the Optional instance.

        """


class OptionalTransformMap(OptionalTransform[T, R]):
    """A class for mapping Optional values."""

    def _get_value(self) -> R | None:
        """Run the transformation and return the result.

        Returns:
            R | None: The result of the transformation.

        """
        value: T = self._parent.get()
        return self._callback(value)  # type: ignore [misc]


class OptionalTransformFilter(OptionalTransform[T, T]):
    """A class for filtering Optional values."""

    def _get_value(self) -> T | None:
        """Run the filter and return the result.

        Returns:
            T | None: The filtered result.

        """
        value: T = self._parent.get()
        return value if self._callback(value) else self._get_null_value()  # type: ignore [misc]


class OptionalTransformPeek(OptionalTransform[T, T]):
    """A class for peeking Optional values."""

    def _get_value(self) -> T | None:
        """Run the function and return the original value.

        Returns:
            T | None: The original value.

        """
        value: T = self._parent.get()
        self._callback(value)  # type: ignore [misc]
        return value


class OptionalTransformCache(OptionalTransform[T, T]):
    """A class for caching Optional values."""

    def is_cached(self) -> bool:
        """Test if value is in cache.

        Returns:
            bool.

        """
        return getattr(self, "_cached", False)

    def _get_value(self) -> T | None:
        """Cache the value and return the result.

        Returns:
            T | None: The cached value.

        """
        if not self.is_cached():
            try:
                self._value = self._parent.get()
            except MissingValueError:
                self._value = self._get_null_value()
            finally:
                self._cached = True
        return self._value
