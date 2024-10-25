import unittest
from src.decorator import type_enforcer


class TestEnforceTypes(unittest.TestCase):

    def test_correct_simple_types(self):
        @type_enforcer
        def add(a: int, b: int) -> int:
            return a + b

        self.assertEqual(add(3, 4), 7)

    def test_correct_list_type(self):
        @type_enforcer
        def double_values(values: list[int]) -> list[int]:
            return [v * 2 for v in values]

        self.assertEqual(double_values([1, 2, 3]), [2, 4, 6])

    def test_incorrect_list_type(self):
        @type_enforcer
        def double_values(values: list[int]) -> list[int]:
            return [v * 2 for v in values]

        with self.assertRaises(TypeError) as context:
            double_values(["a", "b", "c"])
        self.assertIn("Argument 'values' must be of type list[int]", str(context.exception))

    def test_correct_dict_type(self):
        @type_enforcer
        def invert_dict(d: dict[str, int]) -> dict[int, str]:
            return {v: k for k, v in d.items()}

        self.assertEqual(invert_dict({"one": 1, "two": 2}), {1: "one", 2: "two"})

    def test_incorrect_dict_key_type(self):
        @type_enforcer
        def invert_dict(d: dict[str, int]) -> dict[int, str]:
            return {v: k for k, v in d.items()}

        with self.assertRaises(TypeError) as context:
            invert_dict({1: "one", 2: "two"})
        self.assertIn("Argument 'd' must be of type dict[str, int]", str(context.exception))

    def test_incorrect_dict_value_type(self):
        @type_enforcer
        def invert_dict(d: dict[str, int]) -> dict[int, str]:
            return {v: k for k, v in d.items()}

        with self.assertRaises(TypeError) as context:
            invert_dict({"one": "1", "two": "2"})
        self.assertIn("Argument 'd' must be of type dict[str, int]", str(context.exception))

    def test_incorrect_return_list_type(self):
        @type_enforcer
        def get_strings() -> list[str]:
            return [1, 2, 3]

        with self.assertRaises(TypeError) as context:
            get_strings()
        self.assertIn("Return value must be of type list[str]", str(context.exception))

    def test_incorrect_return_dict_type(self):
        @type_enforcer
        def get_str_int_map() -> dict[str, int]:
            return {"a": "1", "b": "2"}

        with self.assertRaises(TypeError) as context:
            get_str_int_map()
        self.assertIn("Return value must be of type dict[str, int]", str(context.exception))

    def test_correct_tuple_type(self):
        @type_enforcer
        def process_data(data: tuple[int, str]) -> tuple[str, int]:
            num, text = data
            return text, num

        self.assertEqual(process_data((42, "answer")), ("answer", 42))

    def test_incorrect_tuple_argument_type(self):
        @type_enforcer
        def process_data(data: tuple[int, str]) -> tuple[str, int]:
            num, text = data
            return text, num

        with self.assertRaises(TypeError) as context:
            process_data((42, 42))
        self.assertIn("Argument 'data' must be of type tuple[int, str]", str(context.exception))

    def test_incorrect_tuple_return_type(self):
        @type_enforcer
        def process_data(data: tuple[int, str]) -> tuple[str, int]:
            num, text = data
            return num, text

        with self.assertRaises(TypeError) as context:
            process_data((42, "answer"))
        self.assertIn("Return value must be of type tuple[str, int]", str(context.exception))
