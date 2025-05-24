from itertools import combinations
import re
import sys

def partition_text_lines(text_lines):
    words = ' '.join(line.strip() for line in text_lines).split()
    num_lines = len(text_lines)

    if num_lines <= 1 or len(words) <= 1:
        return [' '.join(words)]

    break_positions = combinations(range(1, len(words)), num_lines - 1)

    best_partition = None
    best_score = float('inf')

    for breaks in break_positions:
        parts = []
        last = 0
        for b in breaks:
            parts.append(words[last:b])
            last = b
        parts.append(words[last:])

        line_lengths = [sum(len(w) for w in part) + (len(part) - 1) for part in parts]
        score = max(line_lengths) - min(line_lengths)

        if score < best_score:
            best_score = score
            best_partition = parts

    return [' '.join(part) for part in best_partition]

def extract_description_block(text):
    pattern = re.compile(r'(DESCRIPTIONS_4=)((?:[^\n]+\n)+)', re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(2).strip().splitlines()
    return None

def rebalance_description(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = extract_description_block(content)
    if not lines:
        print("❌ DESCRIPTIONS_4 block not found.")
        return

    normalized = partition_text_lines(lines)
    new_description = '\n'.join(normalized)

    pattern = re.compile(r'(DESCRIPTIONS_4=)((?:[^\n]+\n)+)', re.DOTALL)
    replacement = rf"\1{new_description}\n"
    new_content = pattern.sub(replacement, content, count=1)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ DESCRIPTIONS_4 block rebalanced.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rebalance_description.py <file_path>")
        sys.exit(1)

    rebalance_description(sys.argv[1])