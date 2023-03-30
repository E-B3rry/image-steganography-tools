# Internal modules

# Project modules
from constants import *

# External modules
import PIL
from PIL import Image

from l10n import Locales


def load_image(file_path: str) -> Image:
    """
    Loads an image into a Pillow Image object.
    :param file_path: str
    :return: Image
    """
    image = Image.open(file_path)

    if image.format not in currently_supported_formats:
        raise ValueError(f"Unsupported image format. Please use a supported format ({currently_supported_formats_string}).")

    return image


def save_image(image: Image, output_path: str, image_format: str = "PNG") -> None:
    """
    Saves a Pillow Image to the specified output path.
    :param image: Image
    :param output_path: str
    :param image_format: optional: str (default is "PNG")
    :return: None
    """
    if image_format not in currently_supported_formats:
        raise ValueError(f"Unsupported image format. Please use a supported format ({currently_supported_formats_string}).")

    image.save(output_path, format=image_format)


def get_image_bytes_size(image: Image) -> int:
    """
    Returns the size of an image in bytes. (Calculates the size of each pixel and multiplies it by the number of pixels)
    :param image: Image
    :return: tuple
    """

    return image.size[0] * image.size[1] * len(image.getbands())
