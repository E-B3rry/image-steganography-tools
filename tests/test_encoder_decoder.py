import unittest
import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'src')
sys.path.insert(0, src_path)

from src.encoder import Encoder  # noqa: E402
from src.decoder import Decoder  # noqa: E402
from src.pattern import Pattern  # noqa: E402


def generate_test_patterns():
    test_patterns = []

    for channels in ["RGB", "RGBA", "BA", 'A']:
        for bit_frequency in range(1, 3):
            for redundancy in range(1, 3, 2):  # Only odd numbers for redundancy
                for byte_spacing in range(1, 3):
                    for hash_check in [True, False]:
                        pattern = Pattern(
                            channels=channels,
                            bit_frequency=bit_frequency,
                            byte_spacing=byte_spacing,
                            redundancy=redundancy,
                            hash_check=hash_check,
                        )
                        test_patterns.append(pattern)

    return test_patterns


class TestEncoderDecoder(unittest.TestCase):
    def test_encode_decode(self):
        test_patterns = generate_test_patterns()
        data = "This is a test string with utf-8 characters: ąęćłńóśźż ĄĘĆŁŃÓŚŹŻ 1234567890 !@#$%^&*()_+ -=[]\\;',./{}|:\"<>?`~\n"

        for pattern in test_patterns:
            with self.subTest(pattern=pattern.generate_pattern()):
                try:  # Catching the AssertionError to print the pattern that failed before raising it again
                    # First, encode the data using the pattern
                    encoder = Encoder()
                    encoder.encode("test_images/png/test_image.png", data, pattern, "test_images/png/encoded_image.png")

                    # Then, decode the data using the same pattern
                    decoder = Decoder()
                    decoded_data = decoder.decode("test_images/png/encoded_image.png", pattern)

                    # Check if the decoded data matches the original data
                    if pattern.hash_check:
                        self.assertEqual(decoded_data, data)
                    else:
                        self.assertTrue(decoded_data.startswith(data))
                except (AssertionError, ValueError):
                    print(f"Test failed for pattern: {pattern.generate_pattern()}")
                    print(f"Original data (len={len(data)}): {data}")
                    print(f"Decoded data (len={len(decoded_data)}): {decoded_data[:len(data) * 2]}\n")
                    raise

    # Add more test cases for different image formats


if __name__ == "__main__":
    unittest.main()
