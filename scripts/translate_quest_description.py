import re
import sys
import openai  # Requires `pip install openai`
import os
from pathlib import Path
import re

# Optional: load your API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Environment variable OPENAI_API_KEY not found.")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_description(text):
    pattern = re.compile(
        r'(DESCRIPTIONS_4=)((?:[^\n]+\n)+)',  # lines until a blank line
        re.DOTALL
    )
    match = pattern.search(text)
    if match:
        return match.group(2).strip()
    return None


def translate_with_gpt(original_text):
    prompt = (
        "Você é um localizador de jogos profissionais.\n"
        "Traduza o texto abaixo do espanhol para o português do Brasil.\n"
        "Mantenha a quantidade de linhas e o tom original (dramático, engraçado, heroico etc).\n"
        "Leve em conta que o texto é descrição de Missões do jogo Monster Hunter 3 Ultimate.\n"
        "Traduzir 'Llano' como 'Planície'\n"
        "Traduzir 'Cumbres borrascosas' como 'Cumes nebulosos'\n"
        "Traduzir 'Estamos todos' para 'Todos aqui'\n"
        "Traduzir 'Ticket zarpa' para 'Ticket garra'\n"
        "Texto:\n"
        f"{original_text}\n\n"
        "Tradução:\n"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()

def update_description(file_path, new_description):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match DESCRIPTIONS_4= followed by one or more non-empty lines, until a blank line
    pattern = re.compile(
        r'(DESCRIPTIONS_4=)((?:[^\n]+\n)+)',  # Match until next blank line
        re.DOTALL
    )
    replacement = rf"\1{new_description.strip()}\n"
    new_content = pattern.sub(replacement, content, count=1)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ DESCRIPTION_4 updated successfully.")

def main(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_block = extract_description(content)
    if not original_block:
        print("❌ DESCRIPTIONS_4 not found.")
        return

    print("🔄 Translating DESCRIPTIONS_4...")
    translated = translate_with_gpt(original_block)
    update_description(input_path, translated)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translate_quest_description.py <input_file>")
        sys.exit(1)

    main(sys.argv[1])

