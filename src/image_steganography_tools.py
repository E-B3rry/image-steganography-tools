# Internal modules
from pprint import pprint

# Project modules
from utils import load_image, get_image_bytes_size

# External modules
import PIL
from PIL import Image

from l10n import Locales


"""
ImageSteganographyTools is a library designed to provide functionality for hiding and revealing text or files within images;
It currently supports PGM, PNG and Bitmap image formats and allows encoding of text in ASCII or UTF-8 character sets.
"""


# Direct testing
if __name__ == "__main__":
    print("IST v1.0.0a")

    # Load an image
    image1 = load_image("../img/image1-transparent.png")
    image2 = load_image("../img/chat.pgm")

    # Get the size of the image in bytes
    image_size = get_image_bytes_size(image2)
    pprint(image_size)
