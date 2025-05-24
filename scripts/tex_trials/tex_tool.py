import sys
from pathlib import Path
from tex_parser import unpack_tex, pack_tex

if len(sys.argv) < 3:
    print("Usage:")
    print("  tex_tool.py unpack <input.tex> <output_folder>")
    print("  tex_tool.py pack <input.png> <input.meta> <output.tex>")
    sys.exit(1)

command = sys.argv[1]

if command == 'unpack':
    tex_path = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    unpack_tex(tex_path, output_dir)

elif command == 'pack':
    png_path = Path(sys.argv[2])
    meta_path = Path(sys.argv[3])
    output_path = Path(sys.argv[4])
    pack_tex(png_path, meta_path, output_path)

else:
    print(f"Unknown command {command}")
    sys.exit(1)
