import struct
import os
import sys
import zlib
from pathlib import Path

# Validates that a directory exists and contains files, returns relative file paths
def validate_directory(path):
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")

    files = [os.path.relpath(os.path.join(root, f), path).replace("\\", "/")
             for root, _, filenames in os.walk(path)
             for f in filenames]

    if not files:
        print(f"Error: Directory '{path}' contains no files.")
        sys.exit(1)
    return set(files)

# Constructs path to the .properties file (sibling to the ARC folder)
def get_properties_path(directory):
    base_name = os.path.basename(directory.rstrip(os.sep))
    parent_dir = os.path.dirname(os.path.abspath(directory))
    return os.path.join(parent_dir, base_name + ".properties")

# Determines zlib compression level based on known signatures
def detect_compression_level(signature_hex):
    try:
        sig = int(signature_hex, 16)
        if sig == 0x00000178:
            return 1
        elif sig == 0x0000da78:
            return 9
        elif sig == 0x00009c78:
            return 6
    except ValueError:
        pass
    return None

# Loads and parses the .properties file into a list of entry dictionaries
# Each entry describes metadata for one ARC file
def load_properties(properties_path):
    entries = []
    try:
        with open(properties_path, 'r', encoding='utf-16', errors='replace') as prop_file:
            for line in prop_file:
                line = line.strip()
                if not line or line.startswith("OFFSET"):
                    continue
                parts = line.split(';')
                if len(parts) >= 7:
                    compression_level = detect_compression_level(parts[5].strip())
                    if compression_level is None:
                        print(f"Error: Unknown compression signature '{parts[5].strip()}' in properties file.")
                        sys.exit(1)
                    entry = {
                        #'fullpath': parts[3].replace("\\", "/"),
                        'fullpath': parts[3],
                        'compressed': parts[4].strip().upper() == 'YES',
                        'signature': parts[5].strip(),
                        'compression_level': compression_level,
                        'file_offset': parts[0].strip(),
                        'unknown_value': parts[1].strip(),
                        'raw_size': int(parts[7].strip()),
                        'comp_size': int(parts[6].strip())
                    }
                    entries.append(entry)
    except IOError as e:
        print(f"Failed to read properties file: {e}")
        sys.exit(1)
    return entries

# Ensures all files referenced in the .properties exist in the directory, and no extras exist
def validate_properties_entries(entries, file_set):
    missing_files = []
    found_files = set()
    expected_basenames = set()

    for entry in entries:
        basename = os.path.basename(entry['fullpath'])
        expected_basenames.add(basename)
        match = next((p for p in file_set if os.path.basename(p) == basename), None)
        if match:
            found_files.add(match)
        else:
            missing_files.append(entry['fullpath'])

    extra_files = [f for f in file_set if os.path.basename(f) not in expected_basenames]

    if missing_files:
        print(f"Error: Missing files from properties:")
        for missing in missing_files:
            print(f"  - {missing}")
        sys.exit(1)

    if extra_files:
        print("Error: Extra files present not listed in properties:")
        for extra in extra_files:
            print(f"  - {extra}")
        sys.exit(1)

# Writes the final ARC file with embedded header and data blocks
# Places the output in a mirrored subpath relative to MOD_PATH_DIR
def write_binary_files(base_name, entries, dir_path, output_root):
    # Preserve folder hierarchy relative to ARC_EXTRACTED_DIR, but avoid nesting filename in path
    relative_output_dir = Path(dir_path).relative_to(Path(os.environ['ARC_EXTRACTED_DIR']))
    full_output_dir = output_root / relative_output_dir.parent
    full_output_dir.mkdir(parents=True, exist_ok=True)

    final_path = full_output_dir / base_name

    try:
        with open(final_path, 'wb') as final_file:
            # Write ARC header: magic, version, and entry count
            final_file.write(b'ARC\x00')
            final_file.write(struct.pack('<HH', 0x0010, len(entries)))
            final_file.write(b'\x00' * (12 - final_file.tell()))

            data_offset = 0x8000
            entry_data = bytearray()

            for entry in entries:
                # Pad file path (without extension) to 64 bytes
                path_no_ext, _ = os.path.splitext(entry['fullpath'])

                encoded_path = path_no_ext.encode('utf-8')                
                final_file.write(encoded_path.ljust(64, b'\x00'))

                # Unknown value field (likely type hash or magic)
                final_file.write(struct.pack('<I', int(entry['unknown_value'], 16)))

                full_input_path = Path(dir_path) / entry['fullpath']
                try:
                    with open(full_input_path, 'rb') as f:
                        raw_data = f.read()
                except FileNotFoundError:
                    print(f"Error: File not found: {full_input_path}")
                    sys.exit(1)

                # Apply compression if required
                if entry['compressed']:
                    comp_data = zlib.compress(raw_data, entry['compression_level'])
                else:
                    comp_data = raw_data

                # Entry metadata: compressed size, raw size | 0x40000000, data offset
                final_file.write(struct.pack('<I', len(comp_data)))
                #final_file.write(struct.pack('<I', entry['comp_size']))
                final_file.write(struct.pack('<I', len(raw_data) | 0x40000000))
                final_file.write(struct.pack('<I', data_offset))

                entry_data.extend(comp_data)
                data_offset += len(comp_data)

            # Pad header to 0x8000 before writing data segment
            current_pos = final_file.tell()
            if current_pos < 0x8000:
                final_file.write(b'\x00' * (0x8000 - current_pos))

            final_file.write(entry_data)

        print(f"Merged ARC written to {final_path}")
    except IOError as e:
        print(f"Failed to write ARC file: {e}")
        sys.exit(1)

# Entry point: resolves paths and coordinates loading, validation and writing
def main():
    output_root = Path(os.environ.get("MOD_PATH_DIR", "C:/temp"))

    # Input path can be passed as CLI arg or taken from ARC_EXTRACTED_DIR env
    if len(sys.argv) >= 2:
        dir_path = Path(sys.argv[1]).resolve()
        arc_extracted_dir = Path(os.environ.get("ARC_EXTRACTED_DIR"))
    else:
        root_input = os.environ.get("ARC_EXTRACTED_DIR")
        if not root_input:
            print("Error: Provide input path or set ARC_EXTRACTED_DIR.")
            sys.exit(1)
        dir_path = Path(root_input).resolve()
        arc_extracted_dir = dir_path

    base_name = dir_path.name
    files_in_dir = validate_directory(dir_path)
    properties_path = get_properties_path(str(dir_path))
    entries = load_properties(properties_path)
    validate_properties_entries(entries, files_in_dir)

    os.environ['ARC_EXTRACTED_DIR'] = str(arc_extracted_dir)
    write_binary_files(base_name, entries, dir_path, output_root)

if __name__ == '__main__':
    main()
