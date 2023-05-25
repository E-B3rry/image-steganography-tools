# Internal modules
import unittest
from itertools import product
import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / "IST")
sys.path.insert(0, src_path)

# Project modules
from IST.pattern import Pattern  # noqa: E402


def generate_test_patterns(default_params: dict, test_params: dict):
    test_patterns = []

    # Generate all combinations of test parameter values
    test_param_keys, test_param_values = zip(*test_params.items())
    param_combinations = list(product(*test_param_values))

    for combination in param_combinations:
        # Combine default parameters and current test parameter combination
        current_params = dict(zip(test_param_keys, combination))
        combined_params = {**default_params, **current_params}

        # Create a Pattern object with the combined parameters and append it to the test patterns list
        pattern = Pattern(**combined_params)
        test_patterns.append(pattern)

    return test_patterns


def filter_patterns(test_patterns, *rule_pairs):
    """
    Filters test patterns based on the provided rule pairs.

    :param test_patterns: List of test patterns to filter.
    :param rule_pairs: Any number of tuple pairs containing two sets of rules.
                       The function will eliminate patterns that meet the conditions
                       specified in the second set of rules if any of the conditions
                       in the first set of rules are met.
    :return: Filtered list of test patterns.
    """
    filtered_patterns = []

    # Iterate through each test pattern
    for pattern in test_patterns:
        eliminate = False

        # Iterate through each rule pair
        for rule_pair in rule_pairs:
            # Check if any rule in the first set is met
            first_set_met = any(all(getattr(pattern, key) == value for key, value in rule.items()) for rule in rule_pair[0])

            # Check if any rule in the second set is met
            second_set_met = any(all(getattr(pattern, key) == value for key, value in rule.items()) for rule in rule_pair[1])

            # If both sets have met rules, mark the pattern for elimination
            if first_set_met and second_set_met:
                eliminate = True
                break

        # If the pattern is not marked for elimination, add it to the filtered patterns list
        if not eliminate:
            filtered_patterns.append(pattern)

    return filtered_patterns


class TestPattern(unittest.TestCase):
    def test_generate_pattern(self):
        pattern = Pattern()
        generated_pattern = pattern.generate_pattern(image_channels="RGBA")
        self.assertIsInstance(generated_pattern, dict)

    def test_compute_hash(self):
        pattern = Pattern()
        data = b"Test data"
        data_hash = pattern.compute_hash(data)
        self.assertIsInstance(data_hash, bytes)


if __name__ == "__main__":
    unittest.main()
