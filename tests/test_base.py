import unittest
import sys
import os
from pathlib import Path
from PIL import Image

src_path = str(Path(__file__).resolve().parent.parent / 'IST')
sys.path.insert(0, src_path)

from IST.base import BaseSteganography  # noqa: E402
from IST.pattern import Pattern  # noqa: E402
from IST.exceptions import UnsupportedImageFormatError  # noqa: E402
from IST.constants import currently_supported_formats  # noqa: E402


# Subclass of BaseSteganography for testing purposes
class TestSteganography(BaseSteganography):
    def load_pattern(self, pattern: Pattern):
        pass

    def process(self, *args, **kwargs):
        pass


class TestBaseSteganography(unittest.TestCase):
    def setUp(self):
        self.base = TestSteganography()
        self.test_images_path = Path(__file__).resolve().parent / 'test_images'
        self.supported_formats = currently_supported_formats

    def test_load_image(self):
        for image_format in self.supported_formats:
            image_path = self.test_images_path / f"{image_format.lower()}/test_image.{image_format.lower()}"
            self.base.load_image(str(image_path))
            self.assertIsNotNone(self.base.image)
            self.base.unload_image()

        with self.assertRaises(UnsupportedImageFormatError):
            self.base.load_image(str(self.test_images_path / "unsupported_format.xyz"))

    def test_unload_image(self):
        image_path = self.test_images_path / "png/test_image.png"
        self.base.load_image(str(image_path))
        self.assertIsNotNone(self.base.image)
        self.base.unload_image()
        self.assertIsNone(self.base.image)

    def test_save_image(self):
        output_path = self.test_images_path / "output"
        os.makedirs(output_path, exist_ok=True)

        for image_format in self.supported_formats:
            input_path = self.test_images_path / f"{image_format.lower()}/test_image.{image_format.lower()}"
            output_file = output_path / f"test_image_saved.{image_format.lower()}"
            self.base.load_image(str(input_path))
            self.base._perform_save_image(self.base.image, str(output_file))
            self.base.unload_image()

            saved_image = Image.open(output_file)
            self.assertEqual(saved_image.format, image_format if image_format != "PGM" else "PPM")
            saved_image.close()
            os.remove(output_file)

        with self.assertRaises(UnsupportedImageFormatError):
            self.base._perform_save_image(self.base.image, str(output_path / "unsupported_format.xyz"))

    def tearDown(self):
        self.base.unload_image()


if __name__ == "__main__":
    unittest.main()
