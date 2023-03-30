# Internal modules

# Project modules

# External modules
from PIL import Image


"""
Encoder module of the Image Steganography Tools library.
"""


class Encoder:
    def __init__(self, argument):
        self.blob = argument

    def load_pattern(self, pattern: any):
        self.pattern

    def encode(pixels: list[tuple[int, ...]], data: str, pattern: any) -> list[tuple[int, ...]]:
        pass


arg1 = "ceci est mon argument"

my_object = Encoder(arg1)
print(my_object)

my_object.load_pattern("blobfish")
print(my_object.blob)

del my_object
