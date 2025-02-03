from abc import ABC, abstractmethod
from typing import Type


class TypeChecker(ABC):
    @abstractmethod
    def check_type(self, expected_type: Type) -> bool:
        pass

