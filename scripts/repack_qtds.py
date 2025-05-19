from pathlib import Path
import sys
import os


VALID_HEADERS = {
    "TITLES", "OBJECTIVES", "FAIL_CONDITIONS", "CLIENTS",  "DESCRIPTIONS"
}

def is_valid_section_header(line):
    line = line.strip()
    return (
        line.startswith("[") and
        line.endswith("]") and
        line[1:-1] in VALID_HEADERS
    )

def encode_string_block(entries):
    block = bytearray()
    for key, text in entries:
        # Replace placeholder with actual CRLF during encoding
        cleaned = text.replace("\r\n", "")
        encoded = cleaned.replace("__CRLF__", "\r\n").encode("utf-8")
        block.extend(len(encoded).to_bytes(4, 'little'))
        block.extend(encoded)
    return block


def parse_text_file(txt_path):
    sections = {}
    current = None
    with open(txt_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    buffer = []
    for line in lines:
        if is_valid_section_header(line):
        #if line.strip().startswith("[") and line.strip().endswith("]"):
            if current and buffer:
                sections[current] = buffer
                buffer = []
            current = line.strip()[1:-1]
        elif current and "=" in line:
            key, val = line.split("=", 1)
            buffer.append((key.strip(), val))
        elif buffer:
            prev_key, prev_val = buffer.pop()
            buffer.append((prev_key, prev_val + "__CRLF__" + line.rstrip("\n")))

    if current and buffer:
        sections[current] = buffer

    for section, items in sections.items():
        for i, (key, val) in enumerate(items):
            if val.startswith("<<RAW_BYTES_"):
                index = int(key.split("_")[-1])
                binfile = txt_path.with_name(f"{txt_path.stem}{section}_{index:02}.bin")
                val = binfile.read_bytes().decode("utf-8", errors="replace")
                items[i] = (key, val)

    return sections


def main(txt_file):
    txt_path = Path(txt_file)
    base_name = txt_path.stem
    bin_dir = txt_path.parent
    #bin_dir="C:\\temp\\mh3u_ptbr\\arc_extracted\\arc\\quest\\us\\quest00.arc\\quest\\us"
    #print(bin_dir)

    output_base = Path(os.environ.get("ARC_EXTRACTED_DIR"))
    qtds_base = Path(os.environ.get("QTDS_TEXT_DIR"))
    try:
        rel_path = Path(txt_file).relative_to(qtds_base)
    except ValueError:
        print(f"❌ Error: {txt_file} is not inside {qtds_base}")
        return

    output_path = output_base / rel_path.parent
    output_path.mkdir(parents=True, exist_ok=True)
    print(output_path)
    output_path = output_path / f"{base_name}.qtds"
    
    parts = []
    parts.append((bin_dir / f"{base_name}.00.bin").read_bytes())
    sections = parse_text_file(txt_path)
    parts.append(encode_string_block(sections["TITLES"]))
    parts.append((bin_dir / f"{base_name}.01.bin").read_bytes())
    parts.append(encode_string_block(sections["OBJECTIVES"]))
    parts.append((bin_dir / f"{base_name}.02.bin").read_bytes())
    parts.append(encode_string_block(sections["FAIL_CONDITIONS"]))
    parts.append((bin_dir / f"{base_name}.03.bin").read_bytes())
    parts.append(encode_string_block(sections["CLIENTS"]))
    parts.append(encode_string_block(sections["DESCRIPTIONS"]))
    parts.append((bin_dir / f"{base_name}.04.bin").read_bytes())

    output_path.write_bytes(b"".join(parts))
    print(f"✅ Repacked to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python repack_qtds.py <path_to_txt_file>")
    else:
        main(sys.argv[1])
