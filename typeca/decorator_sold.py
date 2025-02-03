from abc import ABC, abstractmethod
from inspect import Signature, signature
from typing import Any, Type, get_args, Union, get_origin
from functools import lru_cache, wraps


class TypeChecker(ABC):
    @abstractmethod
    def check_type(self, value: Any, expected_type: Type) -> bool:
        pass


class TypeCheckerFactory(ABC):
    @abstractmethod
    def get_checker(self, expected_type: Type) -> TypeChecker:
        pass


class StandardTypeChecker(TypeChecker):
    def check_type(self, value: Any, expected_type: Type) -> bool:
        origin_type = get_origin(expected_type)
        if origin_type is None:
            return isinstance(value, expected_type)
        return True


class ListChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        if not isinstance(value, list):
            return False
        elem_type = get_args(expected_type)[0]
        checker = self.factory.get_checker(elem_type)
        return all(checker.check_type(v, elem_type) for v in value)


class DictChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        if not isinstance(value, dict):
            return False
        key_type, value_type = get_args(expected_type)
        key_checker = self.factory.get_checker(key_type)
        value_checker = self.factory.get_checker(value_type)
        return all(key_checker.check_type(key, key_type) for key in value) and \
            all(value_checker.check_type(v, value_type) for v in value.values())


class TupleChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        if not isinstance(value, tuple):
            return False
        expected_types = get_args(expected_type)
        return isinstance(value, tuple) and len(expected_types) == len(value) and \
            all(self.factory.get_checker(t).check_type(v, t) for v, t in zip(value, expected_types))


class BaseSetChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory, expected_cls: Type):
        self.factory = factory
        self.expected_cls = expected_cls

    def check_type(self, value: Any, expected_type: Type) -> bool:
        if not isinstance(value, self.expected_cls):
            return False
        elem_type = get_args(expected_type)[0]
        checker = self.factory.get_checker(elem_type)
        return all(checker.check_type(v, elem_type) for v in value)


class SetChecker(BaseSetChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, set)


class FrozenSetChecker(BaseSetChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, frozenset)


class UnionChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        return any(
            self.factory.get_checker(t).check_type(value, t) for t in get_args(expected_type))


class DefaultTypeCheckerFactory(TypeCheckerFactory):
    def __init__(self):
        self.checkers = {
            list: ListChecker(self),
            dict: DictChecker(self),
            tuple: TupleChecker(self),
            set: SetChecker(self),
            frozenset: FrozenSetChecker(self),
            Union: UnionChecker(self)
        }

    def get_checker(self, expected_type: Type) -> TypeChecker:
        origin_type = get_origin(expected_type)

        if origin_type in self.checkers:
            return self.checkers[origin_type]

        return StandardTypeChecker()


class SignatureHelper:
    @staticmethod
    def get_signature_and_hints(func) -> tuple[dict, Signature]:
        hints = func.__annotations__
        sig = signature(func)
        return hints, sig

    @staticmethod
    def check_args_types(func, hints: dict[str, Type], sig: Signature, args: tuple, kwargs: dict,
                         factory: TypeCheckerFactory):
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_value in bound_args.arguments.items():
            expected_type = hints.get(param_name)
            if expected_type and not factory.get_checker(expected_type).check_type(param_value,
                                                                                   expected_type):
                raise TypeError(f"Argument '{param_name}' must be of type {expected_type}, "
                                f"but got {type(param_value).__name__}")

    @staticmethod
    def check_return_type(result: Any, return_type: Type, factory: TypeCheckerFactory):
        if return_type and not factory.get_checker(return_type).check_type(result, return_type):
            raise TypeError(f'Return value must be of type {return_type}, '
                            f'but got {type(result).__name__}')


class TypeEnforcer:
    def __init__(self,
                 factory: TypeCheckerFactory = None,
                 maxsize: int = 64,
                 enable: bool = True):
        self.factory = factory if factory else DefaultTypeCheckerFactory()
        self.enable = enable
        self.get_cached_signature_and_hints = lru_cache(maxsize=maxsize)(
            SignatureHelper.get_signature_and_hints)

    def __call__(self, func):
        if not self.enable:
            return func

        hints, sig = self.get_cached_signature_and_hints(func)
        return_type = hints.get('return')

        @wraps(func)
        def wrapper(*args, **kwargs):
            SignatureHelper.check_args_types(func, hints, sig, args, kwargs, self.factory)
            result = func(*args, **kwargs)
            SignatureHelper.check_return_type(result, return_type, self.factory)
            return result

        return wrapper
