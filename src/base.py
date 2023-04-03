# Internal modules
import logging
from abc import ABC, abstractmethod
from typing import Union

# Project modules
from src.exceptions import UnsupportedImageFormatError
from src.constants import currently_supported_formats
from src.log_config import get_logger

# External modules
from PIL import Image


class BaseSteganography(ABC):
    def __init__(self):
        self.pattern = None
        self.image: Image = None
        self.logger = get_logger(self.__class__.__name__)

    def load_image(self, file_path: str) -> None:
        if file_path.split('.')[-1].upper() not in currently_supported_formats:
            raise UnsupportedImageFormatError()

        image = Image.open(file_path)

        if image.format not in currently_supported_formats:
            image.close()
            raise UnsupportedImageFormatError()

        self.image = image
        self.logger.info(f"Image loaded from {file_path}")

    def save_image(self, output_path: str, image_format: Union[str, None] = None) -> None:
        if image_format is None:
            image_format = output_path.split('.')[-1].upper()

        if not image_format:
            raise ValueError("Image format not specified")

        if image_format not in currently_supported_formats:
            raise UnsupportedImageFormatError()

        self.image.save(output_path, format=image_format)
        self.logger.info(f"Image saved to {output_path}")

    @abstractmethod
    def load_pattern(self, pattern: any):
        pass

    @abstractmethod
    def process(self, *args, **kwargs):
        pass

    def __del__(self):
        if self.image is not None:
            self.image.close()
            self.logger.info("Image closed")
