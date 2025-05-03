#!/usr/bin/env python3
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

        magic_ext_map = {
            b'GMD\x00': '.gmd',
            b'GFD\x00': '.gfd',
            b'GUI\x00': '.gui',
            b'GII\x00': '.gii',
            b'TEX\x00': '.tex',
            b'MRL\x00': '.mrl',
            b'MOD\x00': '.mod',
            b'LMT\x00': '.lmt',
            b'EAN\x00': '.ean',
            b'EFL\x00': '.efl',
            b'XFS\x00': '.xfs',
            b'DCM\x00': '.dcm',
            b'ESQ\x00': '.esq',
            b'MSS\x00': '.mss',
            b'EMS\x00': '.ems',
            b'EMM\x00': '.emm',
            b'EMG\x00': '.emg',
            b'EML\x00': '.eml',
            b'EMT\x00': '.emt',
            b'EAR\x00': '.ear',
            b'EMC\x00': '.emc',
            b'HTD\x00': '.htd',
            b'BDD\x00': '.bdd',
            b'HTS\x00': '.hts',
            b'SDL\x00': '.sdl',
            b'rvl\x00': '.rvl',
            b'MADP': '.madp',            
            b'DMEM': '.dmem',
            b'SNDB': '.sndb',
            b'SREQ': '.sreq',
            b'QTDS': '.qtds',
            b'REV\x00': '.rev',
            b'CFL\x00': '.cfl',
            b'SBC\xFF': '.sbc',
            b'LFP\x00': '.lfp',

            # Add more if needed
        }

        magic = raw[:4]
        extension = magic_ext_map.get(magic)
        if not extension:
            print(f"Error: Can’t unpack {file.name}. Unknown magic header {magic.hex()} for file {entry['path']}, size {entry['raw_size']}")
            print(f"Magic (hex): 0x{magic.hex()} | Magic (ascii): {magic.decode('ascii', errors='replace')}")
            print(f"b\'{magic.decode('ascii', errors='replace')}\\x00\': \'.{magic.decode('ascii', errors='replace').lower()}\',")
            sys.exit(1)
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
