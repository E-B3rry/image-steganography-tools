# Internal modules
import time
from abc import ABC, abstractmethod
from typing import Union

# Project modules
from pattern import Pattern
from exceptions import UnsupportedImageFormatError
from constants import currently_supported_formats
from log_config import get_logger

# External modules
from PIL import Image


class BaseSteganography(ABC):
    def __init__(self):
        self.pattern = None
        self.image: Image = None
        self.logger = get_logger(self.__class__.__name__)

    def _perform_load_image(self, file_path: str) -> Image:
        if file_path.split('.')[-1].upper() not in currently_supported_formats:
            raise UnsupportedImageFormatError()

        image = Image.open(file_path)

        if image.format not in currently_supported_formats:
            image.close()
            raise UnsupportedImageFormatError()

        self.logger.info(f"Image loaded from {file_path}")
        return image

    def load_image(self, file_path: str) -> None:
        self.image = self._perform_load_image(file_path)

    def _perform_unload_image(self, image: Image) -> None:
        if image is not None:
            image.close()
            self.logger.info(f"Image {image.filename} unloaded")

    def unload_image(self) -> None:
        self._perform_unload_image(self.image)
        self.image = None

    def _perform_save_image(self, image: Image, output_path: str, image_format: Union[str, None] = None, quality: int = 100) -> None:
        if image_format is None:
            image_format = output_path.split('.')[-1].upper()

        if not image_format:
            raise ValueError("Image format not specified")

        if image_format not in currently_supported_formats:
            raise UnsupportedImageFormatError()

        # If the image_format is PGM, set the image_format to PPM
        if image_format in ["PGM", "PPM"]:
            image_format = "PPM"

            with open(output_path, "w+b") as f:
                image.save(f, format=image_format)
        elif image_format in ["JPEG", "JPG", "WEBP"]:
            image.save(output_path, format=image_format, quality=quality)
        else:
            image.save(output_path, format=image_format)

        self.logger.info(f"Image saved to {output_path}")

    @abstractmethod
    def load_pattern(self, pattern: Pattern):
        pass

    @abstractmethod
    def process(self, **kwargs):
        pass

    def __del__(self):
        if self.image is not None:
            self.image.close()
            self.logger.info("Image closed")
