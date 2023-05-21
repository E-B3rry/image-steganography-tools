# Project modules
from constants import *

"""
ImageSteganographyTools Exception classes
"""


# TODO: Implement all exceptions


class UnsupportedImageFormatError(ValueError):
    def __init__(self):
        super().__init__(
            f"Unsupported image format. Please use a supported format ({currently_supported_formats_string})."
        )


class CompressionNotImplementedError(ValueError):
    def __init__(self, compression_pattern):
        super().__init__(
            f"Compression pattern \"{compression_pattern}\" not implemented."
        )