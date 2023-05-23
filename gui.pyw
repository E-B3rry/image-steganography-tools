# Internal modules
import base64
import io
import os
import sys
import threading

from PIL import Image

# Project modules
from IST import Encoder, Decoder, Pattern

# External modules
import eel


main_lock = threading.Lock()


def is_chrome_installed():
    paths = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "C:/Users/%USERNAME%/AppData/Local/Google/Chrome/Application/chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]

    for path in paths:
        if os.path.exists(os.path.expandvars(path)):
            return True

    return False


if not is_chrome_installed():
    print("Chromium is not installed on your system. Please download and install it from:")
    print("https://www.google.com/chrome/")
    exit()


eel.init("web")


@eel.expose
def encode_data(input_image, output_image, data, pattern):
    with main_lock:
        try:
            input_image_content = base64.b64decode(input_image.split(',')[1])
            input_image_file = io.BytesIO(input_image_content)
            input_image_pil = Image.open(input_image_file)

            encoder = Encoder(image=input_image_pil)
            encoder.load_pattern(Pattern.from_dict(pattern))
            encoder.process(data=data, output_path=output_image)
            return f"Data encoded and saved to {output_image}"
        except Exception as e:
            return f"Error while encoding: {e}"


@eel.expose
def decode_data(input_image, pattern, enforce_provided_pattern, data_length):
    with main_lock:
        try:
            if data_length:
                data_length = int(data_length)

            input_image_content = base64.b64decode(input_image.split(',')[1])
            input_image_file = io.BytesIO(input_image_content)
            input_image_pil = Image.open(input_image_file)

            decoder = Decoder(image=input_image_pil)
            decoder.load_pattern(Pattern.from_dict(pattern))
            decoded_data = decoder.process(enforce_provided_pattern=bool(enforce_provided_pattern), data_length=data_length)
            return f"Decoded data: {decoded_data}"
        except Exception as e:
            return f"Error while decoding: {e}"


eel.start('index.html', size=(1200, 600))

sys.exit()
