import unittest
from PIL import Image

import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'src')
sys.path.insert(0, src_path)

from src.utils import get_image_bytes_size, get_image_pixels, create_image_from_pixels  # noqa: E402


class TestUtils(unittest.TestCase):
    def test_get_image_bytes_size(self):
        img = Image.new("RGB", (10, 10))
        size = get_image_bytes_size(img)
        self.assertEqual(size, 300)

    def test_get_image_pixels(self):
        img = Image.new("RGB", (2, 2))
        pixels = get_image_pixels(img)
        self.assertEqual(len(pixels), 4)

    def test_create_image_from_pixels(self):
        pixels = [(0, 0, 0), (255, 255, 255), (255, 255, 255), (0, 0, 0)]
        img = create_image_from_pixels(pixels, "RGB", (2, 2))
        self.assertIsInstance(img, Image.Image)


if __name__ == "__main__":
    unittest.main()
