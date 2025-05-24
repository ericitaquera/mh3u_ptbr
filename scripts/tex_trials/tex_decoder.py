from PIL import Image
import numpy as np


def decode_texture(data, width, height, output_path):
    # Placeholder: Creates a dummy image
    image = Image.new('RGBA', (width, height), (255, 0, 0, 255))
    image.save(output_path)


def encode_texture(png_path, width, height):
    # Placeholder: Returns dummy binary data
    image = Image.open(png_path)
    image = image.resize((width, height))
    raw_data = b'\x00' * (width * height * 4)  # Dummy data
    return raw_data
