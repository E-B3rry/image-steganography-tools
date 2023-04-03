# Internal modules
import hashlib

# Project modules

# External modules
from PIL import Image


"""
Pattern generator and interpreter of the Image Steganography Tools library.
"""


class Pattern:
    def __init__(self, channels: str = 'RGBA', bit_frequency: int = 1, byte_spacing: int = 1, redundancy: int = 1, hash_check: bool = True):
        self.channels = channels
        self.bit_frequency = bit_frequency
        self.byte_spacing = byte_spacing
        self.redundancy = redundancy
        self.hash_check = hash_check

    def generate_pattern(self, *args, **kwargs):
        return {
            'channels': self.channels,
            'bit_frequency': self.bit_frequency,
            'byte_spacing': self.byte_spacing,
            'redundancy': self.redundancy,
            'hash_check': self.hash_check,
        }

    @staticmethod
    def compute_hash(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
