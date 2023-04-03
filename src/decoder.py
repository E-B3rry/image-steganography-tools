# Internal modules

# Project modules
from src.base import BaseSteganography
from src.pattern import Pattern
from src.utils import get_image_pixels
from log_config import get_logger

# External modules


"""


"""


class Decoder(BaseSteganography):
    def __init__(self):
        super().__init__()

    def load_pattern(self, pattern: Pattern):
        self.pattern = pattern.generate_pattern()

    def extract_data(self, pixels: list[tuple[int, ...], ...]) -> str:
        pattern = self.pattern
        channels = pattern['channels']
        bit_frequency = pattern['bit_frequency']
        redundancy = pattern['redundancy']
        hash_check = pattern['hash_check']
        byte_spacing = pattern['byte_spacing']

        extracted_bits = ''
        channel_counters = {channel: 0 for channel in self.image.mode}
        for pixel_index, pixel in enumerate(pixels):
            for channel_index, value in enumerate(pixel):
                channel = self.image.mode[channel_index]

                if channel in channels:
                    if channel_counters[channel] % byte_spacing == 0:
                        value_bits = format(value, '08b')
                        extracted_bits += value_bits[-bit_frequency:]

                    channel_counters[channel] += 1

        data = ''
        for i in range(0, len(extracted_bits), 8 * redundancy):
            byte = extracted_bits[i:i + 8 * redundancy]

            # TODO: Really implement redundancy check in Decoder
            # Reduce redundancy
            byte = byte[::redundancy]

            if byte == '00000000':  # Stop at the null delimiter
                break
            data += chr(int(byte, 2))

        if hash_check:
            original_data, data_hash = data[:-64], data[-64:]
            if Pattern.compute_hash(original_data) != data_hash:
                raise ValueError("Data integrity check failed")
            return original_data

        self.logger.debug(f"Extracted bits: {extracted_bits}")
        self.logger.debug(f"Data: {data}")

        return data

    def process(self):
        pass

    def decode(self, file_path: str, pattern: Pattern) -> str:
        self.load_image(file_path)
        self.load_pattern(pattern)
        pixels = get_image_pixels(self.image)
        data = self.extract_data(pixels)
        return data
