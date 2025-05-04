import sys
import os

def number_blocks(input_path):
    if not os.path.isfile(input_path):
        print(f"❌ File not found: {input_path}")
        return

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}.numbered{ext}"

    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        count = 0
        for line in infile:
            if line.strip() == "--- BLOCK ---":
                count += 1
                outfile.write(f"--- BLOCK [{count:03}] ---\n")
            else:
                outfile.write(line)

    print(f"✅ Saved numbered file as: {output_path}")
    print(f"🔢 Total BLOCKs found: {count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python number_blocks.py <filename.txt>")
    else:
        number_blocks(sys.argv[1])
