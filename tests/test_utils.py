import unittest
from PIL import Image

import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'IST')
sys.path.insert(0, src_path)

from IST.utils import (get_image_bytes_size, get_image_pixels,
                       create_image_from_pixels, calculate_byte_distance)  # noqa: E402


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

    def test_calculate_byte_distance(self):
        candidate_byte = 128
        neighbors = [100, 150, 200]
        distance = calculate_byte_distance(candidate_byte, neighbors)
        self.assertEqual(distance, 122)


if __name__ == "__main__":
    unittest.main()
