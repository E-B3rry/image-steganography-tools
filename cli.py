# Internal modules
import argparse

# Project modules
from IST import Encoder, Decoder, Pattern, version


# TODO: Support files in the CLI


def add_pattern_arguments(parser):
    pattern_group = parser.add_argument_group("pattern options")
    pattern_group.add_argument("--offset", type=int, default=0,
                               help="Offset in pixels from the top-left corner of the image "
                                    "(header included if enabled and in before_data position). (default: 0)")
    pattern_group.add_argument("--channels", default="all",
                               help="Channels to be used for encoding. "
                                    "When None, empty, 'all' or unknown, all channels are used. (default: 'all')")
    pattern_group.add_argument("--bit-frequency", type=int, default=1, help="Frequency of bits used for encoding (default: 1)")
    pattern_group.add_argument("--byte-spacing", type=int, default=1, help="Spacing between bytes in the encoding (default: 1)")
    pattern_group.add_argument("--hash-check", default="sha256",
                               help="Hash algorithm for data integrity check. Set to 'none' to disable. (default: 'sha256')")
    pattern_group.add_argument("--compression", default="none", help="Data compression method. Options: 'zlib', 'none' (default)")
    pattern_group.add_argument("--compression-strength", type=int, default=6, help="Compression strength (1-9). (default: 6)")
    pattern_group.add_argument("--advanced-redundancy", default="reed_solomon",
                               help="Advanced redundancy method. Options: 'reed_solomon' (default), 'hamming', 'none'")
    pattern_group.add_argument("--advanced-redundancy-correction-factor", type=float, default=0.1,
                               help="Advanced redundancy correction factor. Allowed range ]0, 1] (default: 0.1)")
    pattern_group.add_argument("--repetitive-redundancy", type=int, default=1,
                               help="Repetitive redundancy factor. If 1, no repetitive redundancy is applied. (default: 1)")
    pattern_group.add_argument("--repetitive-redundancy-mode", default="byte_per_byte",
                               help="Repetitive redundancy mode. Options: 'byte_per_byte' (default), 'block'")
    pattern_group.add_argument("--header-enabled", action="store", nargs="?", const=True, default=True, type=bool,
                               help="Enable or disable header for encoding (default: True)")
    pattern_group.add_argument("--header-write-data-size", action="store", nargs="?", const=True, default=True, type=bool,
                               help="Enable or disable writing data size in the header (default: True)")
    pattern_group.add_argument("--header-write-pattern", action="store", nargs="?", const=True, default=False, type=bool,
                               help="Enable writing pattern in the header (default: False)")
    pattern_group.add_argument("--header-channels", default="auto",
                               help="Channels to be used for header encoding. "
                                    "When 'auto', channels are selected based on header discoverability. (default: 'auto')")
    pattern_group.add_argument("--header-position", default="auto",
                               help="Header position in the image. Options: 'auto' (default), 'image_start', 'before_data'")
    pattern_group.add_argument("--header-bit-frequency", type=int, default=1, help="Header bit frequency for encoding (default: 1)")
    pattern_group.add_argument("--header-byte-spacing", type=int, default=1, help="Spacing between bytes in the header encoding (default: 1)")
    pattern_group.add_argument("--header-repetitive-redundancy", type=int, default=5,
                               help="Repetitive redundancy factor for header. If 1, no repetitive redundancy is applied.")
    pattern_group.add_argument("--header-advanced-redundancy", default="reed_solomon",
                               help="Advanced redundancy method for header. Options: 'reed_solomon' (default), 'hamming', 'none'")
    pattern_group.add_argument("--header-advanced-redundancy-correction-factor", type=float, default=0.1,
                               help="Advanced redundancy correction factor for header. Allowed range ]0, +inf] (default: 0.1)")

    return parser


def main():
    parser = argparse.ArgumentParser(description="Image Steganography Tools")
    subparsers = parser.add_subparsers(dest="command")

    # Encoder
    encode_parser = subparsers.add_parser("encode", help="Encode data into an image")
    encode_parser.add_argument("input_image", help="Path to the input image")
    encode_parser.add_argument("output_image", help="Path to the output image")
    encode_parser.add_argument("--data", help="Data to be encoded")
    encode_parser.add_argument("--data-file", help="Path to a file containing data to be encoded")
    add_pattern_arguments(encode_parser)

    # Decoder
    decode_parser = subparsers.add_parser("decode", help="Decode data from an image")
    decode_parser.add_argument("input_image", help="Path to the input image")
    add_pattern_arguments(decode_parser)

    # Version
    version_parser = subparsers.add_parser("version", help="Show the current version of the package")

    args = parser.parse_args()

    if args.command in ["encode", "decode"]:
        pattern = Pattern(
            offset=args.offset,
            channels=args.channels,
            bit_frequency=args.bit_frequency,
            byte_spacing=args.byte_spacing,
            hash_check=args.hash_check,
            compression=args.compression,
            compression_strength=args.compression_strength,
            advanced_redundancy=args.advanced_redundancy,
            advanced_redundancy_correction_factor=args.advanced_redundancy_correction_factor,
            repetitive_redundancy=args.repetitive_redundancy,
            repetitive_redundancy_mode=args.repetitive_redundancy_mode,
            header_enabled=args.header_enabled,
            header_write_data_size=args.header_write_data_size,
            header_write_pattern=args.header_write_pattern,
            header_channels=args.header_channels,
            header_position=args.header_position,
            header_bit_frequency=args.header_bit_frequency,
            header_byte_spacing=args.header_byte_spacing,
            header_repetitive_redundancy=args.header_repetitive_redundancy,
            header_advanced_redundancy=args.header_advanced_redundancy,
            header_advanced_redundancy_correction_factor=args.header_advanced_redundancy_correction_factor,
        )

        if args.command == "encode":
            if not (args.data or args.data_file):
                parser.error("Either --data or --data-file must be provided for encoding")

            if args.data_file:
                with open(args.data_file, "rb") as file:
                    data = file.read()
            else:
                data = args.data

            encoder = Encoder(pattern=pattern)
            encoder.load_image(args.input_image)
            encoder.process(data=data, output_path=args.output_image)
            print(f"Data encoded into {args.output_image}")

        elif args.command == "decode":
            decoder = Decoder(pattern=pattern)
            decoder.load_image(args.input_image)
            decoded_data = decoder.process()
            print("Decoded data:", decoded_data)

    elif args.command == "version":
        print(f"Image Steganography Tools v{version}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
