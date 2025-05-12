import os
import sys
import argparse
from pathlib import Path

# Argumentos
parser = argparse.ArgumentParser(description="Reempacota .txt + .header em um .gmd")
parser.add_argument("InputFile", help="Arquivo .txt de entrada")
args = parser.parse_args()

INPUT_FILE = Path(args.InputFile)
BASE_NAME = INPUT_FILE.stem

GMD_TXT_PTBR_DIR = Path(os.environ.get("GMD_TXT_PTBR_DIR", ""))
GMD_TXT_DIR = Path(os.environ.get("GMD_TXT_DIR", ""))
ARC_EXTRACTED_DIR = Path(os.environ.get("ARC_EXTRACTED_DIR", ""))

if not GMD_TXT_PTBR_DIR or not ARC_EXTRACTED_DIR or not GMD_TXT_DIR:
    print("Variáveis de ambiente GMD_TXT_PTBR_DIR, GMD_TXT_DIR e ARC_EXTRACTED_DIR devem estar definidas.")
    sys.exit(1)

RELATIVE_PATH = INPUT_FILE.relative_to(GMD_TXT_PTBR_DIR)
TARGET_DIR = ARC_EXTRACTED_DIR / RELATIVE_PATH.parent
TARGET_DIR.mkdir(parents=True, exist_ok=True)

HEADER_FILE = GMD_TXT_DIR / RELATIVE_PATH.with_suffix(".header")
OUTPUT_GMD = TARGET_DIR / f"{BASE_NAME}.gmd"

if not HEADER_FILE.exists():
    print(f"[ERRO] Arquivo de header não encontrado: {HEADER_FILE}")
    sys.exit(1)

# Leitura do header
with open(HEADER_FILE, "rb") as f:
    header_bytes = f.read()

# Leitura do texto
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.rstrip("\r\n") for line in f if line.strip()]

# Validação de linhas longas
offending = [i + 1 for i, line in enumerate(lines)
             if line.strip() != "--- BLOCK ---" and len(line.strip()) > 100]

if offending:
    print("\n[ERRO] As seguintes linhas ultrapassam 100 caracteres:")
    for line in offending:
        print(f" - Linha {line}")
    sys.exit(1)

# Construção dos bytes de texto
text_bytes = bytearray()

for i, line in enumerate(lines):
    if line.strip() == "--- BLOCK ---":
        text_bytes.append(0x00)
    else:
        utf8_line = line.encode("utf-8")
        text_bytes.extend(utf8_line)
        if i + 1 < len(lines) and lines[i + 1].strip() != "--- BLOCK ---":
            text_bytes.extend(b"\x0D\x0A")  # quebra de linha

# Combinação final
final_bytes = header_bytes + text_bytes

# Escrita do .gmd final
with open(OUTPUT_GMD, "wb") as f:
    f.write(final_bytes)

print(f"\n✅ GMD recomposto com sucesso:")
print(f" - {OUTPUT_GMD}")
