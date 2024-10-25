# Typeca

**Typeca** is a lightweight Python decorator for enforcing type checks on both positional and keyword arguments with annotated types.

It ensures that arguments passed to functions and the function's return value match their specified types, 
raising a TypeError if any type mismatch is found.

## Features
* **Positional and Keyword Argument Checks**.
* **Flexible Enforcement**: Skips type checking for arguments without annotations, providing flexibility where needed.
* **Error Handling**: Raises a TypeError if a type mismatch is detected for either function args or the return value.

## Supported Types
* **Primitive Types**: Such as int, str, float, bool, and other built-in types.
* **Annotated Data Structures**:
    * list[T]: Checks that the value is a list and that every element conforms to type T.
    * dict[K, V]: Checks that the value is a dictionary, ensuring that each key has type K and each value has type V.
    * tuple[T1, T2, ...]: Checks that the value is a tuple, ensuring that each element matches the specified type (e.g., tuple[int, str] for (42, "answer")).

## Installation

## Usage
Use **@type_enforcer** to enforce type checks on your functions:

```python
from typeca import type_enforcer 

@type_enforcer
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
@type_enforcer
def add(a: int, b: int) -> int:
    return a + b

add(3, 4)  # Works fine
add(3, '4')  # Raises TypeError
```

### Example 2: Complex Data Structures

Supports lists, dictionaries, and tuples with type annotations:

```python
@type_enforcer
def process_items(items: list[int]) -> list[int]:
    return [item * 2 for item in items]

process_items([1, 2, 3])  # Works fine
process_items(['a', 'b', 'c'])  # Raises TypeError
```