# Typeca

**Typeca** is a Python decorator for enforcing type checks on both positional and keyword arguments
on functions with annotated types.

It ensures that arguments passed to functions and the function's return value match their specified types, 
raising a TypeError if any type mismatch is found.

P.S. Anyway, this decorator would negatively affect a function`s performance, so the best approach would be to use it 
during development and testing phases.

```python
%timeit -n 10 -r 7 gen_array(1_000_000)
50.5 ms ± 1.53 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

%timeit -n 10 -r 7 gen_array_type_enforced(1_000_000)
474 ms ± 14.9 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
```

## Supported Python Versions
* Python 3.9 and later.

## Features
* **Flexible Enforcement**: Skips type checking for arguments without annotations.
* **Nested Annotation Check**: The decorator supports recursive type checking for nested data structures.
* **Enable/Disable Type Checking**: Users can enable or disable type enforcement on a function by using the enable parameter, defaults to True.
* **Error Handling**: Raises a TypeError if a type mismatch is detected for either function args or the return value.

## Supported Types
* **Standard Types**: Such as int, str, float, bool, and other built-in types.
* **Annotated Data Structures**:
  1. **list[T]**: Checks that the value is a list and that every element conforms to type T.
  2. **dict[K, V]**: Checks that the value is a dictionary, and that each key has type K and each value has type V.
  3. **tuple[T1, T2, ...]**: Checks that the value is a tuple, and that each element has specified type (e.g., tuple[int, str] for (41, 'Saturday')).

## Installation

```bash
pip install typeca
```

## Usage
Use **@type_enforcer** to enforce type checks on your functions:

```python
from typeca import type_enforcer 

@type_enforcer()
def two_num_product(a: int, b: int) -> int:
    return a * b

# Valid usage
print(two_num_product(2, 3))  # Output: 6

# Invalid usage
print(two_num_product(2, '3'))  # Raises TypeError
```

## Examples
### Example 1: Simple Type Enforcement

```python
@type_enforcer()
def add(a: int, b: int) -> int:
    return a + b

add(3, 4)  # Works fine
add(3, '4')  # Raises TypeError
```

### Example 2: Complex Data Structures

Supports lists, dictionaries, and tuples with type annotations:

```python
@type_enforcer()
def process_items(items: list[int]) -> list[int]:
    return [item * 2 for item in items]

process_items([1, 2, 3])  # Works fine
process_items(['a', 'b', 'c'])  # Raises TypeError
```

### Example 3: Disable Type Enforcement

At any moment you can disable check to improve performance of the function:
```python
@type_enforcer(enable=False)
def process_array(*args) -> list[int]:
    return list(args) * 2

process_array(1, 2, 3) # Works without type enforcement
```