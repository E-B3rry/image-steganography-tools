# Internal modules

# Project modules
from src.base import BaseSteganography
from src.pattern import Pattern
from src.utils import get_image_pixels
from log_config import get_logger

# External modules
from PIL import Image


"""


"""


class Decoder(BaseSteganography):
    def __init__(self, **kwargs):
        super().__init__()
        self.pattern: Pattern = kwargs.get("pattern", None)

        self.encoding: str = kwargs.get("encoding", "utf-8")
        self.image: Image = kwargs.get("image", None)

    def load_pattern(self, pattern: Pattern):
        self.pattern = pattern

    def extract_data(self, pixels: list[tuple[int, ...], ...]) -> str:
        pattern_data = self.pattern.generate_pattern()
        channels = pattern_data["channels"]
        bit_frequency = pattern_data["bit_frequency"]
        redundancy = pattern_data["redundancy"]
        hash_check = pattern_data["hash_check"]
        byte_spacing = pattern_data["byte_spacing"]
        compression_enabled = pattern_data["compression"]

        extracted_bits = ""
        channel_counters = {channel: 0 for channel in self.image.mode}
        for pixel_index, pixel in enumerate(pixels):
            for channel_index, value in enumerate(pixel):
                channel = self.image.mode[channel_index]

                if channel in channels:
                    if channel_counters[channel] % byte_spacing == 0:
                        value_bits = format(value, '08b')
                        extracted_bits += value_bits[-bit_frequency:]

                    channel_counters[channel] += 1

        data_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8 * redundancy):
            byte = extracted_bits[i:i + 8 * redundancy]

            # TODO: Really implement redundancy check in Decoder
            # Reduce redundancy
            byte = byte[::redundancy]

            if byte == "00000000":  # Stop at the null delimiter
                break
            data_bytes.append(int(byte, 2))

        if compression_enabled:
            compression_flag, data_bytes = data_bytes[0], data_bytes[1:]

            if compression_flag == b'1':
                data_bytes = self.pattern.decompress_data(data_bytes)

        data = data_bytes.decode(self.encoding, errors="ignore")

        if hash_check:
            original_data, data_hash = data[:-64], data[-64:]
            if Pattern.compute_hash(original_data) != data_hash:
                raise ValueError("Data integrity check failed")
            return original_data

        # self.logger.debug(f"Extracted bits: {extracted_bits}")
        self.logger.debug(f"Extracted data: {data}")

        return data

    def process(self):
        pass

    def decode(self, file_path: str, pattern: Pattern) -> str:
        self.load_image(file_path)
        self.load_pattern(pattern)
        pixels = get_image_pixels(self.image)
        data = self.extract_data(pixels)
        return data
