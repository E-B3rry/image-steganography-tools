# Image Steganography Tools

![Logo](img/logo-transparent.png)

Image Steganography Tools is a Python library designed to provide functionality for hiding and revealing text or files within images. It supports various image formats and allows users to customize the encoding and decoding process with different patterns.

## Features

- Supports multiple image formats: PNG, BMP, PGM and PPM (more to come)
- Customizable encoding and decoding patterns
- *[Upcoming] Integrating patterns data directly into the image for hassle-free decoding*
- Redundancy and hash check options for improved data integrity
- Easy-to-use API for encoding and decoding operations
- Command-line interface for quick access
- GUI App for user-friendly interaction

## Installation

To install the Image Steganography Tools library, simply clone the repository and install the required dependencies:

```bash
git clone https://github.com/E-B3rry/image-steganography-tools.git
cd image-steganography-tools
pip install -r requirements.txt
```

## Usage

### Basic Usage

To use the library, first import the necessary modules:

```python
from IST import Encoder, Decoder, Pattern, version
```

Next, create a pattern for encoding and decoding:

```python
pattern = Pattern(
    channels="RGBA",
    bit_frequency=1,
    byte_spacing=2,
    advanced_redundancy="reed_solomon",
    advanced_redundancy_correction_factor=0.1,
    repetitive_redundancy=1,
    hash_check=True,
)
```

To encode data into an image:

```python
# To encode data into an image
encoder = Encoder()

# Load an image and pattern
encoder.load_image("path/to/image.png")
encoder.load_pattern(pattern)

# Hide the data and save the processed image
encoder.process(data="Secret message", output_path="path/to/processed_image.png")
```

To decode data from an image:

```python
decoder = Decoder()

# Load an image and pattern
decoder.load_image("path/to/processed_image.png")
decoder.load_pattern(pattern)

# Extract the hidden data
decoded_data = decoder.process()

print(decoded_data)
```

### Advanced Usage

You can customize the encoding and decoding process by modifying the pattern parameters:

- `channels`: The color channels to use for encoding (e.g., "auto", "all", "RGBA", "RGB", "A")
- `bit_frequency`: The number of least significant bits to use for encoding (1-8)
- `byte_spacing`: The spacing between encoded bytes in the image (1-x)
- `advanced_redundancy`: The advanced redundancy algorithm to use for error correction (e.g., "reed_solomon", "hamming", "none")
- `advanced_redundancy_correction_factor`: The correction factor for the advanced redundancy algorithm (0-1)
- `repetitive_redundancy`: The number of times each byte is repeated for error correction (odd numbers recommended)
- `repetitive_redundancy_mode`: The mode for applying repetitive redundancy (e.g., "byte_per_byte", "block")
- `hash_check`: Whether to include a hash for data integrity checking (True/False/Other)
- `header_enabled`: Whether to enable the header for storing pattern information (True/False)
- `header_channels`: The color channels to use for encoding the header (e.g., "auto", "all", "RGBA", "RGB", "A")
- `header_bit_frequency`: The number of least significant bits to use for encoding the header (1-8)
- `header_byte_spacing`: The spacing between encoded bytes in the header (1-x)

For example, to create a pattern with higher redundancy and no hash check:

```python
pattern = Pattern(
    channels="RGBA",
    bit_frequency=1,
    byte_spacing=2,
    advanced_redundancy="reed_solomon",
    advanced_redundancy_correction_factor=0.1,
    repetitive_redundancy=3,
    repetitive_redundancy_mode="byte_per_byte",
    hash_check=False,
    header_enabled=True,
    header_channels="RGBA",
    header_bit_frequency=1,
    header_byte_spacing=2,
)
```

## Testing

To run the tests, navigate to the `tests` directory and execute the test scripts:

```bash
cd tests
python test_base.py
python test_encoder_decoder.py
python test_pattern.py
python test_redundancy.py
python test_utils.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes or improvements.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Pillow (PIL Fork)](https://pillow.readthedocs.io/en/stable/) for image processing
- [reedsolo](https://pypi.org/project/reedsolo/) for Reed-Solomon error correction
- [Eel](https://pypi.org/project/Eel/) for the GUI App
- [l10n](https://pypi.org/project/l10n/) for localization support