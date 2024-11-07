from functools import lru_cache, wraps
from inspect import Signature, signature
from typing import Any, Type, Union, get_args, get_origin


def get_signature_and_hints(func) -> tuple[dict, Signature]:
    """
    Get type annotations and signature of a func.

    Args:
        func (Callable): func to be decorated.

    Returns:
        tuple[dict, Signature]: A tuple containing dict of type annotations and signature of a func.
    """
    hints = func.__annotations__
    sig = signature(func)
    return hints, sig


def check_type(value: Any, expected_type: Type) -> bool:
    """
    Check if value matches expected type.

    Args:
        value (Any): value to be checked.
        expected_type (Type): expected type.

    Returns:
        bool: True if value matches expected type.
    """
    origin_type = get_origin(expected_type)

    if origin_type is None:
        return isinstance(value, expected_type)

    type_checkers = {
        list: lambda val, typ: isinstance(val, list) and all(check_type(v, typ[0]) for v in val),
        dict: lambda val, typ: isinstance(val, dict) and all(
            check_type(k, typ[0]) for k in val) and all(
            check_type(v, typ[1]) for v in val.values()),
        tuple: lambda val, typ: isinstance(val, tuple) and len(val) == len(typ) and all(
            check_type(v, t) for v, t in zip(val, typ)),
        set: lambda val, typ: isinstance(val, set) and all(check_type(v, typ[0]) for v in val),
        frozenset: lambda val, typ: isinstance(val, frozenset) and all(
            check_type(v, typ[0]) for v in val),
        Union: lambda val, typ: any(check_type(val, t) for t in typ),
    }

    if origin_type in type_checkers:
        args = get_args(expected_type)
        return type_checkers[origin_type](value, args)

    return True  # return True for unsupported types


def check_args_types(func, hints: dict, sig: Signature, args: tuple, kwargs: dict):
    """
    Check types of function arguments.

    Args:
        func (Callable): function to be decorated.
        hints (dict): dict of type annotations.
        sig (Signature): signature of the function.
        args (tuple): args of function.
        kwargs (dict): kwargs of function.

    Raises:
        TypeError: if args and kwargs have different types.
    """
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    for param_name, param_value in bound_args.arguments.items():
        expected_type = hints.get(param_name)
        if expected_type and not check_type(param_value, expected_type):
            raise TypeError(f"Argument '{param_name}' must be of type {expected_type}, "
                            f"but got {type(param_value).__name__}")


def check_return_types(result: Any, return_type: Type):
    """
    Check return type of result.

    Args:
        result (Any): result of function.
        return_type (Type): expected type.

    Raises:
        TypeError: if result is not of expected type.
    """
    if return_type and not check_type(result, return_type):
        raise TypeError(f'Return value must be of type {return_type}, '
                        f'but got {type(result).__name__}')


def type_enforcer(maxsize: int = 64, enable: bool = True):
    """
    Decorator to enforce type checking on function arguments and return types.

    Args:
        maxsize (int): maximum size of the cache for storing function signatures.
        enable (bool): enable type checking.

    Returns:
        Callable: decorated function.

    Notes:
        Maxsize defaults to 64.
        Enable defaults to True.
        If enable is False, the decorator returns the original function unchanged.
    """
    get_cached_signature_and_hints = lru_cache(maxsize=maxsize)(get_signature_and_hints)

    def decorator(func):
        if not enable:
            return func

        hints, sig = get_cached_signature_and_hints(func)
        return_type = hints.get('return')

        @wraps(func)
        def wrapper(*args, **kwargs):
            check_args_types(func, hints, sig, args, kwargs)
            result = func(*args, **kwargs)
            check_return_types(result, return_type)

            return result

        return wrapper

    return decorator
