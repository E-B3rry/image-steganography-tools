# Project modules
from typing import Union, Any

from .constants import *

"""
ImageSteganographyTools Exception classes
"""


# TODO: Implement all exceptions


# General exceptions
class UnsupportedTypeForParameterError(ValueError):
    def __init__(self, parameter: str, current_type: Any, expected_type: Union[Any, tuple[Any, ...]]):
        current_type_str = self._get_type_name(current_type)

        if isinstance(expected_type, tuple):
            expected_type_str = " or ".join([self._get_type_name(t) for t in expected_type])
        else:
            expected_type_str = self._get_type_name(expected_type)

        super().__init__(
            f"Unsupported type for parameter \"{parameter}\", expected {expected_type_str}, got {current_type_str}."
        )

    @staticmethod
    def _get_type_name(obj: Any) -> str:
        if isinstance(obj, type):
            return obj.__name__
        else:
            return type(obj).__name__


class RequiredParameterMissingError(ValueError):
    def __init__(self, parameter: str):
        super().__init__(f"Required parameter \"{parameter}\" missing.")


# Encoding / Decoding exceptions
class NoImageLoadedError(ValueError):
    def __init__(self):
        super().__init__("No image loaded, use load_image() or pass the file_path as a keyword argument.")


class NoPatternLoadedError(ValueError):
    def __init__(self):
        super().__init__("No pattern loaded, use load_pattern() or pass the pattern as a keyword argument.")


class DataSizeTooLargeError(ValueError):
    def __init__(self, data_size, max_data_size):
        super().__init__(
            f"Data size exceeds available capacity ({data_size}/{max_data_size} bytes), "
            f"try using a different pattern or increasing compression rate if possible."
        )


class DataIntegrityCheckFailedError(ValueError):
    def __init__(self):
        super().__init__("Data integrity check failed. The data may be corrupted or the pattern may be incorrect.")


class InvalidDataTypeEncounteredDecodingError(ValueError):
    def __init__(self):
        super().__init__("Invalid data type encountered during decoding.")


# Pattern exceptions
class InvalidChannelsError(ValueError):
    def __init__(self, channels, image_channels, initial=None):
        initial = "" if not initial else f"(initial value: {initial}) "

        super().__init__(
            f"Invalid channel(s) for image: {channels} {initial}for image channels {image_channels}."
        )


class InvalidHeaderChannelsError(ValueError):
    def __init__(self, header_channels, image_channels):
        super().__init__(
            f"Invalid header channel(s) for image: {header_channels} for image channels {image_channels}."
        )


class CompressionNotImplementedError(ValueError):
    def __init__(self, compression_pattern):
        super().__init__(
            f"Compression pattern \"{compression_pattern}\" not implemented."
        )


class InvalidRepetitiveRedundancyModeError(ValueError):
    def __init__(self, repetitive_redundancy_mode):
        super().__init__(
            f"Invalid repetitive redundancy mode \"{repetitive_redundancy_mode}\"."
        )


class InvalidAdvancedRedundancyModeError(ValueError):
    def __init__(self, advanced_redundancy_mode):
        super().__init__(
            f"Invalid advanced redundancy pattern \"{advanced_redundancy_mode}\"."
        )


class AdvancedRedundancyNotImplementedError(ValueError):
    def __init__(self, redundancy_pattern):
        super().__init__(
            f"Advanced redundancy pattern \"{redundancy_pattern}\" not implemented."
        )


class InvalidHashAlgorithmError(ValueError):
    def __init__(self, hash_algorithm):
        super().__init__(
            f"Invalid hash algorithm \"{hash_algorithm}\"."
        )


class ShouldNotComputeHashError(ValueError):
    def __init__(self):
        super().__init__(
            f"Should not compute hash for this pattern, as it is disabled."
        )


# Other exceptions
class NoImageChannelsError(ValueError):
    def __init__(self):
        super().__init__("Invalid image channels (empty).")


class UnsupportedImageFormatError(ValueError):
    def __init__(self):
        super().__init__(
            f"Unsupported image format. Please use a supported format ({currently_supported_formats_string})."
        )
