import unittest
import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'src')
sys.path.insert(0, src_path)

from src.base import BaseSteganography  # noqa: E402
from src.exceptions import UnsupportedImageFormatError  # noqa: E402


# Subclass of BaseSteganography for testing purposes
class TestSteganography(BaseSteganography):
    def load_pattern(self, pattern: any):
        pass

    def process(self, *args, **kwargs):
        pass


class TestBaseSteganography(unittest.TestCase):
    def test_load_image(self):
        base = TestSteganography()
        with self.assertRaises(UnsupportedImageFormatError):
            base.load_image("test_images/unsupported_format.xyz")

    def test_save_image(self):
        base = TestSteganography()
        base.load_image("test_images/png/test_image.png")
        with self.assertRaises(UnsupportedImageFormatError):
            base.save_image("test_images/unsupported_format.xyz")


if __name__ == "__main__":
    unittest.main()
