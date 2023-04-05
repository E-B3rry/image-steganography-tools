# Internal modules
import zlib
import hashlib

# Project modules

# External modules
from PIL import Image


"""
Pattern generator and interpreter of the Image Steganography Tools library.
"""


class Pattern:
    def __init__(self, **kwargs):
        self.channels = kwargs.get("channels", "RGBA")
        self.bit_frequency = kwargs.get("bit_frequency", 1)
        self.byte_spacing = kwargs.get("byte_spacing", 1)
        self.redundancy = kwargs.get("redundancy", 1)
        self.hash_check = kwargs.get("hash_check", True)

        self.compression = kwargs.get("compression", False)
        self.compression_pattern = kwargs.get("compression_pattern", "zlib")
        self.compression_strength = kwargs.get("compression_strength", 6)  # Default for zlib is 6

    def generate_pattern(self, *args, **kwargs):
        return {
            "channels": self.channels,
            "bit_frequency": self.bit_frequency,
            "byte_spacing": self.byte_spacing,
            "redundancy": self.redundancy,
            "hash_check": self.hash_check,
            "compression": self.compression,
            "compression_pattern": self.compression_pattern,
            "compression_strength": self.compression_strength,
        }

    def compress_data(self, data: bytes) -> bytes:
        if self.compression:
            if self.compression_pattern == "zlib":
                return zlib.compress(data, self.compression_strength)
            else:
                raise NotImplementedError(f"Compression pattern \"{self.compression_pattern}\" not implemented.")
        else:
            return data

    def decompress_data(self, data: bytes) -> bytes:
        if self.compression:
            if self.compression_pattern == "zlib":
                return zlib.decompress(data)
            else:
                raise NotImplementedError(f"Compression pattern \"{self.compression_pattern}\" not implemented.")
        else:
            return data

    @staticmethod
    def compute_hash(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
