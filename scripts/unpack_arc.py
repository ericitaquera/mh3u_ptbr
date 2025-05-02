import os
import sys
import struct
import zlib

def read_arc_header(file):
    magic = file.read(4)
    if magic != b'ARC\x00':
        raise ValueError("Not a valid ARC file")

    version, num_files = struct.unpack('<HH', file.read(4))
    file.seek(12)  # skip reserved
    return num_files

def extract_entries(file, num_files):
    entries = []
    for _ in range(num_files):
        path = file.read(64).rstrip(b'\x00').decode('utf-8')
        unk1 = struct.unpack('<I', file.read(4))[0]
        comp_size = struct.unpack('<I', file.read(4))[0]
        raw_field = struct.unpack('<I', file.read(4))[0]
        offset = struct.unpack('<I', file.read(4))[0]

        raw_size = raw_field & 0x3FFFFFFF
        compressed = bool(raw_field & 0x40000000)

        entries.append({
            'path': path,
            'raw_field': raw_field,
            'unk1': unk1,
            'comp_size': comp_size,
            'raw_size': raw_size,
            'offset': offset,
            'compressed': compressed
        })
    return entries

def extract_files(file, entries, output_dir):
    properties = ["OFFSET;UNK1;FLAGS;FULLPATH;COMPRESSED;SIGNATURE;SIZE;ZSIZE"]

    for entry in entries:
        file.seek(entry['offset'])
        data = file.read(entry['comp_size'])

        if entry['compressed']:
            try:
                raw = zlib.decompress(data)
                compressed = "YES"
                sig_bytes = data[:2][::-1]
                sig = f"0x{int.from_bytes(sig_bytes, 'big'):08x}"
            except Exception as e:
                print(f"Failed to decompress {entry['path']}: {e}")
                raw = data
                compressed = "NO"
                sig = "0x00000000"

        else:
            input()
            raw = data
            compressed = "NO"
            sig = "0x00000000"

        ext_map = {
            0x241F5DEB: '.tex',
            0x242BB29A: '.gmd',
            0x07F768AF: '.gii',
            0x2D462600: '.gfd',
            0x22948394: '.gui',
            0x0AAF2DB2: '.xfs',            
            0x2749c8a8: '.mrl',
            0x58a15856: '.mod',
            0x76820d81: '.lmt',
            0x6d5ae854: '.efl',
            0x4c0db839: '.sdl',
        }
        if entry['unk1'] not in ext_map:
            print(f"Error: Can´t unpack {file.name}. Unknown UNK1 signature 0x{entry['unk1']:08x} for file {entry['path']}, size {entry['raw_size']}")  
             
            sys.exit(1)
        extension = ext_map[entry['unk1']]
        out_path = os.path.join(output_dir, entry['path'] + extension)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(raw)
        properties.append(f"{entry['offset']:#010x};0x{entry['unk1']:08x};0x{entry['raw_field']:08x};{entry['path'] + extension};{compressed};{sig};{entry['comp_size']};{entry['raw_size']}")

    return properties

def main():
    base_dir = os.environ.get('BASE_DIR')
    if not base_dir:
        print("Error: Required environment variable BASE_DIR is not set.")
        return
    if len(sys.argv) < 2:
        print("Usage: python unpack_arc.py <file.arc|dir> [output_dir]\nIf output_dir is omitted, $env:ARC_EXTRACTED_DIR will be used.")
        return

    input_path = sys.argv[1]
    output_root = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('ARC_EXTRACTED_DIR')
    if output_root is None:
        print("Error: No output directory provided and $env:ARC_EXTRACTED_DIR is not set.")
        return

    if not os.path.exists(input_path):
        print(f"Error: path '{input_path}' does not exist.")
        return

    arc_files = []
    if os.path.isdir(input_path) and not os.path.isfile(input_path):
        arc_files = []
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith('.arc'):
                    arc_files.append(os.path.join(root, f))
    elif os.path.isfile(input_path):
        arc_files = [input_path]
    else:
        print(f"Error: '{input_path}' is not a file or directory.")
        return

    for arc_path in arc_files:
        base_name = os.path.splitext(os.path.basename(arc_path))[0]
        output_ext = os.path.splitext(arc_path)[1].lstrip('.')
        romfs_dir = os.environ.get('ROMFS_DIR')
        if not romfs_dir:
            print("Error: Required environment variable ROMFS_DIR is not set.")
            return
        if romfs_dir and arc_path.startswith(romfs_dir):
            rel_path = os.path.relpath(os.path.dirname(arc_path), romfs_dir)
            output_dir = os.path.join(output_root, rel_path, base_name + '.' + output_ext)
            props_path = os.path.join(output_root, rel_path, os.path.basename(arc_path) + ".properties")
        else:
            output_dir = os.path.join(output_root, base_name + '.' + output_ext)
            props_path = os.path.join(output_root, os.path.basename(arc_path) + ".properties")

        with open(arc_path, 'rb') as file:
            num_files = read_arc_header(file)
            entries = extract_entries(file, num_files)
            props = extract_files(file, entries, output_dir)

        
        with open(props_path, 'w', encoding='utf-16') as f:
            f.write("\n".join(props))

        print(f"Saved properties: {props_path}")
        print(f"Output directory: {output_dir}")
        print(f"Extracted {len(entries)} files to {output_dir}")

if __name__ == '__main__':
    main()
