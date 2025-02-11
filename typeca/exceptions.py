from typing import Any, Type


class ArgumentTypeError(TypeError):
    def __init__(self, param_name: str, expected_type: type, param_value: Any):
        self.message = (f"Argument '{param_name}' must be of type {expected_type}, "
                        f"but got {type(param_value).__name__}")
        super().__init__(self.message)


class ReturnTypeError(TypeError):
    def __init__(self, return_type: Type, actual_type: Any):
        self.message = (f"Return value must be of type {return_type}, "
                        f"but got {actual_type.__name__}")
        super().__init__(self.message)
