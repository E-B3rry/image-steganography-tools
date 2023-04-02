# Internal modules
from typing import Union

# Project modules
from constants import *
from exceptions import UnsupportedImageFormatError

# External modules
import PIL
from PIL import Image

from l10n import Locales


def get_image_bytes_size(img: Image) -> int:
    """
    Returns the size of an image in bytes. (Calculates the size of each pixel and multiplies it by the number of pixels)
    :param img: the Pillow image object
    :return: int
    """

    return img.size[0] * img.size[1] * len(img.getbands())


# Alternative:
#
# def get_image_pixels(img: Image, channels: Union[int, list[int], None] = None) -> list:
#     """
#     Returns a list of all image's pixels with the selected channels.
#     :param channels:
#     :param img:
#     :return list:
#     """
#     if type(channels) == int:
#         pixels = list(img.getdata(band=channels))
#     elif type(channels) == list:
#         pixels = [list(pixel) for pixel in zip(*[list(img.getdata(band=c)) for c in channels])]
#     elif channels == None:
#         pixels = list(img.getdata())
#
#     return pixels

def get_image_pixels(img: Image) -> list[tuple[int, ...], ...]:
    """
    Returns a list of all image's pixels in a list.
    :param img: the Pillow image object
    :return list:
    """
    return list(img.getdata())


def create_image_from_pixels(pixels: list, mode: str, size: tuple[int, int], ext: Union[str, None] = None) -> Image:
    """
    Creates a new image from the given list of pixels and prepares the image for saving it in desired format.
    :param pixels: the pixels list
    :param mode: the pixels list mode
    :param size: a tuple with size of the image (x, y)
    :param ext: optional: the desired extension
    :return:
    """
    img = Image.new(mode=mode, size=size)
    img.putdata(pixels)

    if ext:
        ext = ext.strip('.').upper()

        match ext:
            case "PNG":
                img = img.convert("RGBA")
            case "JPEG" | "BMP":
                img = img.convert("RGB")
            case "PGM" | "PPM" | "PBM":
                img = img.convert("L")
            case _:
                raise UnsupportedImageFormatError()

    return img
