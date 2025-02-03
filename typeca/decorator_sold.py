from abc import ABC, abstractmethod
from typing import Any, Type, get_args


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
        return isinstance(value, expected_type)


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
        return all(checker.check_type(value, elem_type) for v in value)


class SetChecker(BaseSetChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, set)


class FrozenSetChecker(BaseSetChecker):
    def __init__(self, factory: TypeCheckerFactory):
        super().__init__(factory, frozenset)
