# Internal modules
import argparse

# Project modules
from encoder import Encoder
from decoder import Decoder
from pattern import Pattern


def main():
    parser = argparse.ArgumentParser(description="Image Steganography Tools")
    subparsers = parser.add_subparsers(dest="command")

    # Encoder
    encode_parser = subparsers.add_parser("encode", help="Encode data into an image")
    encode_parser.add_argument("input_image", help="Path to the input image")
    encode_parser.add_argument("output_image", help="Path to the output image")
    encode_parser.add_argument("--data", help="Data to be encoded")
    encode_parser.add_argument("--data-file", help="Path to a file containing data to be encoded")

    # Decoder
    decode_parser = subparsers.add_parser("decode", help="Decode data from an image")
    decode_parser.add_argument("input_image", help="Path to the input image")

    # Version
    version_parser = subparsers.add_parser("version", help="Show the version of the package")

    args = parser.parse_args()

    if args.command == "encode":
        if not (args.data or args.data_file):
            parser.error("Either --data or --data-file must be provided for encoding")

        if args.data_file:
            with open(args.data_file, "r") as file:
                data = file.read()
        else:
            data = args.data

        pattern = Pattern()
        encoder = Encoder(pattern=pattern)
        encoder.load_image(args.input_image)
        encoder.process(data=data, output_path=args.output_image)
        print(f"Data encoded into {args.output_image}")

    elif args.command == "decode":
        pattern = Pattern()
        decoder = Decoder(pattern=pattern)
        decoder.load_image(args.input_image)
        decoded_data = decoder.process()
        print("Decoded data:", decoded_data)

    elif args.command == "version":
        import __version__
        print(f"Image Steganography Tools v{__version__.__version__}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
