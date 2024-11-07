import unittest
from typing import Dict, List, Optional, Tuple, Union

from typeca import type_enforcer


class TestEnforceTypes(unittest.TestCase):

    def test_correct_simple_types(self):
        @type_enforcer()
        def add(a: int, b: int) -> int:
            return a + b

        self.assertEqual(add(3, 4), 7)

    def test_correct_simple_list_type(self):
        @type_enforcer()
        def concat(a: list, b: list) -> list:
            return a + b

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

    def test_skipped_annot(self):
        @type_enforcer()
        def process_data(a, b: float, c: int) -> float:
            return a * b * c

        self.assertEqual(process_data(1, 2.0, 3), 6.0)

    def test_set_type(self):
        @type_enforcer()
        def unique_values(values: set[int]) -> set[int]:
            return set(values)

        self.assertEqual(unique_values({1, 2, 3, 3}), {1, 2, 3})

    def test_frozenset_type(self):
        @type_enforcer()
        def fixed_values() -> frozenset[int]:
            return frozenset({1, 2, 3})

        self.assertEqual(fixed_values(), frozenset({1, 2, 3}))

    def test_correct_set_type(self):
        @type_enforcer()
        def unique_values(values: set[int]) -> set[int]:
            return set(values)

        self.assertEqual(unique_values({1, 2, 3}), {1, 2, 3})

    def test_incorrect_set_type(self):
        @type_enforcer()
        def unique_values(values: set[int]) -> set[int]:
            return set(values)

        with self.assertRaises(TypeError) as context:
            unique_values({1, "2", 3})
        self.assertIn("Argument 'values' must be of type set[int]", str(context.exception))

    def test_set_empty(self):
        @type_enforcer()
        def unique_values(values: set[int]) -> set[int]:
            return set(values)

        self.assertEqual(unique_values(set()), set())

    def test_set_with_non_int_elements(self):
        @type_enforcer()
        def unique_values(values: set[int]) -> set[int]:
            return set(values)

        with self.assertRaises(TypeError) as context:
            unique_values({1, 2, "3"})
        self.assertIn("Argument 'values' must be of type set[int]", str(context.exception))

    def test_correct_frozenset_type(self):
        @type_enforcer()
        def fixed_values() -> frozenset[int]:
            return frozenset({1, 2, 3})

        self.assertEqual(fixed_values(), frozenset({1, 2, 3}))

    def test_correct_frozenset_type_2(self):
        @type_enforcer()
        def fixed_values() -> frozenset[int | str]:
            return frozenset({1, 'a'})

        self.assertEqual(fixed_values(), frozenset({1, 'a'}))

    def test_incorrect_frozenset_type(self):
        @type_enforcer()
        def fixed_values() -> frozenset[int]:
            return frozenset({1, 2, 3})

        with self.assertRaises(TypeError):
            fixed_values({"a", 2, 3})

    def test_frozenset_empty(self):
        @type_enforcer()
        def fixed_values() -> frozenset[int]:
            return frozenset()

        self.assertEqual(fixed_values(), frozenset())

    def test_frozenset_with_non_int_elements(self):
        @type_enforcer()
        def fixed_values() -> frozenset[int]:
            return frozenset({1, 2, "3"})

        with self.assertRaises(TypeError) as context:
            fixed_values()
        self.assertIn("Return value must be of type frozenset[int]", str(context.exception))

    def test_set_of_frozenset_elements(self):
        @type_enforcer()
        def set_of_frozensets(values: set[frozenset[int]]) -> set[frozenset[int]]:
            return {frozenset(val) for val in values}

        self.assertEqual(set_of_frozensets({frozenset([1, 2]), frozenset([3, 4])}),
                         {frozenset([1, 2]), frozenset([3, 4])})

    def test_frozenset_of_sets(self):
        @type_enforcer()
        def frozenset_of_sets(values: frozenset[frozenset[int]]) -> frozenset[frozenset[int]]:
            return frozenset(values)

        self.assertEqual(frozenset_of_sets(frozenset([frozenset([1, 2]), frozenset([3, 4])])),
                         frozenset([frozenset([1, 2]), frozenset([3, 4])]))

        with self.assertRaises(TypeError):
            frozenset_of_sets(
                frozenset([frozenset([1, 2]), {3, 4}]))

    def test_list_with_nested_types(self):
        @type_enforcer()
        def process_nested_list(values: list[list[int]]) -> list[list[int]]:
            return values

        self.assertEqual(process_nested_list([[1, 2], [3, 4]]), [[1, 2], [3, 4]])

        with self.assertRaises(TypeError):
            process_nested_list([[1, 2], "string"])

    def test_set_with_non_type_compliant_elements(self):
        @type_enforcer()
        def process_set(values: set[int]) -> set[int]:
            return values

        with self.assertRaises(TypeError) as context:
            process_set({1, 2, "string"})  # "string" is not an int
        self.assertIn("Argument 'values' must be of type set[int]", str(context.exception))

    def test_union_type(self):
        @type_enforcer()
        def process_union(value: int | str) -> int | str:
            return value

        self.assertEqual(process_union(10), 10)
        self.assertEqual(process_union("test"), "test")

    def test_optional_type(self):
        @type_enforcer()
        def process_optional(value: int | None) -> int | None:
            return value

        self.assertEqual(process_optional(10), 10)
        self.assertIsNone(process_optional(None))

    def test_optional_int_type(self):
        @type_enforcer()
        def process_optional(value: int | None) -> int | None:
            return value

        self.assertEqual(process_optional(10), 10)
        self.assertIsNone(process_optional(None))

    def test_optional_list_type(self):
        @type_enforcer()
        def process_optional_list(value: list[int] | None) -> list[int] | None:
            return value

        self.assertEqual(process_optional_list([1, 2, 3]), [1, 2, 3])
        self.assertIsNone(process_optional_list(None))

    def test_union_without_none(self):
        @type_enforcer()
        def process_union(value: int | str) -> int | str:
            return value

        self.assertEqual(process_union(10), 10)
        self.assertEqual(process_union("text"), "text")

    def test_optional_int(self):
        @type_enforcer()
        def process_value(value: Optional[int]) -> Optional[int]:
            return value

        self.assertEqual(process_value(10), 10)
        self.assertEqual(process_value(None), None)

        # Invalid case
        with self.assertRaises(TypeError):
            process_value("string")

    def test_union_int_or_str(self):
        @type_enforcer()
        def process_union(value: Union[int, str]) -> Union[int, str]:
            return value

        self.assertEqual(process_union(10), 10)
        self.assertEqual(process_union("hello"), "hello")

        with self.assertRaises(TypeError):
            process_union(10.5)

    def test_optional_union_int_or_str(self):
        @type_enforcer()
        def process_optional_union(value: Optional[Union[int, str]]) -> Optional[Union[int, str]]:
            return value

        # Valid cases
        self.assertEqual(process_optional_union(10), 10)
        self.assertEqual(process_optional_union("text"), "text")
        self.assertEqual(process_optional_union(None), None)

        # Invalid case
        with self.assertRaises(TypeError):
            process_optional_union(10.5)

    def test_optional_dict_with_union_values(self):
        @type_enforcer()
        def process_dict(values: Optional[dict[str, Union[int, None]]]) \
                -> Optional[dict[str, Union[int, None]]]:
            return values

        self.assertEqual(process_dict({"a": 1, "b": None}), {"a": 1, "b": None})
        self.assertEqual(process_dict(None), None)

        # Invalid case
        with self.assertRaises(TypeError):
            process_dict({"a": 1, "b": "text"})

    def test_optional_tuple_of_optional_elements(self):
        @type_enforcer()
        def process_tuple(value: Optional[tuple[Optional[int], Optional[str]]]) \
                -> Optional[tuple[Optional[int], Optional[str]]]:
            return value

        # Valid cases
        self.assertEqual(process_tuple((None, None)), (None, None))
        self.assertEqual(process_tuple((10, "text")), (10, "text"))
        self.assertEqual(process_tuple(None), None)

        # Invalid case
        with self.assertRaises(TypeError):
            process_tuple((10.5, "text"))
