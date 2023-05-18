# Image Steganography Tools

Image Steganography Tools is a Python library designed to provide functionality for hiding and revealing text or files within images. It supports various image formats and allows users to customize the encoding and decoding process with different patterns.

## Features

- Supports multiple image formats: PNG, BMP, PGM, PBM, PPM, PNM (more to come)
- Customizable encoding and decoding patterns
- *[Upcoming] Integrating patterns data directly into the image for hassle-free decoding*
- Redundancy and hash check options for improved data integrity
- Easy-to-use API for encoding and decoding operations
- *[Upcoming] GUI App for user-friendly interaction*

## Installation

To install the Image Steganography Tools library, simply clone the repository and install the required dependencies:

```bash
git clone https://github.com/E-B3rry/ImageSteganographyTools.git
cd ImageSteganographyTools
pip install -r requirements.txt
```

## Usage

### Basic Usage

To use the library, first import the necessary modules:

```python
from image_steganography_tools.encoder import Encoder
from image_steganography_tools.decoder import Decoder
from image_steganography_tools.pattern import Pattern
```

Next, create a pattern for encoding and decoding:

```python
pattern = Pattern(
    channels="RGBA",
    bit_frequency=1,
    byte_spacing=2,
    redundancy=1,
    hash_check=True,
)
```

To encode data into an image:

```python
encoder = Encoder()
encoder.process("input_image.png", "Secret message", pattern, "output_image.png")
```

To decode data from an image:

```python
decoder = Decoder()
decoded_data = decoder.process("output_image.png", pattern)
print(decoded_data)
```

### Advanced Usage

You can customize the encoding and decoding process by modifying the pattern parameters:

- `channels`: The color channels to use for encoding (e.g., "RGBA", "RGB", "A")
- `bit_frequency`: The number of least significant bits to use for encoding (1-8)
- `byte_spacing`: The spacing between encoded bytes in the image
- `redundancy`: The number of times each bit is repeated for error correction (odd numbers only)
- `hash_check`: Whether to include a hash for data integrity checking (True/False)

For example, to create a pattern with higher redundancy and no hash check:

```python
pattern = Pattern(
    channels="RGBA",
    bit_frequency=1,
    byte_spacing=2,
    redundancy=3,
    hash_check=False,
)
```

## Testing

To run the tests, navigate to the `tests` directory and execute the test scripts:

```bash
cd tests
python test_base.py
python test_encoder_decoder.py
python test_pattern.py
python test_utils.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes or improvements.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Pillow (PIL Fork)](https://pillow.readthedocs.io/en/stable/) for image processing
- [l10n](https://pypi.org/project/l10n/) for localization support