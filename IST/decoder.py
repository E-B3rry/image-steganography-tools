# Internal modules
from . import DataIntegrityCheckFailedError, InvalidDataTypeEncounteredDecodingError, UnsupportedTypeForParameterError, NoImageLoadedError, \
    NoPatternLoadedError
# Project modules
from .base import BaseSteganography
from .pattern import Pattern
from .utils import get_image_pixels, ranges_overlap

# External modules
from PIL import Image


"""
Decoder.py is a module in the IST (Image Steganography Tools) library that provides functionality for decoding and extracting hidden data from images. It is designed to work with various image formats and supports customizable decoding patterns. The module contains a Decoder class that implements the decoding process and provides methods for loading images, patterns, and extracting data.


Classes and Methods:
- Decoder: The main class that implements the decoding process.
    - __init__(self, **kwargs): Initializes the Decoder object with optional keyword arguments.
    - load_pattern(self, pattern: Pattern): Loads a Pattern object for decoding.
    - decode_data(self, pixels: list[tuple[int, ...], ...], data_length: int, channels: str, bit_frequency: int, byte_spacing: int, offset: int = 0): Decodes and extracts data from the given pixel values based on the specified parameters.
    - extract_data(self, pixels: list[tuple[int, ...], ...], data_length=None, enforce_provided_pattern=False): Extracts the hidden data from the given pixel values based on the loaded pattern and optional data_length parameter.
    - process(self, **kwargs): Main method that loads the image and pattern (if not already loaded) and extracts the hidden data. Accepts optional keyword arguments for file_path, pattern, data_length, and enforce_provided_pattern.

Usage:
To use the Decoder module, create a Decoder object and load an image and pattern. Then, call the process() method to extract the hidden data. For example:

    from IST import Decoder, Pattern

    # Create a Decoder object
    decoder = Decoder()

    # Load an image and pattern
    decoder.load_image("path/to/image.png")
    decoder.load_pattern(Pattern())

    # Extract the hidden data
    hidden_data = decoder.process()

Alternatively, you can pass the file_path and pattern as keyword arguments to the process() method:

    hidden_data = decoder.process(file_path="path/to/image.png", pattern=Pattern())

This module is part of the IST (Image Steganography Tools) library, which provides a comprehensive set of tools for hiding and extracting data within images.
"""


class Decoder(BaseSteganography):
    def __init__(self, **kwargs):
        super().__init__()
        self.pattern: Pattern = kwargs.get("pattern", None)
        self.encoding: str = kwargs.get("encoding", "utf-8")
        self.image: Image = kwargs.get("image", None)

    def load_pattern(self, pattern: Pattern):
        self.pattern = pattern

    def decode_data(self, pixels: list[tuple[int, ...], ...], data_length: int, channels: str,
                    bit_frequency: int, byte_spacing: int, offset: int = 0) -> (bytes, int):
        data_bits = ""

        channel_counters = {channel: 0 for channel in self.image.mode}

        # If pixels list is not made of tuples but of integers, convert it to tuples
        if isinstance(pixels[0], int):
            pixels = [(pixel,) for pixel in pixels]

        last_pixel = offset
        for pixel_index, pixel in enumerate(pixels[offset:], start=offset):
            # print(f"Processing pixel {pixel_index}: {pixel}")
            for channel_index, value in enumerate(pixel):
                channel = self.image.mode[channel_index % len(self.image.mode)]

                if channel in channels:
                    if channel_counters[channel] % byte_spacing == 0:
                        value_bits = format(value, '08b')
                        # print(value_bits)
                        data_bits += value_bits[-bit_frequency:]

                    channel_counters[channel] += 1

                if len(data_bits) >= data_length * 8:
                    last_pixel = pixel_index
                    break
            else:
                continue

            # print(f"Decoded from pixel {offset} to {last_pixel}")
            break

        # print(f"data_bits: {data_bits}")
        data_bytes = bytearray()

        for i in range(0, data_length * 8, 8):
            #self.logger.debug(f"Extracting byte {i} to {i + 8}: {data_bits[i:i + 8]}")
            byte = data_bits[i:i + 8]
            data_bytes.append(int(byte, 2))

        return data_bytes, last_pixel - offset

    def extract_data(self, pixels: list[tuple[int, ...], ...], data_length=None, enforce_provided_pattern=False) -> bytes:
        pattern_data = self.pattern.generate_pattern(image_channels=self.image.mode)

        channels = pattern_data["channels"]
        bit_frequency = pattern_data["bit_frequency"]
        byte_spacing = pattern_data["byte_spacing"]
        position = pattern_data["position"]

        header_enabled = pattern_data["header_enabled"]
        header_channels = pattern_data["header_channels"]
        header_bit_frequency = pattern_data["header_bit_frequency"]
        header_byte_spacing = pattern_data["header_byte_spacing"]

        header_offset_size = 0
        if header_enabled:
            # Get the expected header data size and extract the header data from the specified position
            header_size = len(self.pattern.generate_header(0))  # TODO: Optimize this to avoid generating the header twice

            # Compute the header position
            header_position = 0
            if pattern_data["header_position"] == "image_start":
                header_position = 0
            elif pattern_data["header_position"] == "before_data":
                header_position = position

            # Extract the header data
            header_data, header_offset_size = self.decode_data(pixels, header_size, header_channels, header_bit_frequency, header_byte_spacing,
                                                               header_position)

            # Remove redundancy from the header data
            header_data = self.pattern.reconstruct_redundancy(header_data, "header")

            # Extract the data length and other information from the header_data
            if not data_length or not enforce_provided_pattern:
                data_length = int.from_bytes(header_data[:4], "big") if not enforce_provided_pattern or not data_length else data_length

            pattern_flag = header_data[4]

            if pattern_flag == 1 and not enforce_provided_pattern:
                # TODO: Support extracting and loading the pattern from the header_data
                pass

            if pattern_data["header_position"] == "image_start" and not ranges_overlap(0, header_offset_size, position, position):
                header_offset_size = 0

        data_bytes, _ = self.decode_data(pixels, data_length, channels, bit_frequency, byte_spacing, position + header_offset_size)

        # Remove redundancy from the data
        data_bytes = self.pattern.reconstruct_redundancy(data_bytes, "data")

        if pattern_data["compression_enabled"]:
            data_bytes = self.pattern.decompress_data(data_bytes)

        if pattern_data["hash_check"]:
            data_bytes, data_hash = data_bytes[:-32], data_bytes[-32:]
            if self.pattern.compute_hash(data_bytes) != data_hash:
                raise DataIntegrityCheckFailedError()

        # data = data_bytes.decode(self.encoding)

        return data_bytes

    def _process_data(self, data_bytes):
        data_type = int(data_bytes[0])
        data_bytes = data_bytes[1:]

        if data_type == 0:
            return data_bytes.decode(self.encoding)
        elif data_type == 1:
            file_name = data_bytes[:64].decode(self.encoding).rstrip('\0')
            file_data = data_bytes[64:]
            with open(file_name, 'wb') as file:
                file.write(file_data)
            return f"File '{file_name}' has been extracted."
        elif data_type == 2:
            return data_bytes
        else:
            raise InvalidDataTypeEncounteredDecodingError()

    def process(self, **kwargs) -> str:
        file_path: str = kwargs.get("file_path", None)
        pattern: Pattern = kwargs.get("pattern", None)

        data_length: int = kwargs.get("data_length", None)
        enforce_provided_pattern: bool = kwargs.get("enforce_provided_pattern", False)

        if not self.image or file_path:
            if file_path:
                if isinstance(file_path, str):
                    self.image = self._perform_load_image(file_path)
                else:
                    raise UnsupportedTypeForParameterError("file_path", file_path, str)
            else:
                raise NoImageLoadedError()

        if not self.pattern or pattern:
            if pattern:
                if isinstance(pattern, Pattern):
                    self.load_pattern(pattern)
                else:
                    raise UnsupportedTypeForParameterError("pattern", pattern, Pattern)
            else:
                raise NoPatternLoadedError()

        pixels = get_image_pixels(self.image)
        data_bytes = self.extract_data(pixels, data_length=data_length, enforce_provided_pattern=enforce_provided_pattern)
        return self._process_data(data_bytes)
