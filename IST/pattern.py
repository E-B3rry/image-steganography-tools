# Internal modules
import zlib
import hashlib
from itertools import chain
from math import ceil
from typing import Union

# Project modules
from .utils import calculate_byte_distance, rs_decode, rs_encode
from .log_config import get_logger, logging
from .exceptions import CompressionNotImplementedError

# External modules

"""
Pattern.py is a module in the IST (Image Steganography Tools) library that provides functionality for generating, interpreting, and applying patterns for encoding and decoding hidden data in images. It supports various redundancy and compression methods to enhance data integrity and reduce the size of the hidden data. The module contains a Pattern class that implements the pattern generation, redundancy, compression, and hashing processes.

Classes and Methods:
- Pattern: The main class that implements the pattern generation, redundancy, compression, and hashing processes.
    - __init__(self, **kwargs): Initializes the Pattern object with optional keyword arguments.
    - generate_pattern(self, image_channels: str) -> dict: Generates a pattern dictionary from the Pattern object's attributes.
    - generate_header(self, data_len: int) -> bytes: Generates the header based on the pattern's attributes.
    - compress_data(self, data: bytes, parameters_source: str = "data") -> bytes: Compresses data using the pattern's compression pattern.
    - decompress_data(self, data: bytes, parameters_source: str = "data") -> bytes: Decompresses data using the pattern's compression pattern.
    - apply_redundancy(self, data: bytes, parameters_source: str = "data") -> bytes: Applies redundancy to data using the pattern's redundancy pattern.
    - reconstruct_redundancy(self, data: bytes, parameters_source: str = "data") -> bytes: Reconstructs data using the pattern's redundancy pattern, if any and if applicable.
    - compute_hash(self, data: Union[bytearray, bytes]) -> bytes: Computes the hash of a bytearray.
    - calculate_max_data_size(self, image_size: tuple[int, int], image_mode: str) -> int: Calculates the maximum size of the data that can be stored in an image with current pattern settings.

Usage:
To use the Pattern module, create a Pattern object and configure its attributes. Then, use the methods provided by the Pattern class to generate patterns, headers, apply redundancy, and compress/decompress data. For example:

    from IST import Pattern

    # Create a Pattern object with custom attributes
    pattern = Pattern(bit_frequency=2, byte_spacing=2, compression="zlib", advanced_redundancy="reed_solomon")

    # Generate a pattern dictionary for an RGBA image
    pattern_dict = pattern.generate_pattern("RGBA")

    # Apply redundancy and compression to data
    data = b"Hello, world!"
    compressed_data = pattern.compress_data(data)
    redundant_data = pattern.apply_redundancy(compressed_data)

    # Reconstruct and decompress data
    reconstructed_data = pattern.reconstruct_redundancy(redundant_data)
    decompressed_data = pattern.decompress_data(reconstructed_data)

This module is part of the IST (Image Steganography Tools) library, which provides a comprehensive set of tools for hiding and extracting data within images.
"""


class Pattern:
    @classmethod
    def get_logger(cls) -> logging.Logger:
        return get_logger(cls.__qualname__)

    def __init__(self, **kwargs):
        self.logger = self.get_logger()
        self.offset: int = kwargs.get("offset", 0)  # Offset in pixels from the top-left corner of the image (header included).
        self.channels: Union[str, None] = kwargs.get("channels", "RGBA")  # When None, empty, "all" or unknown, all channels are used.

        self.bit_frequency: int = kwargs.get("bit_frequency", 1)
        self.byte_spacing: int = kwargs.get("byte_spacing", 1)
        self.hash_check: Union[str, bool, None] = kwargs.get("hash_check", "sha256")  # Default: "sha256", supports any hashes from hashlib.

        # Data compression
        self.compression: Union[str, None] = kwargs.get("compression_pattern", "none")  # Options: "zlib", "none"
        self.compression_strength: int = kwargs.get("compression_strength", 6)  # 1-9, default: 6 (and is the zlib default)

        # Data redundancy
        self.advanced_redundancy: str = kwargs.get("advanced_redundancy", "reed_solomon")  # Options: "reed_solomon", "hamming", "none"
        self.advanced_redundancy_correction_factor: float = kwargs.get("advanced_redundancy_correction_factor", 0.1)  # Allowed range ]0, 1]
        # Correction factor capability (default: 0.1), used to calculate the ability to correct errors based on the chosen algorithm.
        # The size augmentation is based on the chose redundancy algorithm and the correction factor.
        # - For reed-solomon, the size augmentation is 2 * correction_factor * data_size.
        # - For hamming, the size augmentation is 2 * correction_factor * data_size. It decides in how many blocks the data will be split.

        self.repetitive_redundancy: int = kwargs.get("repetitive_redundancy", 1)  # If 1, no repetitive redundancy is applied.
        self.repetitive_redundancy_mode: str = kwargs.get("repetitive_redundancy_mode", "byte_per_byte")  # Options: "byte_per_byte", "block"

        # Header (redundancy parameters are the same as above)
        # The header is enabled by default, but only contains the data size. You may enable the header to contain the pattern, if you plan on
        # the header to be easily discoverable.
        self.header_enabled: bool = kwargs.get("header_enabled", True)  # Header is enabled by default.
        self.header_write_data_size: bool = kwargs.get("header_write_data_size", True)  # Data size is enabled by default (4 bytes).
        self.header_write_pattern: bool = kwargs.get("header_write_pattern", False)  # Enabling this will write the pattern in the header.

        self.header_channels: str = kwargs.get("header_channels", "auto")  # When None, empty, "all" or unknown, all channels are used.
        # In "auto" mode, the channels are automatically selected based on whether the header is meant to be discovered or not.
        # To determine if the header should be discovered, the header_enabled, header_write_pattern and header_write_data_size parameters
        # should be enabled. If the header is meant to be discovered:
        # 1 - The header writes in the Alpha channel if the image has an Alpha channel,
        # 2 - It writes in the Blue channel if the image has a Blue channel,
        # 3 - Otherwise it is written in the first channel.
        # If the header shouldn't be discovered, the header writes in the same channels as the data.
        self.header_position: str = kwargs.get("header_position", "auto")  # Options: "auto", "image_start" and "before_data"
        # In "auto" mode, the header is automatically placed before the data, unless the header is meant to be discovered, in which case it is
        # automatically placed at the start of the image.

        # These are default options, but they can be changed to reduce the header's discoverability.
        self.header_bit_frequency: int = kwargs.get("header_bit_frequency", 1)
        self.header_byte_spacing: int = kwargs.get("header_byte_spacing", 1)

        self.header_repetitive_redundancy: int = kwargs.get("header_repetitive_redundancy", 5)  # If 1, no repetitive redundancy is applied.
        self.header_advanced_redundancy: str = kwargs.get("header_advanced_redundancy", "reed_solomon")  # Same as above.
        self.header_advanced_redundancy_correction_factor: float = kwargs.get("header_advanced_redundancy_correction_factor", 0.1)

    def generate_pattern(self, image_channels: str) -> dict:
        """
        Generates a pattern dictionary from the Pattern object's attributes.
        :param image_channels: The channels of the image to be used. E.g. "RGBA".
        :return: A dictionary containing the computed pattern's attributes.
        """
        # Determine and/or validate the image channels.
        image_channels = image_channels.upper()

        if not image_channels:
            raise ValueError("Invalid image channels (empty).")

        self.channels = self.channels.lower()
        if self.channels is None or self.channels == "all" or self.channels == "":
            channels = image_channels
        elif self.channels == "auto":
            channels = image_channels
        else:
            channels = self.channels.upper()

        if not all([channel in image_channels for channel in channels]):
            raise ValueError(f"Invalid channel(s) for image: {channels}, initial value: {self.channels}")

        # Decide which channels the header should be written in.
        self.header_channels = self.header_channels.lower()
        if self.header_channels == "auto":
            if self.header_enabled and self.header_write_data_size and (self.header_write_pattern or self.header_position == "image_start"):
                if "A" in image_channels:
                    header_channels = "A"
                elif "B" in image_channels:
                    header_channels = "B"
                else:
                    header_channels = image_channels[0]
            else:
                header_channels = image_channels
        elif self.header_channels is None or self.header_channels == "all" or self.header_channels == "":
            header_channels = image_channels
        else:
            header_channels = self.header_channels.upper()

        if not all([channel in image_channels for channel in header_channels]):
            raise ValueError(f"Invalid header channel(s) for image: {header_channels}")

        # Decide where the header should be written.
        header_position = self.header_position.lower().strip()
        if header_position == "auto":
            if self.header_enabled and self.header_write_data_size and self.header_write_pattern:
                header_position = "image_start"
            else:
                header_position = "before_data"
        else:
            header_position = self.header_position.lower().strip()

        return {
            "position": self.offset,
            "channels": channels,
            "bit_frequency": self.bit_frequency,
            "byte_spacing": self.byte_spacing,
            "hash_check": self.hash_check,
            "compression_enabled": self.compression and self.compression != "none",
            "compression": self.compression,
            "compression_strength": self.compression_strength,
            "advanced_redundancy": self.advanced_redundancy,
            "advanced_redundancy_correction_factor": self.advanced_redundancy_correction_factor,
            "repetitive_redundancy": self.repetitive_redundancy,
            "repetitive_redundancy_mode": self.repetitive_redundancy_mode,
            "header_enabled": self.header_enabled,
            "header_write_data_size": self.header_write_data_size,
            "header_write_pattern": self.header_write_pattern,
            "header_channels": header_channels,
            "header_position": header_position,
            "header_bit_frequency": self.header_bit_frequency,
            "header_byte_spacing": self.header_byte_spacing,
            "header_repetitive_redundancy": self.header_repetitive_redundancy,
            "header_advanced_redundancy": self.header_advanced_redundancy,
            "header_advanced_redundancy_correction_factor": self.header_advanced_redundancy_correction_factor,
        }

    def generate_header(self, data_len: int) -> bytes:
        """
        Generates the header.
        :param data_len: The length of the data.
        :return: The header.
        """
        header = b""
        if not self.header_enabled or not (self.header_write_data_size or self.header_write_pattern):
            return header

        if self.header_write_data_size:
            header += data_len.to_bytes(4, "big")

        if self.header_write_pattern:
            # TODO: Allow writing pattern in header (and maybe separate offset).
            header += b"\x01"
        else:
            header += b"\x00"

        # Apply redundancy
        header = self.apply_redundancy(header, "header")

        return header

    def compress_data(self, data: bytes, parameters_source: str = "data") -> bytes:
        """
        Compresses data using the pattern's compression pattern.
        :param data: The data to compress.
        :param parameters_source: The source of the compression parameters. Can be "data" or "header".
        :return: The compressed data.
        """
        if parameters_source == "header":
            return data  # Header compression is not supported.
        else:  # "data"
            compression = self.compression
            compression_strength = self.compression_strength

        return self.static_compress_data(data, compression, compression_strength)

    @staticmethod
    def static_compress_data(data: bytes, compression: str, compression_strength: int) -> bytes:
        logger = Pattern.get_logger()

        if compression and compression != "none":
            old_size = len(data)

            if compression == "zlib":
                new_data = zlib.compress(data, compression_strength)
            else:
                raise CompressionNotImplementedError(compression)

            compression_flag = b'0'
            new_size = len(new_data)
            if new_size < old_size:
                logger.debug(f"Compression reduced data size, using compressed data ({new_size}/{old_size} bytes).")
                data = new_data
                compression_flag = b'1'
            else:
                logger.info(f"Compression did not reduce data size, skipping compression ({new_size}/{old_size} bytes).")

            data = compression_flag + data

        return data

    def decompress_data(self, data: bytes, parameters_source: str = "data") -> bytes:
        """
        Decompresses data using the pattern's compression pattern.
        :param data: The data to decompress.
        :param parameters_source: The source of the compression parameters. Can be "data" or "header".
        :return: The decompressed data.
        """
        if parameters_source == "header":
            return data  # Header compression is not supported.
        else:  # "data"
            compression = self.compression

        return self.static_decompress_data(data, compression)

    @staticmethod
    def static_decompress_data(data: bytes, compression: str) -> bytes:
        if compression and compression != "none":
            if compression == "zlib":
                compression_flag, data_bytes = data[0], data[1:]

                if compression_flag == b'1':
                    return zlib.decompress(data)
            else:
                raise NotImplementedError(f"Compression pattern \"{compression}\" not implemented.")

        return data

    def apply_redundancy(self, data: bytes, parameters_source: str = "data") -> bytes:
        """
        Applies redundancy to data using the pattern's redundancy pattern.
        :param data: The data to apply redundancy to.
        :param parameters_source: The source of the redundancy parameters. Can be "data" or "header".
        :return: The data with redundancy applied.
        """
        if parameters_source == "header":
            repetitive_redundancy = self.header_repetitive_redundancy
            repetitive_redundancy_mode = "byte_per_byte"  # Header repetitive redundancy is always applied byte wise.
            advanced_redundancy = self.header_advanced_redundancy
            advanced_redundancy_correction_factor = self.header_advanced_redundancy_correction_factor
        else:  # "data"
            repetitive_redundancy = self.repetitive_redundancy
            repetitive_redundancy_mode = self.repetitive_redundancy_mode
            advanced_redundancy = self.advanced_redundancy
            advanced_redundancy_correction_factor = self.advanced_redundancy_correction_factor

        return self.static_apply_redundancy(data, repetitive_redundancy, repetitive_redundancy_mode, advanced_redundancy,
                                            advanced_redundancy_correction_factor)

    @staticmethod
    def static_apply_redundancy(data: bytes, repetitive_redundancy: int, repetitive_redundancy_mode: str, advanced_redundancy: str,
                                advanced_redundancy_correction_factor: float) -> bytes:
        # Advanced redundancy
        match advanced_redundancy.lower():
            case "reed_solomon" | "rs":
                data = rs_encode(data, advanced_redundancy_correction_factor)
            case "hamming" | "ham":
                raise NotImplementedError("Hamming code correction not implemented.")
            case "none" | "no" | None:
                data = data
            case _:
                raise ValueError(f"Invalid redundancy pattern \"{advanced_redundancy}\".")

        # Simple repetitive redundancy
        if repetitive_redundancy > 1:
            match repetitive_redundancy_mode.lower():
                case "byte_per_byte":
                    data = [byte for byte in data for _ in range(repetitive_redundancy)]
                case "block":
                    data = data * repetitive_redundancy
                case _:
                    raise ValueError(f"Invalid repetitive redundancy mode \"{repetitive_redundancy_mode}\".")

            data = bytes(data)

        return data

    def reconstruct_redundancy(self, data: bytes, parameters_source: str = "data") -> bytes:
        """
        Reconstructs data using the pattern's redundancy pattern, if any and if applicable.
        :param data: The data to reconstruct.
        :param parameters_source: The source of the redundancy parameters. Can be "data" or "header".
        :return: The reconstructed data.
        """
        if parameters_source == "header":
            repetitive_redundancy = self.header_repetitive_redundancy
            repetitive_redundancy_mode = "byte_per_byte"  # Header repetitive redundancy is always applied byte wise.
            advanced_redundancy = self.header_advanced_redundancy
            advanced_redundancy_correction_factor = self.header_advanced_redundancy_correction_factor
        else:  # "data"
            repetitive_redundancy = self.repetitive_redundancy
            repetitive_redundancy_mode = self.repetitive_redundancy_mode
            advanced_redundancy = self.advanced_redundancy
            advanced_redundancy_correction_factor = self.advanced_redundancy_correction_factor

        return self.static_reconstruct_redundancy(data, repetitive_redundancy, repetitive_redundancy_mode, advanced_redundancy,
                                                  advanced_redundancy_correction_factor)

    @staticmethod
    def static_reconstruct_redundancy(data: bytes, repetitive_redundancy: int, repetitive_redundancy_mode: str, advanced_redundancy: str,
                                      advanced_redundancy_correction_factor: float) -> bytes:
        # Simple repetitive redundancy
        if repetitive_redundancy > 1:
            # Reconstruct data using a majority vote method if there is an odd number of repetitions or if the vote is inconclusive due to an
            # even number of repetitions, use surrounding bytes to determine the correct byte.
            match repetitive_redundancy_mode.lower():
                # To simplify the function, the block mode is converted to byte_per_byte mode.
                case "byte_per_byte":
                    pass
                case "block":
                    # Using zip trick for fast alignment of bytes
                    chunk_size = len(data) // repetitive_redundancy
                    data = bytes(chain.from_iterable(zip(*[data[i:i + chunk_size] for i in range(0, len(data), chunk_size)])))
                case _:
                    raise ValueError(f"Invalid repetitive redundancy mode \"{repetitive_redundancy_mode}\".")

            # Reconstructing data
            reconstructed_data = bytearray()
            for i in range(0, len(data), repetitive_redundancy):
                group = data[i:i + repetitive_redundancy]
                byte_counts = {byte: group.count(byte) for byte in set(group)}

                if len(byte_counts) == 1:
                    majority_byte = list(byte_counts.keys())[0]
                else:
                    max_count = max(byte_counts.values())
                    candidates = [byte for byte, count in byte_counts.items() if count == max_count]

                    if len(candidates) == 1:
                        majority_byte = candidates[0]
                    else:
                        # Tie: Use neighbor checking mechanism
                        neighbors = Pattern.get_redundancy_neighbors(len(reconstructed_data), reconstructed_data,
                                                                     data, repetitive_redundancy)
                        neighbor_similarity = {byte: calculate_byte_distance(byte, neighbors) for byte in candidates}
                        majority_byte = min(neighbor_similarity, key=neighbor_similarity.get)

                reconstructed_data.append(majority_byte)

            data = reconstructed_data

        # Advanced redundancy
        match advanced_redundancy.lower():
            case "reed_solomon" | "rs":
                return rs_decode(data, advanced_redundancy_correction_factor)
            case "hamming" | "ham":
                raise NotImplementedError("Hamming code not implemented.")
            case "none" | "no" | None:
                return data
            case _:
                raise ValueError(f"Invalid redundancy pattern \"{advanced_redundancy}\".")

    @staticmethod
    def get_redundancy_neighbors(index: int, reconstructed_data: bytearray, input_data: bytes,
                                 repetitive_redundancy: int) -> list[int]:
        neighbors = []
        if index > 0:
            neighbors.append(reconstructed_data[index - 1])

        if index < len(input_data) // repetitive_redundancy - 1:
            next_neighbor_group = input_data[(index + 1) * repetitive_redundancy:(index + 2) * repetitive_redundancy]
            byte_counts = {byte: next_neighbor_group.count(byte) for byte in set(next_neighbor_group)}
            max_count = max(byte_counts.values())
            majority_bytes = [byte for byte, count in byte_counts.items() if count == max_count]

            if len(majority_bytes) == 1:  # Check if the next neighbor group has a clear majority vote
                neighbors.append(majority_bytes[0])

        return neighbors

    def compute_hash(self, data: Union[bytearray, bytes]) -> bytes:
        """
        Compute the hash of a bytearray.
        :param data: Bytearray to hash
        :return: The hash of the bytearray
        """
        if not self.hash_check:
            raise ValueError("Hashing is disabled for this pattern.")

        if isinstance(self.hash_check, bool) and self.hash_check:
            hash_algorithm = 'sha256'
        else:
            hash_algorithm = self.hash_check.lower()

        if hash_algorithm == "none":
            raise ValueError("Hashing is disabled for this pattern.")

        if hash_algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Invalid hash algorithm \"{self.hash_check}\".")

        return hashlib.new(hash_algorithm, data).digest()

    def calculate_max_data_size(self, image_size: tuple[int, int], image_mode: str) -> int:
        """
        Calculates the maximum size of the data that can be stored in an image with current pattern settings.
        :param image_size: The size of the image (width, height).
        :param image_mode: The Pillow image mode string (e.g., "RGB", "RGBA", "L", etc.).
        :return: The maximum size of the data.
        """
        generated_pattern = self.generate_pattern(image_mode)
        pixels = image_size[0] * image_size[1]

        # Filter the pattern channels based on the image mode
        available_channels = "".join([channel for channel in generated_pattern["channels"] if channel in image_mode])

        # Calculate the number of bits per pixel
        bits_per_pixel = len(available_channels) * self.bit_frequency

        # Calculate the number of bits per byte
        bits_per_byte = 8 * self.byte_spacing

        # Calculate the number of bytes that can be stored in the image
        raw_data_bytes = (pixels * bits_per_pixel) // bits_per_byte

        # Calculate the redundancy overhead
        if self.advanced_redundancy.lower() == "reed_solomon":
            # RS codes estimation
            rs_redundant_symbols = ceil(self.advanced_redundancy_correction_factor * raw_data_bytes * 2)
        else:
            rs_redundant_symbols = 0

        raw_data_bytes -= rs_redundant_symbols

        if self.repetitive_redundancy > 1:
            if self.repetitive_redundancy_mode.lower() in ["byte_per_byte", "block"]:
                max_data_size = raw_data_bytes // self.repetitive_redundancy
            else:
                max_data_size = raw_data_bytes
        else:
            max_data_size = raw_data_bytes

        return max_data_size

    @classmethod
    def from_dict(cls, pattern_dict: dict):
        # Extracting header if nested
        if "header" in pattern_dict:
            for k, v in pattern_dict["header"].items():
                pattern_dict[f"header_{k}"] = v

        del pattern_dict["header"]

        # Ensuring types
        if "channels" in pattern_dict:
            if isinstance(pattern_dict["channels"], list):
                pattern_dict["channels"] = ''.join(pattern_dict["channels"]).upper()

        if "header_channels" in pattern_dict:
            if isinstance(pattern_dict["header_channels"], list):
                pattern_dict["header_channels"] = ''.join(pattern_dict["header_channels"]).upper()

        # Ensuring types for other parameters
        for key, value in pattern_dict.items():
            if key.endswith("_redundancy_correction_factor"):
                pattern_dict[key] = float(value)
            elif key.endswith("redundancy") or key.endswith("strength") or key.endswith("bit_frequency") or key.endswith("byte_spacing") or key.endswith("offset"):
                if key not in ["advanced_redundancy", "header_advanced_redundancy"]:
                    pattern_dict[key] = int(value)
            elif key.endswith("_enabled") or key.endswith("_write_data_size") or key.endswith("_write_pattern"):
                pattern_dict[key] = bool(value)

        return cls(**pattern_dict)
