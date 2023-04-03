import unittest
import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'src')
sys.path.insert(0, src_path)

from src.pattern import Pattern  # noqa: E402


class TestPattern(unittest.TestCase):
    def test_generate_pattern(self):
        pattern = Pattern()
        generated_pattern = pattern.generate_pattern()
        self.assertIsInstance(generated_pattern, dict)

    def test_compute_hash(self):
        pattern = Pattern()
        data = "Test data"
        data_hash = pattern.compute_hash(data)
        self.assertIsInstance(data_hash, str)


if __name__ == "__main__":
    unittest.main()
