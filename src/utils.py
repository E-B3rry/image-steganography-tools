# Internal modules
from math import ceil, floor
from typing import Union

# Project modules
from exceptions import UnsupportedImageFormatError

# External modules
import PIL
from PIL import Image
from reedsolo import RSCodec

from l10n import Locales


def get_image_bytes_size(img: Image) -> int:
    """
    Returns the size of an image in bytes. (Calculates the size of each pixel and multiplies it by the number of pixels)
    :param img: the Pillow image object
    :return: int
    """

    return img.size[0] * img.size[1] * len(img.getbands())


def get_image_pixels(img: Image) -> list[tuple[int, ...], ...]:
    """
    Returns a list of all image's pixels.
    :param img: the Pillow image object
    :return list:
    """
    return list(img.getdata())


def create_image_from_pixels(pixels: list, mode: str, size: tuple[int, int], ext: Union[str, None] = None) -> Image:
    """
    Creates a new image from the given list of pixels and prepares the image for saving it in desired format.
    :param pixels: the pixels list
    :param mode: the pixels list mode
    :param size: a tuple with size of the image (x, y)
    :param ext: optional: the desired extension
    :return:
    """
    img = Image.new(mode=mode, size=size)
    img.putdata(pixels)

    if ext:
        ext = ext.strip('.').upper()

        match ext:
            case "PNG" | "WEBP":
                img = img.convert("RGBA")
            case "JPEG" | "JPG" | "BMP" | "PPM":
                img = img.convert("RGB")
            case "PGM":
                img = img.convert("L")
            case _:
                raise UnsupportedImageFormatError()

    return img


# Reed Solomon
RS_CHUNK_SIZE = 255


def rs_encode(data: Union[bytearray, bytes], correction_factor: Union[float, int] = 0.5) -> bytearray:
    """
    Encodes the given data using Reed Solomon algorithm.
    :param data: The data to encode
    :param correction_factor: The correction factor
    :return: The encoded data
    """
    data_size = len(data)
    total_redundant_symbols = ceil(round(correction_factor * data_size * 2, 10))
    total_symbols = data_size + total_redundant_symbols

    num_chunks = ceil(total_symbols / RS_CHUNK_SIZE)

    if num_chunks == 0:
        return data

    remaining_data_symbols = data_size
    remaining_redundant_symbols = total_redundant_symbols

    rs_sum = 0
    data_sum = 0

    i = 0
    encoded_data = bytearray()
    while remaining_data_symbols > 0:
        max_data_symbols_in_chunk = floor(RS_CHUNK_SIZE / (1 + correction_factor * 2))
        data_symbols = min(remaining_data_symbols, max_data_symbols_in_chunk)
        rs_redundant_symbols = min(remaining_redundant_symbols, ceil(correction_factor * data_symbols * 2))

        chunk_start = data_size - remaining_data_symbols
        chunk_end = chunk_start + data_symbols

        data_chunk = data[chunk_start:chunk_end]
        data_symbols = len(data_chunk)

        remaining_data_symbols -= data_symbols
        remaining_redundant_symbols -= rs_redundant_symbols

        # print(f"Chunk {i}: {data_symbols} data symbols, {rs_redundant_symbols} redundant symbols")
        data_sum += data_symbols
        rs_sum += rs_redundant_symbols

        rs = RSCodec(rs_redundant_symbols, nsize=RS_CHUNK_SIZE)
        encoded_chunk = rs.encode(data_chunk)

        encoded_data.extend(encoded_chunk)
        i += 1

    # print(f"Total: {data_sum} data symbols, {rs_sum} redundant symbols")

    return encoded_data


def rs_decode(encoded_data: Union[bytearray, bytes], used_correction_factor: Union[float, int] = 0.5) -> bytearray:
    """
    Decodes the given data using Reed Solomon algorithm.
    :param encoded_data: The encoded data to decode
    :param used_correction_factor: The correction factor used to encode the data
    :return: The decoded data
    """

    encoded_data_size = len(encoded_data)

    decoded_data = bytearray()
    remaining_data_symbols = floor(round(encoded_data_size / (1 + used_correction_factor * 2), 10))
    remaining_redundant_symbols = encoded_data_size - remaining_data_symbols

    data_sum = 0
    rs_sum = 0

    i = 0
    while remaining_data_symbols > 0:
        max_data_symbols_in_chunk = floor(RS_CHUNK_SIZE / (1 + used_correction_factor * 2))
        data_symbols = min(remaining_data_symbols, max_data_symbols_in_chunk)
        rs_redundant_symbols = min(remaining_redundant_symbols, ceil(used_correction_factor * data_symbols * 2))

        chunk_start = encoded_data_size - remaining_data_symbols - remaining_redundant_symbols
        chunk_end = chunk_start + data_symbols + rs_redundant_symbols

        encoded_chunk = encoded_data[chunk_start:chunk_end]

        remaining_data_symbols -= data_symbols
        remaining_redundant_symbols -= rs_redundant_symbols

        # print(f"Chunk {i}: {data_symbols} data symbols, {rs_redundant_symbols} redundant symbols")
        data_sum += data_symbols
        rs_sum += rs_redundant_symbols

        if rs_redundant_symbols == 0:
            decoded_data.extend(encoded_chunk)
            continue

        rs = RSCodec(rs_redundant_symbols, nsize=RS_CHUNK_SIZE)
        decoded_chunk, _, _ = rs.decode(encoded_chunk)

        decoded_data.extend(decoded_chunk[:data_symbols])

        i += 1

    # print(f"Total: {data_sum} data symbols, {rs_sum} redundant symbols")

    return decoded_data


def calculate_byte_distance(candidate_byte: int, neighbors: list[int]) -> int:
    """
    Calculates the distance between a candidate byte and its neighbors.
    :param candidate_byte: Candidate byte
    :param neighbors: List of neighbor bytes
    :return: Distance
    """
    return sum(abs(candidate_byte - n) for n in neighbors)


def ranges_overlap(a, b, c, d) -> bool:
    """
    Checks if two ranges overlap.
    :param a: The first range start
    :param b: The first range end
    :param c: The second range start
    :param d: The second range end
    :return: A boolean indicating if the ranges overlap
    """
    return (c <= a <= d) or (c <= b <= d) or (a <= c <= b) or (a <= d <= b)
