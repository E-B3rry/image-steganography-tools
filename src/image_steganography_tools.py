# Internal modules
from pprint import pprint

# Project modules
from encoder import Encoder
from decoder import Decoder
from pattern import Pattern
from utils import get_image_bytes_size, get_image_pixels
from log_config import configure_logging

# External modules
import PIL
from PIL import Image

from l10n import Locales


"""
ImageSteganographyTools is a library designed to provide functionality for hiding and revealing text or files within images;
It currently supports PGM, PNG and Bitmap image formats and allows encoding of text in ASCII or UTF-8 character sets.
"""


configure_logging()


# Direct testing
if __name__ == "__main__":
    print("IST v1.0.0a")

    choice = input("Encode or decode? [e/d] ")

    # Create a pattern
    test_pattern = Pattern(
        channels="A",
        redundancy=3,
    )

    if choice == "e":
        # Create an encoder class
        test_encoder = Encoder()

        # Encode a message
        test_encoder.encode(
            "../img/image1-transparent.png",
            "I'm a fucking blobfish ma gueule",
            test_pattern,
            "../img/output/test-1.png",
        )
    elif choice == "d":
        # Create a decoder class
        test_decoder = Decoder()

        # Decode the message from selected file
        data = test_decoder.decode(
            "../img/output/test-1.png",
            test_pattern,
        )

        print(data)
    else:
        print("Choice not valid")
