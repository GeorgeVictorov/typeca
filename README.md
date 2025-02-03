# Typeca

**Typeca** is a Python decorator for enforcing type checks on both positional and keyword arguments
on functions with annotated types.

It ensures that arguments passed to functions and the function's return value match their specified types,
raising a TypeError if any type mismatch is found.

P.S. Anyway, this decorator would negatively affect a function`s performance, so the best approach would be to use it
during development and testing phases.

```python
%timeit -n 10 -r 7 gen_array(1_000_000)
48 ms ± 1.36 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

%timeit -n 10 -r 7 gen_array_type_enforced(1_000_000)
424 ms ± 34.2 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
```

## Supported Python Versions

* Python 3.10 and later.

## Features

* **Flexible Enforcement**: Skips type checking for arguments without annotations.
* **Nested Annotation Check**: The decorator supports recursive type checking for nested data structures.
* **Configurable Cache Size**: Uses a cache to store function signatures, with a configurable maxsize parameter (default
  is 64).
* **Enable/Disable Type Checking**: Users can enable or disable type enforcement on a function by using the enable
  parameter, defaults to True.
* **Error Handling**: Raises a TypeError if a type mismatch is detected for either function args or the return value.

## Supported Types

* **Standard Types**: Such as int, str, float, bool, and other built-in types.
* **Annotated Data Structures**:
    1. **list[T]**: Checks that the value is a list and that every element conforms to type T.
    2. **dict[K, V]**: Checks that the value is a dictionary, and that each key has type K and each value has type V.
    3. **tuple[T1, T2, ...]**: Checks that the value is a tuple, and that each element has specified type (e.g.,
       tuple[int, str] for (41, 'Saturday')).
    4. **set[T]**: Checks that the value is a set and that every element conforms to type T.
    5. **frozenset[T]**: Checks that the value is a frozenset and that every element conforms to type T.
* **Type Combinations**:
    1. **Union[T1, T2, ...]**: Checks if the value matches one of the types in the Union, e.g., Union[int, str] would
       accept both int and str. (Supports both traditional Union from typing and the new | syntax introduced in Python
       3.10)
    2. **Optional[T]**: Equivalent to Union[T, None], checks that the value is either None or matches type T.

## Installation

```bash
pip install typeca
```

## Usage

Use **@TypeEnforcer** to enforce type checks on your functions:

```python
from typeca import TypeEnforcer


@TypeEnforcer()
def two_num_product(a: int, b: int) -> int:
    return a * b


two_num_product(2, 3)  # Output: 6

two_num_product(2, '3')  # Raises TypeError
```

## Examples

### Example 1: Simple Type Enforcement

```python
@TypeEnforcer()
def add(a: int, b: int) -> int:
    return a + b


add(3, 4)  # Works fine

add(3, '4')  # Raises TypeError
```

### Example 2: Complex Data Structures

Supports lists, dictionaries, and tuples with type annotations:

```python
@TypeEnforcer()
def process_items(items: list[int]) -> list[int]:
    return [item * 2 for item in items]


process_items([1, 2, 3])  # Works fine

process_items(['a', 'b', 'c'])  # Raises TypeError
```

### Example 3: Disable Type Enforcement

At any moment you can disable check to improve performance of the function:

```python
@TypeEnforcer(enable=False)
def process_array(*args) -> list[int]:
    return list(args) * 2


process_array(1, 2, 3)  # Works without type enforcement
```

### Example 4: Custom Cache Size

The TypeEnforcer decorator will cache up to 128 unique signatures for process_data:

```python
@TypeEnforcer(maxsize=128)
def process_data(x: int, y: int) -> int:
    return x + y


process_data(5, 10)  # Type enforcement applies, returns 15

process_data("5", "10")  # Raises TypeError
```

### Example 5: Using frozenset

```python
@TypeEnforcer()
def unique_numbers(data: frozenset[int]) -> frozenset[int]:
    return frozenset([n * 2 for n in data])


unique_numbers(frozenset({1, 2, 3}))  # Returns: frozenset({2, 4, 6})

unique_numbers(frozenset({1, 2, "3"}))  # Raises TypeError
```

### Example 6: Using Union with | syntax

```python
@TypeEnforcer()
def process_value(value: int | str) -> str:
    return f"Processed: {value}"


process_value(42)  # Returns: "Processed: 42"
process_value("hello")  # Returns: "Processed: hello"

process_value([1, 2, 3])  # Raises TypeError
```