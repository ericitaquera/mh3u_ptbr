import sys
from pathlib import Path

def resolve_text(arg: str) -> str:
    if arg.startswith("@"):
        return Path(arg[1:]).read_text(encoding="utf-8")
    return arg

if len(sys.argv) != 4:
    print("Usage: py replace_text.py <file_or_folder> <search> <replace>")
    print("You can use @file.txt to load search/replace from a file.")
    sys.exit(1)

target = Path(sys.argv[1])
search_text = resolve_text(sys.argv[2])
replace_text = resolve_text(sys.argv[3])

def process(file):
    content = file.read_text(encoding="utf-8")
    if search_text in content:
        file.write_text(content.replace(search_text, replace_text), encoding="utf-8")
        print(f"✓ Updated: {file}")

if target.is_file():
    process(target)

elif target.is_dir():
    for txt_file in target.glob("*.txt"):
        process(txt_file)
else:
    print(f"Error: {target} is not a valid file or directory.")
    sys.exit(1)
