import os
import sys

def get_target_directory():
    if len(sys.argv) > 2:
        return sys.argv[2]
    return os.getenv("GMD_TXT_PTBR_DIR")

def search_txt_files(search_term, directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(".txt"):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for lineno, line in enumerate(f, start=1):
                            if search_term in line:
                                print(f"✅ Match in {filepath} (line {lineno}): {line.strip()}")
                except Exception as e:
                    print(f"⚠️ Error reading {filepath}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_txt_string.py <search_string> [directory]")
        sys.exit(1)

    search_term = sys.argv[1]
    directory = get_target_directory()

    if not directory or not os.path.isdir(directory):
        print(f"❌ Invalid directory: {directory}")
        sys.exit(1)

    print(f"🔍 Searching for: '{search_term}' in {directory}")
    search_txt_files(search_term, directory)

if __name__ == "__main__":
    main()
