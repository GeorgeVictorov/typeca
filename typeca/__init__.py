"""
Typeca: A package for type enforcement in Python functions.
"""

from typeca.decorator import TypeEnforcer

type_enforcer = TypeEnforcer()

type_enforcer.__doc__ = """
Typeca: A decorator for enforcing type checks on function args and return values.

Ensures function calls match expected types based on annotations.
Raises TypeError on type mismatches.

Args:
    maxsize (int, default=64): Cache size for function signatures.
    enable (bool, default=True): Whether type enforcement is active.
"""

__all__ = ['type_enforcer']
