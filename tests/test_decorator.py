import unittest
from typing import Dict, List, Tuple

from typeca import type_enforcer


class TestEnforceTypes(unittest.TestCase):

    def test_correct_simple_types(self):
        @type_enforcer()
        def add(a: int, b: int) -> int:
            return a + b

        self.assertEqual(add(3, 4), 7)

    def test_correct_list_type(self):
        @type_enforcer()
        def double_values(values: list[int]) -> list[int]:
            return [v * 2 for v in values]

        self.assertEqual(double_values([1, 2, 3]), [2, 4, 6])

    def test_incorrect_list_type(self):
        @type_enforcer()
        def double_values(values: list[int]) -> list[int]:
            return [v * 2 for v in values]

        with self.assertRaises(TypeError) as context:
            double_values(["a", "b", "c"])
        self.assertIn("Argument 'values' must be of type list[int]", str(context.exception))

    def test_correct_dict_type(self):
        @type_enforcer()
        def invert_dict(d: dict[str, int]) -> dict[int, str]:
            return {v: k for k, v in d.items()}

        self.assertEqual(invert_dict({"one": 1, "two": 2}), {1: "one", 2: "two"})

    def test_incorrect_dict_key_type(self):
        @type_enforcer()
        def invert_dict(d: dict[str, int]) -> dict[int, str]:
            return {v: k for k, v in d.items()}

        with self.assertRaises(TypeError) as context:
            invert_dict({1: "one", 2: "two"})
        self.assertIn("Argument 'd' must be of type dict[str, int]", str(context.exception))

    def test_incorrect_dict_value_type(self):
        @type_enforcer()
        def invert_dict(d: dict[str, int]) -> dict[int, str]:
            return {v: k for k, v in d.items()}

        with self.assertRaises(TypeError) as context:
            invert_dict({"one": "1", "two": "2"})
        self.assertIn("Argument 'd' must be of type dict[str, int]", str(context.exception))

    def test_incorrect_return_list_type(self):
        @type_enforcer()
        def get_strings() -> list[str]:
            return [1, 2, 3]

        with self.assertRaises(TypeError) as context:
            get_strings()
        self.assertIn("Return value must be of type list[str]", str(context.exception))

    def test_incorrect_return_dict_type(self):
        @type_enforcer()
        def get_str_int_map() -> dict[str, int]:
            return {"a": "1", "b": "2"}

        with self.assertRaises(TypeError) as context:
            get_str_int_map()
        self.assertIn("Return value must be of type dict[str, int]", str(context.exception))

    def test_correct_tuple_type(self):
        @type_enforcer()
        def process_data(data: tuple[int, str]) -> tuple[str, int]:
            num, text = data
            return text, num

        self.assertEqual(process_data((42, "answer")), ("answer", 42))

    def test_incorrect_tuple_argument_type(self):
        @type_enforcer()
        def process_data(data: tuple[int, str]) -> tuple[str, int]:
            num, text = data
            return text, num

        with self.assertRaises(TypeError) as context:
            process_data((42, 42))
        self.assertIn("Argument 'data' must be of type tuple[int, str]", str(context.exception))

    def test_incorrect_tuple_return_type(self):
        @type_enforcer()
        def process_data(data: tuple[int, str]) -> tuple[str, int]:
            num, text = data
            return num, text

        with self.assertRaises(TypeError) as context:
            process_data((42, "answer"))
        self.assertIn("Return value must be of type tuple[str, int]", str(context.exception))

    def test_one_elem_tuple(self):
        @type_enforcer()
        def process_data(data: tuple[int]) -> tuple[int, int]:
            return data * 2

        self.assertEqual(process_data((1,)), (1, 1))

    def test_empty_list(self):
        @type_enforcer()
        def return_empty_list() -> list[int]:
            return []

        self.assertEqual(return_empty_list(), [])

    def test_empty_dict(self):
        @type_enforcer()
        def return_empty_dict() -> dict[str, int]:
            return {}

        self.assertEqual(return_empty_dict(), {})

    def test_nested_dicts(self):
        @type_enforcer()
        def process_nested(data: list[dict[str, int]]) -> list[int]:
            return [d['value'] for d in data]

        self.assertEqual(process_nested([{"value": 1}, {"value": 2}]), [1, 2])

    def test_decorator_disabled(self):
        @type_enforcer(enable=False)
        def add(a: int, b: int) -> int:
            return a + b

        self.assertEqual(add(3, 4), 7)

    def test_invalid_return_type(self):
        @type_enforcer()
        def returns_dict() -> dict[str, int]:
            return [1, 2, 3]  # Incorrect return type

        with self.assertRaises(TypeError) as context:
            returns_dict()
        self.assertIn("Return value must be of type dict[str, int]", str(context.exception))

    def test_complex_nested_dicts(self):
        @type_enforcer()
        def extract_values(data: dict[str, dict[str, list[int]]]) -> list[int]:
            return [value for subdict in data.values() for value in subdict["values"]]

        self.assertEqual(
            extract_values({
                "a": {"values": [1, 2, 3]},
                "b": {"values": [4, 5, 6]}
            }),
            [1, 2, 3, 4, 5, 6]
        )

    def test_nested_lists(self):
        @type_enforcer()
        def flatten(data: list[list[int]]) -> list[int]:
            return [num for sublist in data for num in sublist]

        self.assertEqual(flatten([[1, 2], [3, 4]]), [1, 2, 3, 4])

    def test_combined_structures(self):
        @type_enforcer()
        def process_combined(data: list[dict[str, list[tuple[str, int]]]]) -> dict[str, int]:
            result = {}
            for item in data:
                for name, value in item["pairs"]:
                    result[name] = result.get(name, 0) + value
            return result

        self.assertEqual(
            process_combined([
                {"pairs": [("a", 1), ("b", 2)]},
                {"pairs": [("a", 3), ("c", 4)]}
            ]),
            {"a": 4, "b": 2, "c": 4}
        )

    def test_list_of_nested_dicts(self):
        @type_enforcer()
        def process_items(items: list[dict[str, list[int]]]) -> list[int]:
            return [num for item in items for num in item["values"]]

        self.assertEqual(
            process_items([
                {"values": [1, 2]},
                {"values": [3, 4]}
            ]),
            [1, 2, 3, 4]
        )

    def test_prev_annot_style(self):
        @type_enforcer()
        def process_data(data: Tuple[int]) -> Tuple[int, int]:
            return data * 2

        self.assertEqual(process_data((1,)), (1, 1))

    def test_prev_annot_style_incorrect_type(self):
        @type_enforcer()
        def process_data(data: Tuple[int]) -> Tuple[int, int]:
            return data * 2

        with self.assertRaises(TypeError):
            process_data(1)

    def test_prev_annot_correct_list_type(self):
        @type_enforcer()
        def double_values(values: List[int]) -> List[int]:
            return [v * 2 for v in values]

        self.assertEqual(double_values([1, 2, 3]), [2, 4, 6])

    def test_prev_annot_incorrect_return_dict_type(self):
        @type_enforcer()
        def get_str_int_map() -> Dict[str, int]:
            return {"a": "1", "b": "2"}

        with self.assertRaises(TypeError):
            get_str_int_map()

    def test_with_many_args(self):
        @type_enforcer()
        def process_array(*args) -> list[int]:
            return list(args) * 2

        self.assertEqual(process_array(1, 2, 3), [1, 2, 3, 1, 2, 3])
