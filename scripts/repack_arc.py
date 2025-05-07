import struct
import os
import sys
import zlib

def validate_directory(path):
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a valid directory.")
        # sys.exit(1)  # Removed to allow script to continue

    files = [os.path.relpath(os.path.join(root, f), path).replace("\\", "/")
             for root, _, filenames in os.walk(path)
             for f in filenames]

    if not files:
        print(f"Error: Directory '{path}' contains no files.")
        sys.exit(1)
    return set(files)  # Use set for faster lookup

def get_properties_path(directory):
    base_name = os.path.basename(directory.rstrip(os.sep))
    if not base_name:
        print("Error: Base name of directory is empty.")
        sys.exit(1)

    parent_dir = os.path.dirname(os.path.abspath(directory))
    return os.path.join(parent_dir, base_name + ".properties")

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
                        'fullpath': parts[3].replace("\\", "/"),
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

def validate_properties_entries(entries, file_set):
    missing_files = []
    found_files = set()
    expected_basenames = set()

    for entry in entries:
        basename = os.path.basename(entry['fullpath'])
        #print(entry)
        expected_basenames.add(basename)
        match = next((p for p in file_set if os.path.basename(p) == basename), None)
        if match:
            found_files.add(match)
        else:
            missing_files.append(entry['fullpath'])

    extra_files = [f for f in file_set if os.path.basename(f) not in expected_basenames]

    if missing_files:
        print(f"Error: The following files from properties were not found in directory:")
        for missing in missing_files:
            print(f"  - {missing}")
        sys.exit(1)

    if extra_files:
        print("Error: The following files are present in the directory but missing in properties:")
        for extra in extra_files:
            print(f"  - {extra}")
        sys.exit(1)

def write_binary_files(base_name, entries, dir_path):
    output_dir = "C:\\temp"
    header_path = os.path.join(output_dir, f"{base_name}.header.bin")
    data_path = os.path.join(output_dir, f"{base_name}.data.bin")
    final_path = os.path.join(output_dir, f"{base_name}")

    #ext_map = {
    #    '.tex': 0x241F5DEB,
    #    '.gmd': 0x242BB29A,
    #    '.gii': 0x07F768AF,
    #    '.gfd': 0x2D462600,
    #    '.gui': 0x22948394,
    #    '.xfs': 0x0AAF2DB2,
    #}

    try:
        with open(header_path, 'wb') as header_file, open(data_path, 'wb') as data_file:
            header_file.write(b'ARC\x00')
            header_file.write(struct.pack('<HH', 0x0010, len(entries)))
            header_file.write(b'\x00' * (12 - header_file.tell()))

            data_offset = 0x8000

            for index, entry in enumerate(entries):
                original_path = entry['fullpath'].replace('/', '\\')
                path_no_ext, extension = os.path.splitext(original_path)
                encoded_path = path_no_ext.encode('utf-8')
                padded_path = encoded_path.ljust(64, b'\x00')
                header_file.write(padded_path)

                #if extension.lower() not in ext_map:
                #    print(f"Error: Unsupported file extension '{extension}'")
                #    sys.exit(1)

                #unk1_value = ext_map[extension.lower()]
                header_file.write(struct.pack('<I', int(entry['unknown_value'],16)))
                
                #print(int(entry['unknown_value'],16))
                #input()

                full_input_path = os.path.join(dir_path, entry['fullpath'].replace('/', os.sep))
                try:
                    with open(full_input_path, 'rb') as f:
                        raw_data = f.read()
                except FileNotFoundError:
                    print(f"Error: File not found: {full_input_path}")
                    sys.exit(1)

                if entry['compressed']:
                    compressor = zlib.compressobj(entry['compression_level'], zlib.DEFLATED, zlib.MAX_WBITS)
                    comp_data = compressor.compress(raw_data) + compressor.flush()
                else:
                    comp_data = raw_data

                comp_size = len(comp_data)
                current_offset = data_offset
                data_file.write(comp_data)
                data_offset += len(comp_data)
                expected = entry['comp_size']
                #if comp_size != expected:
                    #print(f"⚠️  COMP size mismatch for {entry['fullpath']}: expected {expected}, got {comp_size}")
                header_file.write(struct.pack('<I', entry['comp_size']))
                raw_field = len(raw_data)
                header_file.write(struct.pack('<I', raw_field | 0x40000000))
                header_file.write(struct.pack('<I', current_offset))

                #print(f"[{index+1:04}/{len(entries):04}] {entry['fullpath'].replace('/', '\\')} | RAW: {len(raw_data)} | COMP: {comp_size} | OFFSET: 0x{data_offset:08X}")

            # Pad header to reach offset 0x8000
            current_pos = header_file.tell()
            if current_pos < 0x8000:
                header_file.write(b'\x00' * (0x8000 - current_pos))

        # Merge header and data into final output file
        with open(final_path, 'wb') as final_file:
            with open(header_path, 'rb') as header_file:
                final_file.write(header_file.read())
            with open(data_path, 'rb') as data_file:
                final_file.write(data_file.read())

        print(f"Merged ARC written to {final_path}")
    except IOError as e:
        print(f"Failed to write binary files: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python repack_arc.py <directory>")
        sys.exit(1)

    dir_path = sys.argv[1]
    base_name = os.path.basename(dir_path.rstrip(os.sep))

    files_in_dir = validate_directory(dir_path)
    properties_path = get_properties_path(dir_path)
    entries = load_properties(properties_path)
    validate_properties_entries(entries, files_in_dir)

    write_binary_files(base_name, entries, dir_path)

if __name__ == '__main__':
    main()
