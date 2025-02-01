# py-joptional

The Optional class represents an optional value that may or may not contain a value (implementing the Java Optional class in Python).

## Usage

This class can be used to safely and expressively manipulate optional values. It offers a variety of methods to transform, filter, and interact with the encapsulated value.

## Advantages

### *Safety*

The Optional class allows managing optional values without worrying about NoneType errors. Methods such as get and get_or_else ensure that values are handled safely.

### *Expressiveness*

With methods like map, flat_map, filter, peek, and if_present, the Optional class makes the code more readable and expressive. These methods make it easy to manipulate encapsulated values without constantly checking for their presence.

### *Method Chaining*

The ability to chain method calls allows for applying multiple successive operations in a fluid and concise manner. This improves code readability and reduces complexity.

### *Encapsulation*

The Optional class encapsulates the logic for handling optional values, making the code cleaner and more maintainable. It centralizes the checks and transformations in one place.

### *Interoperability*

The Optional class is compatible with generic types, making it possible to use it with any data type. It offers increased flexibility for handling different kinds of optional values.

### *Error Prevention*

Using Optional makes it harder to forget null checks, reducing the risk of errors and bugs related to missing values.

### *Lazy Evaluation*

The Optional class supports lazy evaluation, meaning that transformations and checks on the optional value are only performed when necessary. This can improve performance by avoiding unnecessary computations.

### *Caching*

The Optional class includes a cache method, which allows caching the value and returning a new Optional instance with the cached value. This is useful for ensuring that the value is computed only once and reused in subsequent operations, improving performance and efficiency.

## Example of Use

```python
from typing import Optional

# Initializing the Optional class with a value
optional = Optional(10)

# Getting the value or a default value
value_or_default = optional.get_or_else(lambda: 100)
print(f"Value or Default: {value_or_default}")  # Prints: Value or Default: 10

# Checking if the Optional contains a value
if optional: # idem "not optional.is_empty()"
    print(f"Value: {optional.get()}")  # Prints: Value: 10

# Applying a transformation to the value
mapped_value = optional.map(lambda x: x * 2)
print(f"Mapped Value: {mapped_value.get()}")  # Prints: Mapped Value: 20

# Filtering the value based on a condition
filtered_value = optional.filter(lambda x: x > 5)
print(f"Filtered Value: {filtered_value.get()}")  # Prints: Filtered Value: 10

# Applying a function without changing the value
optional.peek(lambda x: print(f"Peeking at: {x}"))  # Prints: Peeking at: 10

# Applying a transformation and flattening the result
flat_mapped_value = optional.flat_map(lambda x: Optional(x * 3))
print(f"Flat Mapped Value: {flat_mapped_value.get()}")  # Prints: Flat Mapped Value: 30

# Applying a function if the value is present
optional.if_present(lambda x: print(f"Present Value: {x}"))  # Prints: Present Value: 10

```

### Chained Method Calls Example
```python

# Chaining methods: map, filter, and peek
result = (
    Optional(10)
    .map(lambda x: x * 2)  # Transform the value by multiplying it by 2
    .cache()  # Cache the transformed value
    .filter(lambda x: x > 10)  # Filter the value to keep only values greater than 10
    .peek(lambda x: print(f"Peeking at: {x}"))  # Print the value without modifying it
    .flat_map(lambda x: Optional(x + 5))  # Flatten the transformation by adding 5 to the value
)

# Print the final value after chaining
print(f"Final Value: {result.get()}")  # Prints: Final Value: 25

```
