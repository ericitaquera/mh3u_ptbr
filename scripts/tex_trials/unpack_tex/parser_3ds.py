import struct
from pathlib import Path
from PIL import Image
from unpack_tex.etc1a4_decoder import decode_etc1a4

def parse_3ds(file_path: Path):
    with open(file_path, 'rb') as f:
        magic = f.read(4)
        if magic == b'\x00XET':
            byte_order = '>'
        elif magic == b'TEX\x00':
            byte_order = '<'
        else:
            raise ValueError("Not a valid TEX file")

        version, format, img_count, mip_count = struct.unpack(byte_order + 'BBBB', f.read(4))
        width, height = struct.unpack(byte_order + 'HH', f.read(4))
        swizzle = struct.unpack(byte_order + 'B', f.read(1))[0]
        _ = f.read(3)  # Padding

        print(f"Header → version={version} format={format} img_count={img_count} mip_count={mip_count} width={width} height={height} swizzle={swizzle}")

        data_offset = 0x80 if swizzle == 0x40 else 0x10
        f.seek(data_offset)

        if format == 0x07:  # RGBA8888
            tex_size = width * height * 4
            tex_data = f.read(tex_size)
            img = Image.frombytes('RGBA', (width, height), tex_data)

        elif format == 0x0A:  # ETC1A4
            tex_size = ((width + 3) // 4) * ((height + 3) // 4) * 16
            tex_data = f.read(tex_size)
            img = decode_etc1a4(width, height, tex_data)

        else:
            raise NotImplementedError(f"Format {format} not supported yet")

        out = file_path.with_suffix('.png')
        img.save(out)
        print(f"✅ Saved to {out}")
