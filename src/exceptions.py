# Project modules
from src.constants import *

"""
ImageSteganographyTools Exception classes
"""


class UnsupportedImageFormatError(ValueError):
    def __init__(self):
        super().__init__(
            f"Unsupported image format. Please use a supported format ({currently_supported_formats_string})."
        )
