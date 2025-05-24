from unpack_tex.parser_3ds import parse_3ds
from pathlib import Path

def main():
    tex_file = Path('td_v_yoko00_ID.tex')
    parse_3ds(tex_file)

if __name__ == '__main__':
    main()
