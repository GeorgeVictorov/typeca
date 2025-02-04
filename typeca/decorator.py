from abc import ABC, abstractmethod
from functools import lru_cache, wraps
from inspect import Signature, signature
from typing import Any, Type, Union, get_args, get_origin


class TypeChecker(ABC):
    @abstractmethod
    def check_type(self, value: Any, expected_type: Type) -> bool:
        pass


class TypeCheckerFactory(ABC):
    @abstractmethod
    def get_checker(self, expected_type: Type) -> TypeChecker:
        pass


class SignatureHelperFactory(ABC):
    @abstractmethod
    def get_signature_and_hints(self, func) -> tuple[dict, Signature]:
        pass

    @abstractmethod
    def check_args_types(self, func, hints: dict[str, Type], sig: Signature, args: tuple,
                         kwargs: dict):
        pass

    @abstractmethod
    def check_return_type(self, result: Any, return_type: Type):
        pass


class SignatureInfoInterface(ABC):
    @abstractmethod
    def _get_signature(self, func) -> Signature:
        pass

    @abstractmethod
    def _get_hints(self, func) -> dict[str, Type]:
        pass

    @abstractmethod
    def get_signature_and_hints(self, func) -> tuple[dict, Signature]:
        pass


class ArgsTypeCheckerInterface(ABC):
    @abstractmethod
    def check_args_types(self, func, hints: dict[str, Type], sig: Signature, args: tuple,
                         kwargs: dict):
        pass


class ReturnTypeCheckerInterface(ABC):
    @abstractmethod
    def check_return_type(self, result: Any, return_type: Type):
        pass


class StandardTypeChecker(TypeChecker):
    def check_type(self, value: Any, expected_type: Type) -> bool:
        origin_type = get_origin(expected_type)
        if origin_type is None:
            return isinstance(value, expected_type)
        return True


class BaseArrayChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory, expected_cls: Type):
        self.factory = factory
        self.expected_cls = expected_cls

    def check_type(self, value: Any, expected_type: Type) -> bool:
        elem_type = get_args(expected_type)[0]
        checker = self.factory.get_checker(elem_type)
        return all(checker.check_type(v, elem_type) for v in value)


class ListChecker(BaseArrayChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, list)


class SetChecker(BaseArrayChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, set)


class FrozenSetChecker(BaseArrayChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, frozenset)


class DictChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        key_type, value_type = get_args(expected_type)
        key_checker = self.factory.get_checker(key_type)
        value_checker = self.factory.get_checker(value_type)
        return all(key_checker.check_type(key, key_type) for key in value) and \
            all(value_checker.check_type(v, value_type) for v in value.values())


class TupleChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        expected_types = get_args(expected_type)
        return isinstance(value, tuple) and len(expected_types) == len(value) and \
            all(self.factory.get_checker(t).check_type(v, t) for v, t in zip(value, expected_types))


class UnionChecker(TypeChecker):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_type(self, value: Any, expected_type: Type) -> bool:
        if value is None and type(None) in get_args(expected_type):
            return True
        return any(
            self.factory.get_checker(t).check_type(value, t) for t in get_args(expected_type))


class DefaultTypeCheckerFactory(TypeCheckerFactory):
    def __init__(self):
        self.checkers = {}
        self._register_builtin_checkers()

    def _register_builtin_checkers(self):
        self.register_checker(list, ListChecker(self))
        self.register_checker(dict, DictChecker(self))
        self.register_checker(tuple, TupleChecker(self))
        self.register_checker(set, SetChecker(self))
        self.register_checker(frozenset, FrozenSetChecker(self))
        self.register_checker(Union, UnionChecker(self))

    def register_checker(self, type_key: Type, checker: TypeChecker):
        self.checkers[type_key] = checker

    def get_checker(self, expected_type: Type) -> TypeChecker:
        origin_type = get_origin(expected_type)

        if origin_type in self.checkers:
            return self.checkers[origin_type]

        return StandardTypeChecker()


class SignatureInfo(SignatureInfoInterface):
    def _get_signature(self, func) -> Signature:
        return signature(func)

    def _get_hints(self, func) -> dict[str, Type]:
        return func.__annotations__

    def get_signature_and_hints(self, func) -> tuple[dict, Signature]:
        hints = self._get_hints(func)
        sig = self._get_signature(func)
        return hints, sig


class ArgsTypeChecker(ArgsTypeCheckerInterface):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_args_types(self, func, hints: dict[str, Type], sig: Signature, args: tuple,
                         kwargs: dict):
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_value in bound_args.arguments.items():
            expected_type = hints.get(param_name)
            if expected_type and not self.factory.get_checker(expected_type).check_type(
                    param_value, expected_type):
                raise TypeError(f"Argument '{param_name}' must be of type {expected_type}, "
                                f"but got {type(param_value).__name__}")


class ReturnTypeChecker(ReturnTypeCheckerInterface):
    def __init__(self, factory: TypeCheckerFactory):
        self.factory = factory

    def check_return_type(self, result: Any, return_type: Type) -> bool:
        if return_type and not self.factory.get_checker(return_type).check_type(result,
                                                                                return_type):
            raise TypeError(f'Return value must be of type {return_type}, '
                            f'but got {type(result).__name__}')


class SignatureExtractor:
    def __init__(self, signature_info: SignatureInfoInterface):
        self.signature_info = signature_info

    def extract(self, func) -> tuple[dict, Signature]:
        return self.signature_info.get_signature_and_hints(func)


class TypeValidator:
    def __init__(self,
                 arg_checker: ArgsTypeCheckerInterface,
                 return_checker: ReturnTypeCheckerInterface):
        self.arg_checker = arg_checker
        self.return_checker = return_checker

    def validate_args(self, func, hints: dict[str, Type], sig: Signature, args: tuple,
                      kwargs: dict):
        self.arg_checker.check_args_types(func, hints, sig, args, kwargs)

    def validate_return(self, result: Any, return_type: Type):
        self.return_checker.check_return_type(result, return_type)


class SignatureHelper:
    def __init__(self,
                 signature_extractor: SignatureExtractor,
                 type_validator: TypeValidator):
        self.signature_extractor = signature_extractor
        self.type_validator = type_validator

    def get_signature_and_hints(self, func) -> tuple[dict, Signature]:
        return self.signature_extractor.extract(func)

    def check_args_types(self, func, hints: dict[str, Type], sig: Signature, args: tuple,
                         kwargs: dict):
        self.type_validator.validate_args(func, hints, sig, args, kwargs)

    def check_return_type(self, result: Any, return_type: Type):
        self.type_validator.validate_return(result, return_type)


class SignatureCacheManager:
    def __init__(self, signature_helper: SignatureHelperFactory, maxsize: int = 64):
        self.get_cached_signature_and_hints = lru_cache(maxsize=maxsize)(
            signature_helper.get_signature_and_hints
        )


class TypeEnforcer:
    _instance = None

    def __new__(cls, maxsize: int = 64, enable: bool = True):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(maxsize, enable)
        return cls._instance

    def _init(self, maxsize: int = 64, enable: bool = True):
        self.maxsize = maxsize
        self.enable = enable

        factory = DefaultTypeCheckerFactory()
        signature_info = SignatureInfo()
        arg_checker = ArgsTypeChecker(factory)
        return_checker = ReturnTypeChecker(factory)

        signature_extractor = SignatureExtractor(signature_info)
        type_validator = TypeValidator(arg_checker, return_checker)

        signature_helper = SignatureHelper(signature_extractor, type_validator)
        self.signature_cache = SignatureCacheManager(signature_helper, maxsize)
        self.signature_helper = signature_helper

    def __call__(self, func):
        if not self.enable:
            return func

        hints, sig = self.signature_cache.get_cached_signature_and_hints(func)
        return_type = hints.get('return')

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.signature_helper.check_args_types(func, hints, sig, args, kwargs)
            result = func(*args, **kwargs)
            self.signature_helper.check_return_type(result, return_type)
            return result

        return wrapper
