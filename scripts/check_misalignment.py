from pathlib import Path
import sys

def read_arc_offset(file_path):
    entries = []

    with open(file_path, "rb") as f:
        f.seek(0x0C)  # Absolute position from file start
        count = 1

        while True:
            path_bytes = f.read(0x40)
            try:
                decoded_path = path_bytes.rstrip(b'\x00').decode('utf-8')
            except UnicodeDecodeError:
                decoded_path = "<Invalid UTF-8>"

            print(f"{count} - Path: {decoded_path}", end='; ')
    
            f.seek(4, 1)  # Relative seek from current position
            print(f"{count}", end='-')

            compressed_size_bytes = f.read(4)
            compressed_size = int.from_bytes(compressed_size_bytes, byteorder="little")
            print(f"compressed size: {compressed_size}", end='; ')

            uncompressed_size_bytes = f.read(4)
            uncompressed_size = int.from_bytes(uncompressed_size_bytes, byteorder="little") - 0x40000000
            print(f"Uncompressed size: {uncompressed_size}", end='; ')

            offset_bytes = f.read(4)
            if len(offset_bytes) < 4:
                print("Reached end of file.")
                break

            if offset_bytes == b"\x00\x00\x00\x00":
                print("Found 00 00 00 00. Stopping iteration.")
                break

            offset = int.from_bytes(offset_bytes, byteorder="little")
            print(f" Offset bytes:", ' '.join(f"{b:02x}" for b in offset_bytes))

            entries.append((offset, compressed_size, uncompressed_size))

            count += 1

    # Post-process: compare each entry's compressed size to space until next offset
    print("\n--- Validation ---")
    for i in range(len(entries) - 1):
        curr_offset, comp_size, _ = entries[i]
        next_offset, _, _ = entries[i + 1]
        available_space = next_offset - curr_offset

        if comp_size > available_space:
            print(f"[!] Entry {i+1}: Compressed size {comp_size} exceeds available space {available_space} between offsets {curr_offset}–{next_offset}")

if __name__ == "__main__":
    arc_path = Path("C:\\temp\\luma\\titles\\00040000000AE400\\romfs\\arc\\quest\\us\\quest00.arc")  # Change as needed
    read_arc_offset(arc_path)
