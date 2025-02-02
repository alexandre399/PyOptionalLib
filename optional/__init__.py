from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar
from typing import Optional as TypingOptional

T = TypeVar("T")
R = TypeVar("R")

__all__ = ["Optional"]


class MissingValueError(ValueError):
    pass


class Optional(Generic[T]):
    """A class representing an optional value, which may or may not contain a value.

    Attributes:
        _value (T | None): The optional value.
        _parent (Optional): The parent optional value.

    """

    _value: TypingOptional[T]
    _parent: "Optional[Any]"

    def __init__(self, value: TypingOptional[T] = None) -> None:
        """Initialize the Optional instance with a value.

        Args:
            value (T | None): The initial value.

        """
        self._value = value
        self._parent = object.__new__(Optional)

    @property
    def value(self) -> TypingOptional[T]:
        """Get the value of the Optional instance.

        Returns:
            T | None: The value of the Optional instance.

        """
        return self._value

    def map(self, transform: Callable[[T], R]) -> "Optional[R]":
        """Apply a transformation to the value and return a new Optional instance.

        Args:
            transform (Callable[[T], R]): The transformation function.

        Returns:
            Optional[R]: A new Optional instance with the transformed value.

        """
        return OptionalTransformMap[T, R](parent=self, transform=transform)

    def flat_map(self, transform: Callable[[T], R]) -> "Optional[R]":
        """Apply a transformation to the value and flatten the result.

        Args:
            transform (Callable[[T], R]): The transformation function.

        Returns:
            Optional[R]: A new Optional instance with the transformed and flattened value.

        """
        return OptionalTransformFlatMap[T, R](parent=self, transform=transform)

    def filter(self, transform: Callable[[T], bool]) -> "Optional[T]":
        """Filter the value based on a predicate and return a new Optional instance.

        Args:
            transform (Callable[[T], bool]): The predicate function.

        Returns:
            Optional[T]: A new Optional instance with the filtered value.

        """
        return OptionalTransformFilter[T](parent=self, transform=transform)  # type: ignore [arg-type]

    def cache(self) -> "Optional[T]":
        """Cache the value and return a new Optional instance.

        Returns:
            Optional[T]: A new Optional instance with the cached value.

        """
        return OptionalTransformCache[T](parent=self)

    def peek(self, transform: Callable[[T], None]) -> "Optional[T]":
        """Apply a function to the value without transforming it and return a new Optional instance.

        Args:
            transform (Callable[[T], None]): The function to apply.

        Returns:
            Optional[T]: A new Optional instance with the same value.

        """
        return OptionalTransformPeek[T](parent=self, transform=transform)  # type: ignore [arg-type]

    def if_present(self, transform: Callable[[T], None]) -> None:
        """Apply a function to the value if it is present.

        Args:
            transform (Callable[[T], None]): The function to apply.

        """
        try:
            value: T = self.get()
            transform(value)
        except MissingValueError:
            pass

    def is_empty(self) -> bool:
        """Check if the Optional instance is empty.

        Returns:
            bool: True if the Optional instance is empty, False otherwise.

        """
        try:
            self.get()
            return False
        except MissingValueError:
            return True

    def __bool__(self) -> bool:
        """Check if the Optional instance is not empty.

        Returns:
            bool: True if the Optional instance is not empty, False otherwise.

        """
        return not self.is_empty()

    def _get_value(self) -> TypingOptional[T]:
        """Get the value of the Optional instance.

        Returns:
            T | None: The value of the Optional instance.

        """
        return self.value

    def get(
        self,
        default: TypingOptional[T] = None,
    ) -> T:
        """Get the value of the Optional instance, or a default value if not present.

        Args:
            default (T | None): The default value.

        Returns:
            T: The value of the Optional instance, or the default value.

        Raises:
            MissingValueError: If the value is not present and no default value is provided.

        """
        value: TypingOptional[T] = self._get_value()
        if value is None:
            value = default
        if value is None:
            raise MissingValueError("Optional is empty")
        return value

    def get_or_else(self, transform: Callable[[], T]) -> T:
        """Get the value of the Optional instance, or a value provided by a function if not present.

        Args:
            transform (Callable[[], T]): The function to provide a value.

        Returns:
            T: The value of the Optional instance, or the value provided by the function.

        """
        try:
            return self.get()
        except MissingValueError:
            return transform()


class OptionalTransform(ABC, Generic[T, R], Optional[R]):
    """An abstract base class for transforming Optional values.

    Attributes:
        _transform (Callable[[T], R]): The transformation function.

    """

    _transform: TypingOptional[Callable[[T], R]] = None

    def __init__(self, parent: Optional[T], transform: TypingOptional[Callable[[T], R]] = None) -> None:
        """Initialize the OptionalTransform instance.

        Args:
            parent (Optional): The parent Optional instance.
            transform (Callable[[T], R]): The transformation function.

        """
        self._parent = parent
        self._transform = transform

    @abstractmethod
    def _run(self) -> TypingOptional[R]:
        """Run the transformation and return the result.

        Returns:
            R | None: The result of the transformation.

        """

    def _get_value(self) -> TypingOptional[R]:
        """Get the transformed value of the Optional instance.

        Returns:
            R | None: The transformed value of the Optional instance.

        """
        return self._run()


class OptionalTransformMap(OptionalTransform[T, R]):
    """A class for mapping Optional values."""

    def _run(self) -> TypingOptional[R]:
        """Run the transformation and return the result.

        Returns:
            R | None: The result of the transformation.

        """
        try:
            value: T = self._parent.get()
            return self._transform(value)  # type: ignore [misc]
        except MissingValueError:
            return None


class OptionalTransformFlatMap(OptionalTransform[T, R]):
    """A class for flat mapping Optional values."""

    def _run(self) -> TypingOptional[R]:
        """Run the transformation and return the flattened result.

        Returns:
            R | None: The flattened result of the transformation.

        """
        try:
            value: T = self._parent.get()
            return self._transform(value).get()  # type: ignore [union-attr, misc]
        except MissingValueError:
            return None


class OptionalTransformFilter(OptionalTransform[T, T]):
    """A class for filtering Optional values."""

    def _run(self) -> TypingOptional[T]:
        """Run the filter and return the result.

        Returns:
            T | None: The filtered result.

        """
        try:
            value: T = self._parent.get()
            return value if self._transform(value) else None  # type: ignore [misc]
        except MissingValueError:
            return None


class OptionalTransformPeek(OptionalTransform[T, T]):
    """A class for peeking Optional values."""

    def _run(self) -> TypingOptional[T]:
        """Run the function and return the original value.

        Returns:
            T | None: The original value.

        """
        try:
            value: T = self._parent.get()
            self._transform(value)  # type: ignore [misc]
            return value
        except MissingValueError:
            return None


class OptionalTransformCache(OptionalTransform[T, T]):
    """A class for caching Optional values."""

    def is_cached(self) -> bool:
        """Test if value is in cache.

        Returns:
            bool.

        """
        return getattr(self, "_cached", False)

    def _run(self) -> TypingOptional[T]:
        """Cache the value and return the result.

        Returns:
            T | None: The cached value.

        """
        if not self.is_cached():
            try:
                self._value = self._parent.get()
            except MissingValueError:
                pass
            finally:
                self._cached = True
        return self._value
