from pathlib import Path
from tex_decoder import decode_texture
from tex_decoder import encode_texture

import struct

def unpack_tex(tex_path: Path, output_dir: Path):
    with tex_path.open('rb') as f:
        header = f.read(32)  # Example header size
        magic, width, height, format_code = struct.unpack('<4sIII', header[:16])
        assert magic == b'TEX\x00', "Not a valid TEX file"

        data = f.read()

    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / (tex_path.stem + '.png')

    decode_texture(data, width, height, png_path)

    meta_path = output_dir / (tex_path.stem + '.meta')
    with meta_path.open('w') as meta_file:
        meta_file.write(f'{width},{height},{format_code}\n')

    print(f'✅ Unpacked {tex_path.name} to {png_path.name}')

def pack_tex(png_path: Path, meta_path: Path, output_path: Path):
    with meta_path.open('r') as meta_file:
        width, height, format_code = map(int, meta_file.read().strip().split(','))

    data = encode_texture(png_path, width, height)

    header = struct.pack('<4sIII', b'TEX\x00', width, height, format_code)
    with output_path.open('wb') as out_file:
        out_file.write(header)
        out_file.write(data)

    print(f'✅ Repacked {png_path.name} to {output_path.name}')
