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
        return all(checker.check_type(value, elem_type) for value in value)
