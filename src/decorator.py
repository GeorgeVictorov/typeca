from functools import wraps
from inspect import signature
from typing import get_type_hints, get_origin, get_args


def check_type(value, expected_type):
    if get_origin(expected_type) is None:
        return isinstance(value, expected_type)

    origin_type = get_origin(expected_type)

    if origin_type is list:
        item_type = get_args(expected_type)[0]
        return isinstance(value, list) and all(isinstance(item, item_type) for item in value)

    elif origin_type is dict:
        key_type, val_type = get_args(expected_type)
        return (
                isinstance(value, dict) and
                all(isinstance(k, key_type) for k in value.keys()) and
                all(isinstance(v, val_type) for v in value.values())
        )

    elif origin_type is tuple:
        item_types = get_args(expected_type)
        return (
                isinstance(value, tuple) and
                len(value) == len(item_types) and
                all(isinstance(item, item_type) for item, item_type in zip(value, item_types))
        )

    return False


def check_args_types(func, args, kwargs):
    hints = get_type_hints(func)
    sig = signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    for param_name, param_value in bound_args.arguments.items():
        expected_type = hints.get(param_name)
        if expected_type and not check_type(param_value, expected_type):
            raise TypeError(f"Argument '{param_name}' must be of type {expected_type}, "
                            f"but got {type(param_value).__name__}")


def check_return_types(func, result):
    return_type = get_type_hints(func).get('return')
    if return_type and not check_type(result, return_type):
        raise TypeError(f'Return value must be of type {return_type}, '
                        f'but got {type(result).__name__}')


def type_enforcer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        check_args_types(func, args, kwargs)
        result = func(*args, **kwargs)
        check_return_types(func, result)
        return result

    return wrapper
