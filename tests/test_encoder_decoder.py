# Internal modules
import unittest
import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'src')
sys.path.insert(0, src_path)

# Project modules
from test_pattern import generate_test_patterns, filter_patterns  # noqa: E402
from src.encoder import Encoder  # noqa: E402
from src.decoder import Decoder  # noqa: E402


class TestEncoderDecoder(unittest.TestCase):
    def test_encode_decode(self):
        # Define the test data and image formats
        data = "This is a test string with utf-8 characters: ąęćłńóśźż ĄĘĆŁŃÓŚŹŻ 1234567890 !@#$%^&*()_+ -=[]\\;',./{}|:\"<>?`~\n"
        image_formats = ["bmp", "pgm", "png", "ppm"]  # , "jpeg", "webp"]

        # Test encoding and decoding for each image format and pattern
        for img_format in image_formats:
            success_count = 0
            count = 0

            # Choose used channels based on image format
            if img_format in ["bmp", "jpeg", "jpg", "ppm"]:
                channels = ["RGB", "RB", "G"]
            elif img_format in ["png", "webp"]:
                channels = ["RGB", "RGBA", "RB", "GA", "A"]
            elif img_format in ["pgm"]:
                channels = ["L"]
            else:
                raise ValueError(f"Image format {img_format} is not supported in the test")

            default_params = {
            }

            # # If the image format is compressible, edit the default parameters to ensure that the test makes sense
            # if img_format in ["jpeg", "jpg", "webp"]:
            #     default_params["header_bit_frequency"] = 2
            #     default_params["header_byte_spacing"] = 8
            #     default_params["header_repetitive_redundancy"] = 10
            #     default_params["header_advanced_redundancy"] = "reed_solomon"
            #     default_params["header_advanced_redundancy_correction_factor"] = 0.5

            # Generate test patterns for specific image format
            test_params = {
                "channels": channels,
                "bit_frequency": range(1, 3),
                "redundancy": range(1, 3, 2),
                "byte_spacing": range(1, 3),
                "hash_check": [True, False],
            }
            test_patterns = generate_test_patterns(default_params, test_params)

            for pattern in test_patterns:
                count += 1
                with self.subTest(img_format=img_format,
                                  pattern=pattern.generate_pattern(image_channels=pattern.channels, data_length=len(data))):
                    try:
                        # First, process the data using the pattern
                        encoder = Encoder()
                        input_path = f"test_images/{img_format}/test_image.{img_format}"
                        output_path = f"test_images/{img_format}/encoded_image.{img_format}"
                        encoder.process(input_path=input_path, data=data, pattern=pattern, output_path=output_path)

                        del encoder

                        # Then, process the data using the same pattern
                        decoder = Decoder()
                        decoded_data = decoder.process(file_path=output_path, pattern=pattern)

                        del decoder

                        # Check if the decoded data matches the original data
                        if pattern.hash_check:
                            self.assertEqual(decoded_data, data)
                        else:
                            self.assertTrue(decoded_data.startswith(data))

                        success_count += 1
                    except (AssertionError, ValueError):
                        try:
                            decoded_data
                        except NameError:
                            decoded_data = ""

                        print(f"Test failed for image format: \"{img_format}\" and pattern:",
                              f"{pattern.generate_pattern(image_channels=pattern.channels, data_length=len(data))}")
                        print(f"\nOriginal data (len={len(data)}): {data}")
                        print(f"Decoded data (len={len(decoded_data)}): {decoded_data[:len(data) * 2]}\n")
                        raise

            print(f">>> Tested {count} patterns for image format: {img_format}, {success_count} successful")


if __name__ == "__main__":
    unittest.main()
