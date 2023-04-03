# Internal modules

# Project modules
from src.base import BaseSteganography
from src.pattern import Pattern
from src.utils import get_image_pixels, create_image_from_pixels
from src.log_config import get_logger

# External modules
from PIL import Image

"""
Encoder module of the Image Steganography Tools library.
"""

logger = get_logger("encoder")


class Encoder(BaseSteganography):
    def __init__(self):
        super().__init__()

    def load_pattern(self, pattern: Pattern):
        self.pattern = pattern.generate_pattern()

    def validate_data(self, data: str) -> bool:
        required_bits = len(data) * 8 * self.pattern['redundancy'] * self.pattern['byte_spacing']
        available_bits = self.image.width * self.image.height * \
                         self.pattern['bit_frequency'] * len(self.pattern['channels'])
        return required_bits <= available_bits

    def available_bytes_for_data(self) -> int:
        return self.image.width * self.image.height * self.pattern['bit_frequency'] * len(self.pattern['channels']) / \
            self.pattern['redundancy'] / self.pattern['byte_spacing'] // 8

    def apply_pattern(self, pixels: list[tuple[int, ...], ...], data: str) -> list[tuple[int, ...]]:
        pattern = self.pattern
        channels = pattern['channels']
        bit_frequency = pattern['bit_frequency']
        redundancy = pattern['redundancy']
        hash_check = pattern['hash_check']
        byte_spacing = pattern['byte_spacing']

        if hash_check:
            data_hash = Pattern.compute_hash(data)
            data += data_hash

        data_bits = ''.join(format(ord(char), '08b') for char in data)
        data_bits += '00000000'  # Add 8 null bits as a delimiter

        # Add the redundancy
        data_bits = ''.join([data_bits[i] * redundancy for i in range(len(data_bits))])

        bit_index = 0
        channel_counters = {channel: 0 for channel in self.image.mode}
        encoded_pixels = []
        for pixel_index, pixel in enumerate(pixels):
            new_pixel = []
            for channel_index, value in enumerate(pixel):
                channel = self.image.mode[channel_index % len(self.image.mode)]

                if channel in channels:
                    if bit_index < len(data_bits) and channel_counters[channel] % byte_spacing == 0:
                        # self.logger.debug(f"Modifying pixel {pixel_index}, channel {channel_index} ({channel})")

                        value_bits = format(value, '08b')
                        new_value_bits = value_bits[:-bit_frequency] + data_bits[bit_index:bit_index + bit_frequency]
                        new_value = int(new_value_bits, 2)

                        bit_index += bit_frequency

                        new_pixel.append(new_value)
                    else:
                        new_pixel.append(value)

                    channel_counters[channel] += 1
                else:
                    new_pixel.append(value)

            encoded_pixels.append(tuple(new_pixel))

        return encoded_pixels

    def process(self):
        pass

    def encode(self, file_path: str, data: str, pattern: Pattern, output_path: str) -> None:
        self.load_image(file_path)
        self.load_pattern(pattern)
        if not self.validate_data(data):
            raise ValueError("Data size exceeds available capacity")
        pixels = get_image_pixels(self.image)
        encoded_pixels = self.apply_pattern(pixels, data)
        encoded_image = create_image_from_pixels(encoded_pixels, self.image.mode, self.image.size)
        self.image = encoded_image
        self.save_image(output_path)
