# Internal modules
from typing import Union

# Project modules
from base import BaseSteganography
from pattern import Pattern
from utils import get_image_pixels, create_image_from_pixels, ranges_overlap
from log_config import get_logger

# External modules
from PIL import Image

"""
Encoder.py is a module in the IST (Image Steganography Tools) library that provides functionality for encoding and hiding data within images. It is designed to work with various image formats and supports customizable encoding patterns. The module contains an Encoder class that implements the encoding process and provides methods for loading images, patterns, and hiding data.

Classes and Methods:
- Encoder: The main class that implements the encoding process.
    - __init__(self, **kwargs): Initializes the Encoder object with optional keyword arguments.
    - load_pattern(self, pattern: Pattern): Loads a Pattern object for encoding.
    - unload_processed_image(self): Unloads the processed image from memory.
    - available_bytes_for_data(self): Returns the number of available bytes for data based on the loaded pattern.
    - apply_pattern(self, pixels: list[tuple[int, ...], ...], data: bytes): Applies the encoding pattern to the given pixel values and hides the data.
    - encode_data(self, pixels: list[int | tuple[int, ...], ...], data: Union[bytes, bytearray], channels: str, bit_frequency: int, byte_spacing: int, offset: int = 0): Encodes the data into the given pixel values based on the specified parameters.
    - process(self, **kwargs): Main method that loads the image and pattern (if not already loaded), hides the data, and saves the processed image.

Usage:
To use the Encoder module, create an Encoder object and load an image and pattern. Then, call the process() method to hide the data and save the processed image. For example:

    from IST import Encoder, Pattern

    # Create an Encoder object
    encoder = Encoder()

    # Load an image and pattern
    encoder.load_image("path/to/image.png")
    encoder.load_pattern(Pattern())

    # Hide the data and save the processed image
    encoder.process(data="Secret message", output_path="path/to/processed_image.png")

This module is part of the IST (Image Steganography Tools) library, which provides a comprehensive set of tools for hiding and extracting data within images.
"""

logger = get_logger("encoder")


class Encoder(BaseSteganography):
    def __init__(self, **kwargs):
        super().__init__()
        self.pattern: Pattern = kwargs.get("pattern", None)
        self.encoding: str = kwargs.get("encoding", "utf-8")
        self.image: Image = kwargs.get("image", None)

        self.processed_image: Image = None

    def load_pattern(self, pattern: Pattern):
        self.pattern = pattern

    def unload_processed_image(self) -> None:
        self._perform_unload_image(self.processed_image)
        self.processed_image = None

    def _validate_data_after_pattern_applied(self, data: Union[bytes, bytearray]) -> bool:
        max_size = self.pattern.calculate_max_data_size((self.image.width, self.image.height), self.image.mode)
        return len(data) <= max_size

    def available_bytes_for_data(self) -> int:
        return self.pattern.calculate_max_data_size((self.image.width, self.image.height), self.image.mode) or 0

    def apply_pattern(self, pixels: list[tuple[int, ...], ...], data: bytes) -> list[tuple[int, ...]]:
        pattern_data = self.pattern.generate_pattern(self.image.mode)

        channels = pattern_data["channels"]
        bit_frequency = pattern_data["bit_frequency"]
        byte_spacing = pattern_data["byte_spacing"]
        position = pattern_data["position"]
        hash_check = pattern_data["hash_check"]
        compression_enabled = pattern_data["compression_enabled"]

        header_enabled = pattern_data["header_enabled"]
        header_write_data_size = pattern_data["header_write_data_size"]
        header_write_pattern = pattern_data["header_write_pattern"]
        header_channels = pattern_data["header_channels"]
        header_bit_frequency = pattern_data["header_bit_frequency"]
        header_byte_spacing = pattern_data["header_byte_spacing"]

        # Compute hash if enabled
        if hash_check:
            data_hash = self.pattern.compute_hash(data)
            data += data_hash

        # Compress if enabled
        if compression_enabled:
            data = self.pattern.compress_data(data)

        # Add the redundancy
        data = self.pattern.apply_redundancy(data)

        if not self._validate_data_after_pattern_applied(data):
            raise ValueError(f"Data size exceeds available capacity ({len(data)}/{self.available_bytes_for_data()} bytes), "
                             f"try using a different pattern or increasing compression rate if possible.")

        header_added_offset = 0
        # If header is enabled, accordingly generate the header
        header = None
        if header_enabled and (header_write_data_size or header_write_pattern):
            header = self.pattern.generate_header(len(data))

            # If the header is not null, encode it
            if header:
                # Compute the header position
                header_position = 0
                if pattern_data["header_position"] == "image_start":
                    header_position = 0
                elif pattern_data["header_position"] == "before_data":
                    header_position = position

                # Remember the header_added_offset to add it to the data offset if required
                pixels, header_added_offset = self.encode_data(pixels, header, header_channels, header_bit_frequency, header_byte_spacing,
                                                               header_position)

        if header:
            # If header is set to image_start, and the data is not overlapping with the header, don't add the header offset
            if pattern_data["header_position"] == "image_start" and not ranges_overlap(0, header_added_offset, position, position):
                pixels, _ = self.encode_data(pixels, data, channels, bit_frequency, byte_spacing, position)
            else:
                # Taking into account the header encoded size
                pixels, _ = self.encode_data(pixels, data, channels, bit_frequency, byte_spacing, position + header_added_offset)
        else:
            # If the header is not enabled just encode the data not taking into account the header
            pixels, _ = self.encode_data(pixels, data, channels, bit_frequency, byte_spacing, position)

        return pixels

    def encode_data(self, pixels: list[int | tuple[int, ...], ...], data: Union[bytes, bytearray],
                    channels: str, bit_frequency: int, byte_spacing: int, offset: int = 0) -> (list[int | tuple[int, ...]], int):
        data_bits = ''.join(format(byte, '08b') for byte in data)

        bit_index = 0
        channel_counters = {channel: 0 for channel in self.image.mode}

        # If pixels list is not made of tuples but of integers, convert it to tuples
        if isinstance(pixels[0], int):
            pixels = [(pixel,) for pixel in pixels]

        last_pixel = 0
        # print(f"data_bits: {data_bits}")
        encoded_pixels = pixels[0:max(offset, 0)]
        for pixel_index, pixel in enumerate(pixels[offset:], start=offset):
            new_pixel = []

            for channel_index, value in enumerate(pixel):
                channel = self.image.mode[channel_index % len(self.image.mode)]

                if channel in channels and pixel_index >= offset:
                    if bit_index < len(data_bits):
                        if channel_counters[channel] % byte_spacing == 0:
                            # self.logger.debug(f"Modifying pixel {pixel_index}, channel {channel_index} ({channel})")

                            value_bits = format(value, '08b')

                            new_value_bits = value_bits[:-bit_frequency] + data_bits[bit_index:bit_index + bit_frequency]
                            new_value = int(new_value_bits, 2)

                            bit_index += bit_frequency

                            new_pixel.append(new_value)
                        else:
                            new_pixel.append(value)
                    else:
                        new_pixel.append(value)

                    channel_counters[channel] += 1
                else:
                    new_pixel.append(value)

            encoded_pixels.append(tuple(new_pixel))

            if bit_index >= len(data_bits):
                last_pixel = pixel_index
                # print(f"Encoded from pixel {offset} to {last_pixel}")
                break  # No more bits to encode, stop encoding

        # Add the rest of the pixels
        # encoded_pixels += pixels[len(encoded_pixels):]
        encoded_pixels += pixels[last_pixel + 1:]

        # If pixels list is made of tuples of only one integer, flatten it
        if len(encoded_pixels[0]) == 1:
            encoded_pixels = [pixel[0] for pixel in encoded_pixels]

        return encoded_pixels, last_pixel - offset

    def process(self, **kwargs) -> None:
        image: Image = kwargs.get("image", None)
        input_path: str = kwargs.get("input_path", None)

        if not self.image or image or input_path:
            if image:
                if isinstance(image, Image.Image):
                    self.image = kwargs.get("image")
                else:
                    raise ValueError("Image must be a PIL.Image.Image object.")
            elif input_path:
                if isinstance(input_path, str):
                    self.image = self._perform_load_image(input_path)
                else:
                    raise ValueError("Input path must be a string.")
            else:
                raise ValueError("No image loaded, use load_image() or pass the image as a keyword argument.")

        pattern: Pattern = kwargs.get("pattern", None)
        if not self.pattern or pattern:
            if pattern:
                if isinstance(pattern, Pattern):
                    self.load_pattern(pattern)
                else:
                    raise ValueError("Pattern must be a Pattern object.")
            else:
                raise ValueError("No pattern loaded, use load_pattern() or pass the pattern as a keyword argument.")

        output_path = kwargs.get("output_path", f"{self.image.filename.split('.')[0]}_encoded.{self.image.filename.split('.')[1]}")
        data = kwargs.get("data", None)

        data = data.encode(self.encoding) if isinstance(data, str) else data

        pixels = get_image_pixels(self.image)
        encoded_pixels = self.apply_pattern(pixels, data)
        encoded_image = create_image_from_pixels(encoded_pixels, self.image.mode, self.image.size)
        self.processed_image = encoded_image
        self._perform_save_image(self.processed_image, output_path)
