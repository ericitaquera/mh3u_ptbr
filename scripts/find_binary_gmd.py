import os
import sys

def get_search_bytes(search_str):
    return search_str.encode("utf-8")

def get_target_directory():
    if len(sys.argv) > 2:
        return sys.argv[2]
    return os.getenv("ARC_EXTRACTED_DIR")

def find_txt_counterpart(gmd_path):
    arc_root = os.getenv("ARC_EXTRACTED_DIR")
    gmd_txt_root = os.getenv("GMD_TXT_PTBR_DIR")
    qtds_txt_root = os.getenv("QTDS_TEXT_DIR")

    if not arc_root or not gmd_txt_root or not qtds_txt_root:
        return None

    rel_path = os.path.relpath(gmd_path, arc_root)
    txt_rel_path = os.path.splitext(rel_path)[0] + ".txt"

    # Check in GMD folder
    gmd_txt_path = os.path.join(gmd_txt_root, txt_rel_path)
    if os.path.isfile(gmd_txt_path):
        return gmd_txt_path

    # Check in QTDS folder
    qtds_txt_path = os.path.join(qtds_txt_root, txt_rel_path)
    if os.path.isfile(qtds_txt_path):
        return qtds_txt_path

    return None

def preview_txt_match(txt_file, search_string):
    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            for line in f:
                if search_string in line:
                    print(f"   → Sample: {line.strip()}")
                    return
    except Exception as e:
        print(f"   ⚠️  Could not read sample from {txt_file}: {e}")

def search_bin_files(search_bytes, directory, search_string):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith((".gmd", ".qtds")):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "rb") as f:
                        content = f.read()
                        if search_bytes in content:
                            print(f"✅ Match in: {filepath}")
                            txt_file = find_txt_counterpart(filepath)
                            if txt_file:
                                print(f"   → Translation found: {txt_file}")
                                preview_txt_match(txt_file, search_string)
                            #else:
                                #print("   ⚠️  No Translation found.")
                except Exception as e:
                    print(f"⚠️  Error reading {filepath}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_gmd_string.py <search_string> [directory]")
        sys.exit(1)

    search_string = sys.argv[1]
    directory = get_target_directory()

    if not "directory" or not os.path.isdir(directory):
        print(f"❌ Invalid directory: {directory}")
        sys.exit(1)

    search_bytes = get_search_bytes(search_string)
    #print(search_bytes)
    #search_bytes=b'S\x47\x72\x61\x6E\x6A\x61\x00'
    #print(search_bytes)
    #input()
    print(f"🔍 Searching for UTF-8 bytes: {search_bytes.hex(' ').upper()}")
    search_bin_files(search_bytes, directory, search_string)

if __name__ == "__main__":
    main()
