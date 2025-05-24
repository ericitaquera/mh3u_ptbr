import struct
from PIL import Image

def decode_etc1a4(width, height, data):
    img = Image.new('RGBA', (width, height))
    pixels = img.load()

    blocks_w = (width + 3) // 4
    blocks_h = (height + 3) // 4

    offset = 0
    for by in range(blocks_h):
        for bx in range(blocks_w):
            block = data[offset:offset+8]
            alpha_block = data[offset+8:offset+16]
            offset += 16

            rgba_block = decode_etc1_block(block)

            for py in range(4):
                for px in range(4):
                    alpha_index = py * 2 + (px // 2)
                    alpha_nibble = (alpha_block[alpha_index] >> (4 * (1 - (px % 2)))) & 0xF
                    alpha = (alpha_nibble << 4) | alpha_nibble

                    x = bx * 4 + px
                    y = by * 4 + py

                    if x < width and y < height:
                        r, g, b = rgba_block[py * 4 + px]
                        pixels[x, y] = (r, g, b, alpha)

    return img

def decode_etc1_block(block):
    def extend_5(v):
        return (v << 3) | (v >> 2)

    def extend_4(v):
        return (v << 4) | v

    diff = (block[3] & 2) != 0
    flip = (block[3] & 1) != 0

    base_colors = []
    if diff:
        r1 = extend_5((block[0] >> 3) & 0x1F)
        g1 = extend_5(((block[0] & 0x7) << 2) | ((block[1] >> 6) & 0x3))
        b1 = extend_5((block[1] >> 1) & 0x1F)

        dr = ((block[1] & 0x1) << 2) | (block[2] >> 6)
        dg = (block[2] >> 3) & 0x7
        db = block[2] & 0x7

        dr = (dr ^ 0x4) - 0x4
        dg = (dg ^ 0x4) - 0x4
        db = (db ^ 0x4) - 0x4

        r2 = extend_5(((r1 >> 3) + dr) & 0x1F)
        g2 = extend_5(((g1 >> 3) + dg) & 0x1F)
        b2 = extend_5(((b1 >> 3) + db) & 0x1F)

        base_colors = [(r1, g1, b1), (r2, g2, b2)]
    else:
        r1 = extend_4((block[0] >> 4) & 0xF)
        g1 = extend_4(block[0] & 0xF)
        b1 = extend_4((block[1] >> 4) & 0xF)
        r2 = extend_4(block[1] & 0xF)
        g2 = extend_4((block[2] >> 4) & 0xF)
        b2 = extend_4(block[2] & 0xF)

        base_colors = [(r1, g1, b1), (r2, g2, b2)]

    table1 = (block[3] >> 5) & 0x7
    table2 = (block[3] >> 2) & 0x7

    modifier_tables = [
        [2, 8, -2, -8],
        [5, 17, -5, -17],
        [9, 29, -9, -29],
        [13, 42, -13, -42],
        [18, 60, -18, -60],
        [24, 80, -24, -80],
        [33, 106, -33, -106],
        [47, 183, -47, -183]
    ]

    pixels = []
    bitstring = struct.unpack('>I', block[4:8])[0]

    for py in range(4):
        for px in range(4):
            if (flip and py < 2) or (not flip and px < 2):
                base = 0
                table = table1
            else:
                base = 1
                table = table2

            idx = ((bitstring >> (15 - (py * 4 + px))) & 1) | (((bitstring >> (31 - (py * 4 + px))) & 1) << 1)
            modifier = modifier_tables[table][idx]

            r = max(0, min(255, base_colors[base][0] + modifier))
            g = max(0, min(255, base_colors[base][1] + modifier))
            b = max(0, min(255, base_colors[base][2] + modifier))

            pixels.append((r, g, b))

    return pixels

if __name__ == '__main__':
    print("ETC1A4 decoder module ready")
