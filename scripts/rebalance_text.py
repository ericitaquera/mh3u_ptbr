import sys
from pathlib import Path
import textwrap
from itertools import combinations
from statistics import stdev
import re

# Attempts to split a list of lines into N balanced lines by minimizing length difference
# Uses brute-force partitioning of word positions
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

# Reads the input file and rebalances blocks of text separated by --- BLOCK ---
def process_file(input_path):
    lines = Path(input_path).read_text(encoding='utf-8').splitlines()

    result = []
    current_block = []

    tag_pattern = re.compile(r'^\s*<[^<>]+>\s*$')

    for line in lines:
        if line.strip() == "--- BLOCK ---":
            if current_block:
                tag_lines = []
                text_lines = []
                line_roles = []  # Track original order ("tag" or "text")

                for bl_line in current_block:
                    if tag_pattern.fullmatch(bl_line):
                        tag_lines.append(bl_line)
                        line_roles.append("tag")
                    else:
                        text_lines.append(bl_line)
                        line_roles.append("text")

                if len(text_lines) > 1:
                    balanced = partition_text_lines(text_lines)
                else:
                    balanced = text_lines

                # Rebuild the block preserving original line positions
                rebuilt_block = []
                tag_idx = 0
                text_idx = 0
                for role in line_roles:
                    if role == "tag":
                        rebuilt_block.append(tag_lines[tag_idx])
                        tag_idx += 1
                    else:
                        rebuilt_block.append(balanced[text_idx])
                        text_idx += 1

                result.extend(rebuilt_block)

            result.append("--- BLOCK ---")
            current_block = []
        else:
            current_block.append(line)

    # Final block
    if current_block:
        tag_lines = []
        text_lines = []
        line_roles = []

        for bl_line in current_block:
            if tag_pattern.fullmatch(bl_line):
                tag_lines.append(bl_line)
                line_roles.append("tag")
            else:
                text_lines.append(bl_line)
                line_roles.append("text")

        if len(text_lines) > 1:
            balanced = partition_text_lines(text_lines)
        else:
            balanced = text_lines

        rebuilt_block = []
        tag_idx = 0
        text_idx = 0
        for role in line_roles:
            if role == "tag":
                rebuilt_block.append(tag_lines[tag_idx])
                tag_idx += 1
            else:
                rebuilt_block.append(balanced[text_idx])
                text_idx += 1

        result.extend(rebuilt_block)

    return result

# Main script entry point
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rebalance_blocks.py <input_file.txt>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = input_path.with_name(input_path.stem + "_balanced.txt")

    output_lines = process_file(input_path)
    output_path.write_text('\n'.join(output_lines) + '\n', encoding='utf-8')

    print(f"File saved as: {output_path}")