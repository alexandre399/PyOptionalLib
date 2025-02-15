"""Optional module."""

import functools
from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import copy
from typing import Any, Generic, TypeVar

R = TypeVar("R")
S = TypeVar("S")
T = TypeVar("T")

__all__ = ["Optional", "optional"]


class MissingValueError(ValueError):
    def __init__(self) -> None:
        super().__init__("Optional is empty")


class Optional(Generic[T]):
    """A class representing an optional value, which may or may not contain a value.

    Attributes:
        _value (T | None): The optional value.
        _is_empty (Callable[[T], bool]): Test if value is empty.

    """

    _value: T | None
    _is_empty_callback: Callable[[T | None], bool]

    def __init__(
        self,
        value: T | None = None,
        is_empty: Callable[[T | None], bool] = lambda x: x is None,
    ) -> None:
        """Initialize the Optional instance with a value.

        Args:
            value (T | None): The initial value, default=None.
            is_empty (Callable[[T], bool]): Test if value is empty.

        """
        self._value = value
        self._is_empty_callback = is_empty

    def _is_empty(self, value: T | None) -> bool:
        """Test if value is empty.

        Returns:
            bool.

        """
        return self._is_empty_callback(value)

    @property
    def value(self) -> T | None:
        """Get the value of the Optional instance.

        Returns:
            T | None: The value of the Optional instance.

        """
        return self._value

    def __call__(self, callback: Callable[[T], R]) -> "Optional[R]":
        """Apply the given callback function to the object's state or data and returns
        the result.

        Args:
            callback (Callable[[T], R]): A function that takes an argument of type T and
                                         returns a value of type R.

        Returns:
            Optional[R]: The result of applying the callback to the object's data, or
                         None if the operation cannot be performed.

        """
        return self.map(callback=callback)

    def map(self, callback: Callable[[T], R]) -> "Optional[R]":
        """Apply a transformation to the value and return a new Optional instance.

        Args:
            callback (Callable[[T], R]): The transformation function.

        Returns:
            Optional[R]: A new Optional instance with the transformed value.

        """
        return OptionalMap[T, R](parent=self, callback=callback)

    def flat_map(self, callback: Callable[[T], "Optional[R]"]) -> "Optional[R]":
        """Apply a transformation to the value and flatten the result.

        Args:
            callback (Callable[[T], R]): The transformation function.

        Returns:
            Optional[R]: A new Optional instance with the transformed and flattened value.

        """
        return OptionalMap[T, R](
            parent=self,
            callback=lambda x: callback(x)._get_value(),  # type: ignore[arg-type, return-value]
        )

    def reduce(
        self, optional: "Optional[R]", callback: Callable[[T, R], S]
    ) -> "Optional[S]":
        """Reduce the value with another Optional instance and return a new Optional
        instance.

        Args:
            optional (Optional[R]): The other Optional instance.
            callback (Callable[[T, R], S]): The reduction function.

        Returns:
            Optional[S]: A new Optional instance with the reduced value.

        """
        return OptionalMap[T, S](
            parent=self,
            callback=lambda x: callback(x, optional._get_value()),  # type: ignore[arg-type]
        )

    def filter(self, callback: Callable[[T], bool]) -> "Optional[T]":
        """Filter the value based on a predicate and return a new Optional instance.

        Args:
            callback (Callable[[T], bool]): The predicate function.

        Returns:
            Optional[T]: A new Optional instance with the filtered value.

        """
        return OptionalFilter[T](parent=self, callback=callback)  # type: ignore[arg-type]

    def cache(self) -> "Optional[T]":
        """Cache the value and return a new Optional instance.

        Returns:
            Optional[T]: A new Optional instance with the cached value.

        """
        return OptionalCache[T](parent=self)

    def peek(self, callback: Callable[[T], None]) -> "Optional[T]":
        """Apply a function to the value without transforming it and return a new
        Optional instance.

        Args:
            callback (Callable[[T], None]): The function to apply.

        Returns:
            Optional[T]: A new Optional instance with the same value.

        """
        return OptionalPeek[T](parent=self, callback=callback)  # type: ignore[arg-type]

    def if_present(self, callback: Callable[[T | None], None]) -> None:
        """Apply a function to the value if it is present.

        Args:
            callback (Callable[[T], None]): The function to apply.

        """
        try:
            value: T | None = self._get_value()
        except MissingValueError:
            pass
        else:
            callback(value)

    def is_empty(self) -> bool:
        """Check if the Optional instance is empty.

        Returns:
            bool: True if the Optional instance is empty, False otherwise.

        """
        try:
            self._get_value()
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

    def __str__(self) -> str:
        """Get the string representation of the Optional class.

        Returns:
           str.

        """
        return str(self._get_value())

    def __repr__(self) -> str:
        """Get the string representation of the Optional class.

        Returns:
           str.

        """
        return f"<{self.__class__.__name__}({self._value}) at {hex(id(self))}>"

    def __float__(self) -> float:
        """Get the float representation of the Optional class.

        Returns:
           float.

        """
        return float(self._get_value())  # type: ignore[arg-type]

    def __int__(self) -> int:
        """Get the int representation of the Optional class.

        Returns:
           int.

        """
        return int(self._get_value())  # type: ignore[arg-type, call-overload]

    def __add__(self, other: "Optional[R]") -> "Optional[S]":
        """Add the values of two Optional objects.

        Args:
            other (Optional[R]): Another Optional object to add to this one.

        Returns:
            Optional[S]: An Optional object with the sum of the values, or an empty
                         Optional if either is empty.

        """
        return self.reduce(other, lambda a, b: a + b)  # type: ignore[operator]

    def __sub__(self, other: "Optional[R]") -> "Optional[S]":
        """Subtract the value of another Optional object from this one.

        Args:
            other (Optional[R]): Another Optional object to subtract from this one.

        Returns:
            Optional[S]: An Optional object with the difference of the values, or an
                         empty Optional if either is empty.

        """
        return self.reduce(other, lambda a, b: a - b)  # type: ignore[operator]

    def __mul__(self, other: "Optional[R]") -> "Optional[S]":
        """Multiplie the values of two Optional objects.

        Args:
            other (Optional[R]): Another Optional object to multiply with this one.

        Returns:
            Optional[S]: An Optional object with the product of the values, or an
                         empty Optional if either is empty.

        """
        return self.reduce(other, lambda a, b: a * b)  # type: ignore[operator]

    def __truediv__(self, other: "Optional[R]") -> "Optional[S]":
        """Divide the value of this Optional object by the value of another.

        Args:
            other (Optional[R]): Another Optional object to divide this one by.

        Returns:
            Optional[S]: An Optional object with the quotient of the values, or an empty
                         Optional if either is empty.

        """
        return self.reduce(other, lambda a, b: a / b)  # type: ignore[operator]

    def __floordiv__(self, other: "Optional[R]") -> "Optional[S]":
        """Perform floor division on the values of two Optional objects.

        Args:
            other (Optional[R]): Another Optional object to perform floor division with.

        Returns:
            Optional[S]: An Optional object with the floor division result, or an empty
                         Optional if either is empty.

        """
        return self.reduce(other, lambda a, b: a // b)  # type: ignore[operator]

    def __mod__(self, other: "Optional[R]") -> "Optional[S]":
        """Compute the modulo of the values of two Optional objects.

        Args:
            other (Optional[R]): Another Optional object to compute the modulo with.

        Returns:
            Optional[S]: An Optional object with the modulo result, or an empty Optional
                         if either is empty.

        """
        return self.reduce(other, lambda a, b: a % b)  # type: ignore[operator]

    def __pow__(self, other: "Optional[R]") -> "Optional[S]":
        """Raise the value of this Optional object to the power of the value of another.

        Args:
            other (Optional[R]): Another Optional object to use as the exponent.

        Returns:
            Optional[S]: An Optional object with the power result, or an empty Optional
                         if either is empty.

        """
        return self.reduce(other, lambda a, b: a**b)  # type: ignore[operator]

    def __eq__(self, value: object) -> bool:
        """Check for equality between two Optional instances.

        This method checks if the given value is an instance of Optional and if so,
        compares the values of both instances using the specified lambda function.

        Args:
            value (object): The value to compare against.

        Returns:
            bool: True if the values are not empty and equal, False otherwise.

        """
        return self.reduce(
            value if isinstance(value, Optional) else Optional(value=value),
            lambda a, b: a == b,
        ).get(default=False)

    def __lt__(self, value: object) -> bool:
        """Determine if this object is less than the given value.

        Args:
            value (object): The value to compare with.

        Returns:
            bool: True if this object is not empty and less than the given value,
            False otherwise.

        """
        return self.reduce(
            value if isinstance(value, Optional) else Optional(value=value),
            lambda a, b: a < b,
        ).get(default=False)

    def __le__(self, value: object) -> bool:
        """Determine if this object is less than or equal to the given value.

        Args:
            value (object): The value to compare with.

        Returns:
            bool: True if this object is not empty and less than or equal to the given
            value, False otherwise.

        """
        return self.reduce(
            value if isinstance(value, Optional) else Optional(value=value),
            lambda a, b: a <= b,
        ).get(default=False)

    def __gt__(self, value: object) -> bool:
        """Determine if this object is greater than the given value.

        Args:
            value (object): The value to compare with.

        Returns:
            bool: True if this object is not empty and greater than the given value,
            False otherwise.

        """
        return self.reduce(
            value if isinstance(value, Optional) else Optional(value=value),
            lambda a, b: a > b,
        ).get(default=False)

    def __ge__(self, value: object) -> bool:
        """Determine if this object is greater than or equal to the given value.

        Args:
            value (object): The value to compare with.

        Returns:
            bool: True if this object is not empty and greater than or equal to the given
            value, False otherwise.

        """
        return self.reduce(
            value if isinstance(value, Optional) else Optional(value=value),
            lambda a, b: a >= b,
        ).get(default=False)

    def _get_value(self) -> T | None:
        """Get the value of the Optional instance.

        Returns:
            T | None: The value of the Optional instance.

        Raises:
            MissingValueError: If the value is not present.

        """
        if self._is_empty(self._value):
            raise MissingValueError
        return self._value

    def get(self, exception: type[MissingValueError] = MissingValueError, **kwargs) -> T:  # noqa: ANN003
        """Get the value of the Optional instance, or a default value if not present.

        Args:
            exception (MissingValueError): The default exception
            kwargs (dict): The default value.

        Example:
            Optional(10).map(lambda x: x * 2).get(
                exception=CustomMissingValueError,
                default=42
            )

            Optional(10).map(lambda x: x * 2).get(default=42)

            Optional(10).map(lambda x: x * 2).get(exception=CustomMissingValueError)

        Returns:
            T: The value of the Optional instance, or the default value.

        Raises:
            MissingValueError: If the value is not present and no default value
            is provided.

        """
        try:
            value: T | None = self._get_value()
        except MissingValueError as err:
            try:
                return kwargs["default"]  # type: ignore[assignment]
            except KeyError:
                raise exception from err
        else:
            return value  # type: ignore[return-value]

    def get_or_else(self, callback: Callable[[], T]) -> T:
        """Get the value of the Optional instance, or a value provided by a function
        if not present.

        Args:
            callback (Callable[[], T]): The function to provide a value.

        Returns:
            T: The value of the Optional instance, or the value provided by the function.

        """
        try:
            return self._get_value()  # type: ignore[return-value]
        except MissingValueError:
            return callback()


class OptionalTransform(ABC, Generic[T, R], Optional[R]):
    """An abstract base class for transforming Optional values.

    Attributes:
        _parent (Optional): The parent optional value.
        _callback (Callable[[T], R]): The transformation function.

    """

    _parent: "Optional[Any]"
    _callback: Callable[..., R] | None = None

    def __init__(
        self, parent: Optional[T], callback: Callable[..., R] | None = None
    ) -> None:
        """Initialize the OptionalTransform instance.

        Args:
            parent (Optional): The parent Optional instance.
            callback (Callable[[T], R]): The transformation function.

        """
        self._parent = parent
        self._callback = callback

    def _is_empty(self, value: R | None) -> bool:
        """Test if parent value is empty.

        Returns:
            bool.

        """
        return self._parent._is_empty(value)

    def __repr__(self) -> str:
        """Get the string representation of the Optional class.

        Returns:
           str.

        """
        return f"{self._parent!r} >> <{self.__class__.__name__} at {hex(id(self))}>"

    @abstractmethod
    def _get_value(self) -> R | None:
        """Get the transformed value of the Optional instance.

        Returns:
            R | None: The transformed value of the Optional instance.

        """


class OptionalMap(OptionalTransform[T, R]):
    """A class for mapping Optional values."""

    def _get_value(self) -> R | None:
        """Run the transformation and return the result.

        Returns:
            R | None: The result of the transformation.

        """
        value: T | None = self._parent._get_value()
        new_value: R | None = self._callback(value)  # type: ignore[misc]
        if self._is_empty(new_value):
            raise MissingValueError
        return new_value  # type: ignore[misc]


class OptionalFilter(OptionalTransform[T, T]):
    """A class for filtering Optional values."""

    def _get_value(self) -> T | None:
        """Run the filter and return the result.

        Returns:
            T | None: The filtered result.

        """
        value: T | None = self._parent._get_value()
        if self._callback(value):  # type: ignore[misc]
            return value
        raise MissingValueError


class OptionalPeek(OptionalTransform[T, T]):
    """A class for peeking Optional values."""

    def _get_value(self) -> T | None:
        """Run the function and return the original value.

        Returns:
            T | None: The original value.

        """
        value: T | None = self._parent._get_value()
        self._callback(copy(value))  # type: ignore[misc]
        return value


class OptionalCache(OptionalTransform[T, T]):
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
                self._value: T | None = self._parent._get_value()
            finally:
                self._cached = True

        if not hasattr(self, "_value") or self._is_empty(self._value):
            raise MissingValueError
        return self._value


def optional(
    is_empty: Callable[[T | None], bool] = lambda x: x is None,
    catch: bool = True,  # noqa: FBT001, FBT002
) -> Callable[[Callable[..., T]], Callable[..., Optional]]:
    """Wrap a function and return an Optional object.

    Args:
        is_empty (Callable[[T | None], bool]): A function to determine if the value is
        considered empty. Default is a function that returns True if the value is None.

        catch (bool): If an error occurs during the execution of the wrapped function,
        an empty Optional is returned, default is True.

    Returns:
        Callable[[Callable[..., T]], Callable[..., Optional]]: The wrapped function that
        returns an Optional object.

    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional]:
        """Wrap the given function and returns an Optional object.

        Args:
            func (Callable[..., T]): The function to be wrapped.

        Returns:
            Callable[..., Optional]: The wrapped function that returns an Optional object.

        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional:  # noqa: ANN003,ANN002
            """Execute the wrapped function and returns an Optional object.

            Args:
                *args (Any): Positional arguments for the wrapped function.
                **kwargs (Any): Keyword arguments for the wrapped function.

            Returns:
                Optional: An Optional object wrapping the result of the function.

            """
            try:
                return Optional(value=func(*args, **kwargs), is_empty=is_empty)
            except:
                if catch:
                    return Optional()
                raise

        return wrapper

    return decorator
