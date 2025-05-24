import os
import sys

def search_files(name_part, directory):
    print(f"🔍 Searching for files containing '{name_part}' in: {directory}\n")
    matches = []

    for root, _, files in os.walk(directory):
        for file in files:
            if name_part.lower() in file.lower():
                fullpath = os.path.join(root, file)
                matches.append(fullpath)

    if matches:
        for match in sorted(matches, key=lambda x: os.path.basename(x).lower()):
            print(match)
    else:
        print("❌ No matches found.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_files_by_name.py <name_substring> [directory]")
        sys.exit(1)

    name_part = sys.argv[1]
    directory = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    if not os.path.isdir(directory):
        print(f"❌ Invalid directory: {directory}")
        sys.exit(1)

    search_files(name_part, directory)

if __name__ == "__main__":
    main()
