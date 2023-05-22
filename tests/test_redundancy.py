import random
import unittest
import sys
from pathlib import Path

src_path = str(Path(__file__).resolve().parent.parent / 'IST')
sys.path.insert(0, src_path)

from IST.pattern import Pattern  # noqa: E402
from test_pattern import generate_test_patterns  # noqa: E402


class TestRedundancy(unittest.TestCase):
    def test_redundancy(self):
        default_params = {
            "offset": 0,
            "channels": "RGBA",
            "bit_frequency": 1,
            "byte_spacing": 1,
            "hash_check": "sha256",
            "compression": "none",
            "compression_strength": 6,
            "header_enabled": True,
            "header_write_data_size": True,
            "header_write_pattern": False,
            "header_channels": "auto",
            "header_position": "auto",
            "header_bit_frequency": 1,
            "header_byte_spacing": 1,
            "header_repetitive_redundancy": 5,
            "header_advanced_redundancy": "reed_solomon",
            "header_hamming_parity_bits": 3,
            "header_rs_redundant_symbols": 6,
        }

        test_params = {
            "advanced_redundancy": ["reed_solomon", "none"],
            "repetitive_redundancy": [1, 3, 5],
            "repetitive_redundancy_mode": ["byte_per_byte", "block"],
            "advanced_redundancy_correction_factor": [i / 100 for i in range(5, 100, 5)],
            "bit_frequency": [1, 2],
            "byte_spacing": [1, 2],
        }

        test_patterns = generate_test_patterns(default_params, test_params)

        test_patterns = [
            p for p in test_patterns
            if not (p.repetitive_redundancy == 1 and p.repetitive_redundancy_mode == "block")
            and not (p.advanced_redundancy == "none" and p.advanced_redundancy_correction_factor != 0.05)
        ]

        data = b"Hello, world! This is a test message for redundancy features. ([&*!,-_ ;])" * 100

        for pattern in test_patterns:
            current_pattern_summed_up = {
                "repetitive_redundancy": pattern.repetitive_redundancy,
                "repetitive_redundancy_mode": pattern.repetitive_redundancy_mode,
                "advanced_redundancy": pattern.advanced_redundancy,
                "advanced_redundancy_correction_factor": pattern.advanced_redundancy_correction_factor,
                "bit_frequency": pattern.bit_frequency,
                "byte_spacing": pattern.byte_spacing,
            }
            print(f"Testing pattern > {current_pattern_summed_up}")

            # Apply redundancy
            redundant_data = pattern.apply_redundancy(data)

            # Introduce corruption with half error rate than the correction factor or in case of repetitive
            # redundancy create error in some redundant bytes (but always let at least a majority of the redundant
            # bytes be correct)
            corrupted_data = bytearray(redundant_data)

            error_indices = []
            if pattern.advanced_redundancy == "reed_solomon":
                num_errors = int(len(data) * pattern.advanced_redundancy_correction_factor // 2)
                error_indices = random.sample(range(0, len(data), len(data) // num_errors), num_errors // 2 - 1)
            elif pattern.repetitive_redundancy > 1:
                if pattern.repetitive_redundancy_mode == "byte_per_byte":
                    num_errors = int(len(data) / 2)
                    error_indices = random.sample(
                        range(0, len(redundant_data), pattern.repetitive_redundancy),
                        num_errors
                    )
                else:
                    num_errors = int(len(data) / 2)
                    error_indices = random.sample(
                        range(0, len(redundant_data) // pattern.repetitive_redundancy),
                        num_errors
                    )

            for idx in error_indices:
                corrupted_data[idx] = random.randint(0, 255)

            # Reconstruct data
            reconstructed_data = pattern.reconstruct_redundancy(corrupted_data)

            # Check if the reconstructed data matches the original data
            self.assertEqual(data, reconstructed_data, f"Failed for pattern: {pattern.generate_pattern('RGBA')}")


if __name__ == "__main__":
    unittest.main()
