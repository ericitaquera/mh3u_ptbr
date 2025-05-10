from pathlib import Path
import sys
import os

def read_string_table(data, offset, count):
    strings = []
    for _ in range(count):
        strlen = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4
        strings.append((offset - 4, strlen, data[offset:offset+strlen]))
        offset += strlen
    return strings, offset

def dump_table(label, items, text_file):
    text_file.write(f"[{label}]\n")
    for i, (_, _, raw) in enumerate(items):
        try:
            string = raw.decode('utf-8')
            string = string.replace("\r\n", "\n")
            text_file.write(f"{label}_{i}={string}\n")
        except UnicodeDecodeError:
            text_file.write(f"{label}_{i}=<<RAW_BYTES_{label}_{i}>>\n")
    #text_file.write("\n")

def main(input_file):
    data = Path(input_file).read_bytes()

    arc_base = Path(os.environ.get("ARC_EXTRACTED_DIR", "C:/temp/arc_extracted"))
    output_base = Path(os.environ.get("QTDS_TEXT_DIR", "C:/temp/qtds_text"))
    rel_path = Path(input_file).relative_to(arc_base)
    output_path = output_base / rel_path.parent
    output_path.mkdir(parents=True, exist_ok=True)

    base_name = Path(input_file).stem
    txt_file = output_path / f"{base_name}.txt"

    with txt_file.open("w", encoding="utf-8") as out_txt:
        # Save first 8 bytes
        (output_path / f"{base_name}.00.bin").write_bytes(data[:8])

        offset = 0x008
        titles, offset = read_string_table(data, offset, 5)
        dump_table("TITLES", titles, out_txt)

        # Save 2 bytes after titles
        (output_path / f"{base_name}.01.bin").write_bytes(data[offset:offset+2])
        offset += 2

        objectives, offset = read_string_table(data, offset, 5)
        dump_table("OBJECTIVES", objectives, out_txt)

        # Save 0x18 bytes after objectives
        (output_path / f"{base_name}.02.bin").write_bytes(data[offset:offset+0x18])
        offset += 0x18

        failures, offset = read_string_table(data, offset, 5)
        dump_table("FAIL_CONDITIONS", failures, out_txt)

        # Save 0x06 bytes after failures
        (output_path / f"{base_name}.03.bin").write_bytes(data[offset:offset+6])
        offset += 6

        clients, offset = read_string_table(data, offset, 5)
        dump_table("CLIENTS", clients, out_txt)

        descs, offset = read_string_table(data, offset, 5)
        dump_table("DESCRIPTIONS", descs, out_txt)

        # Save everything from here to EOF
        (output_path / f"{base_name}.04.bin").write_bytes(data[offset:])

    print(f"✅ Extraction complete: {txt_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python unpack_qtds.py <path_to_qtds_file>")
    else:
        main(sys.argv[1])
