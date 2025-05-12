import argparse
import os
from pathlib import Path

# Argumentos
parser = argparse.ArgumentParser(description="Extrai .gmd em .txt e .header")
parser.add_argument("SourceFile", help="Caminho para o arquivo .gmd")
parser.add_argument("--execute", action="store_true", help="Escreve os arquivos. Sem isso, é dry-run.")
args = parser.parse_args()

SOURCE_FILE = Path(args.SourceFile)
ARC_EXTRACTED_DIR = Path(os.environ.get("ARC_EXTRACTED_DIR", ""))
GMD_TXT_DIR = Path(os.environ.get("GMD_TXT_DIR", ""))

if not ARC_EXTRACTED_DIR or not GMD_TXT_DIR:
    print("Variáveis de ambiente ARC_EXTRACTED_DIR e GMD_TXT_DIR não definidas.")
    exit(1)

# Caminhos
rel_path = SOURCE_FILE.relative_to(ARC_EXTRACTED_DIR)
base_name = SOURCE_FILE.stem
target_dir = GMD_TXT_DIR / rel_path.parent
target_dir.mkdir(parents=True, exist_ok=True)

output_text = target_dir / f"{base_name}.txt"
output_header = target_dir / f"{base_name}.header"

# Leitura de bytes
with open(SOURCE_FILE, "rb") as f:
    data = f.read()

# Encontra último 0x12
last_0x12 = data.rfind(b'\x12')
if last_0x12 == -1:
    header = b""
    text_data = data
    print("[WARN] Nenhum byte 0x12 encontrado. Nenhum cabeçalho extraído.")
else:
    header = data[:last_0x12 + 1]
    text_data = data[last_0x12 + 1:]

# Simulação (dry-run)
if not args.execute:
    print(f"[Dry Run] Arquivo: {SOURCE_FILE}")
    print(f" - Header: {output_header}")
    print(f" - Texto:  {output_text}")
    exit(0)

# Confirmação de sobrescrita
for path in (output_text, output_header):
    if path.exists():
        response = input(f"[AVISO] O arquivo '{path}' já existe. Deseja sobrescrevê-lo? (s/N): ").strip().lower()
        if response != 's':
            print("Operação cancelada pelo usuário.")
            exit(0)

# Salva header
with open(output_header, "wb") as f:
    f.write(header)

# Extrai blocos de texto
lines = []
block = bytearray()
i = 0
while i < len(text_data):
    byte = text_data[i]
    if byte == 0x00:
        if block:
            lines.append(block.decode("utf-8", errors="replace"))
            block.clear()
        lines.append("--- BLOCK ---")
        i += 1
    elif byte == 0x0D and (i + 1 < len(text_data) and text_data[i + 1] == 0x0A):
        if block:
            lines.append(block.decode("utf-8", errors="replace"))
            block.clear()
        i += 2
    else:
        block.append(byte)
        i += 1

# Adiciona bloco restante
if block:
    lines.append(block.decode("utf-8", errors="replace"))

# Salva .txt
with open(output_text, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("\n[OK] Extração concluída:")
print(f" - Texto:  {output_text}")
print(f" - Header: {output_header}")
