# Text Translator 1.0
# Clean, fixed version following the corrected principles

import subprocess
import sys
import os
import argparse
import openai
import re
from datetime import datetime

"""
Kraken v5.3b - Translation Batch Processor with Placeholder Preservation and argparse CLI

Usage:
    python text_translator.py.py input_file.txt
    python text_translator.py.py input_file.txt --starting_block=25
    python text_translator.py.py input_file.txt --blocks_per_batch=10
    python text_translator.py.py input_file.txt --starting_block=5 --blocks_per_batch=3

Optional environment variable:
    BLOCKS_PER_BATCH     (overridden if --blocks_per_batch is provided)

Description:
    - Automatically resumes from last translated block if --starting_block not specified
    - Preserves <SUBS X> placeholder lines even when embedded within translatable blocks
    - Logs all debug-level operations to the log file
    - Uses OpenAI API to translate text in batches
"""

# ========== CONFIGURATION ==========
OUTPUT_FOLDER = os.getenv("GMD_TXT_PTBR_DIR")
if not OUTPUT_FOLDER:
    raise ValueError("Environment variable GMD_TXT_PTBR_DIR not found.")

txt_base = os.getenv("GMD_TXT_DIR")
if not txt_base:
    raise ValueError("Environment variable GMD_TXT_DIR not found.")

BLOCKS_PER_BATCH = 20
TAG_PATTERN = re.compile(r"<(SUBS|COLO)\s+\d+>")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.7


# ====================================

def is_uppercase_identifier(block_lines):
    return len(block_lines) == 1 and block_lines[0].isupper()

def is_placeholder_or_symbolic(text):
    text = text.strip()
    return bool(re.fullmatch(r'(\<.*?\>|\(!\))', text))

def log_output_stdout(message, mode, log_f=None):
    """
    mode:
        0 = no output
        1 = stdout only
        2 = log only (requires log_f)
        3 = both
    """
    timestamped = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    if mode == 1:
        print(timestamped)
    elif mode == 2 and log_f:
        log_f.write(timestamped + "\n")
        log_f.flush()
    elif mode == 3 and log_f:
        print(timestamped)
        log_f.write(timestamped + "\n")
        log_f.flush()

def translate_batch(batch_text, log_f):
    full_prompt = f"""{PROMPT_STYLE}

        ---
        FORMAT ENFORCEMENT (DO NOT IGNORE):

        - DO NOT repeat or echo the original text.
        - Only output translations, using strictly the "TEXT X: translated text" format.
        - No extra commentary, no mention of the original language.
        - Example of correct answer: TEXT 1: My translated text here.
        - Translate texts to Brazilian Portuguese

        Traduzir "Aldeia de" sempre para "Vila"
        Traduzir "Bosque de" sempra para "Floresta"
        Traduzir "Granja" sempra para "Fazenda"
        Traduzir "Hoja" sempra para "Lãmina"

        ---
        TEXTS TO TRANSLATE:
        {batch_text}
    """
    
    log_output_stdout("[INFO] Sending batch to OpenAI...", 3, log_f)    
    log_output_stdout(f"[INFO] Full Prompt:{full_prompt}", 2, log_f)
    log_output_stdout("[INFO] Text being sent to GPT for translation:", 2, log_f)
    cleaned_batch_text = "\n".join([line for line in batch_text.splitlines() if line.strip()])
    log_output_stdout(cleaned_batch_text, 2, log_f)


    response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional game translator."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=OPENAI_TEMPERATURE
            )
    
    result =  response.choices[0].message.content.strip()
    log_output_stdout("[INFO] Raw GPT response received.", 3, log_f)
    cleaned_batch_text = "\n".join([line for line in result.splitlines() if line.strip()])
    log_output_stdout(cleaned_batch_text, 2, log_f)
    
    # Split back out into individual responses
    splits = re.split(r'TEXT(?:O)? \d+:', result)[1:]
    return [s.strip() for s in splits]

def process_batch_output(batch, out_f, log_f):
    # Step 1: Extract and index text blocks
    text_contents = [content for kind, content, _, _ in batch if kind == "text"]
    text_indices  = [i for i, (kind, _, _, _) in enumerate(batch) if kind == "text"]

    if text_contents:
        batch_text = "\n\n".join([f"TEXT {i+1}: {t}" for i, t in enumerate(text_contents)])
        translated_texts = translate_batch(batch_text, log_f)

        if len(translated_texts) != len(text_contents):
            log_output_stdout(f"Enviados: {len(text_contents)}", 3, log_f)
            log_output_stdout(f"Recebidos: {len(translated_texts)}", 3, log_f)
            log_output_stdout("[ERROR] GPT response count mismatch.", 3, log_f)
            return

        for i, idx in enumerate(text_indices):
            kind, _, lines, block_no = batch[idx]
            batch[idx] = (kind, translated_texts[i], lines, block_no)

    # Step 2: Write all blocks in original order
    for index, (kind, content, lines, block_number) in enumerate(batch):
        if kind in ["text", "tagged_text"]:
            balanced_lines = rebalance_lines(content, lines)
            content = "\n".join(balanced_lines)

        out_f.write(content + "\n")
        out_f.write("--- BLOCK ---\n")
        log_output_stdout(f"[SUCCESS] Block {block_number} ({kind}) written to output.", 2, log_f)

        if index == len(batch) - 1:
            log_output_stdout(f"[SUCCESS] Last block processed: {block_number} - ({kind}).", 3, log_f)

def rebalance_lines(text, num_lines):
    words = text.split()
    if num_lines <= 1 or len(words) <= num_lines:
        return [text]

    avg = len(words) // num_lines
    remainder = len(words) % num_lines

    result = []
    index = 0
    for i in range(num_lines):
        count = avg + (1 if i < remainder else 0)
        line = " ".join(words[index:index+count])
        result.append(line)
        index += count

    return result

def detect_last_translated_block(output_path):
    """Detects how many blocks have already been translated in output."""
    if not os.path.exists(output_path):
        return 0

    count = 0
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "--- BLOCK ---":
                count += 1
    return count

# ========== PARSE ARGUMENTS ==========
parser = argparse.ArgumentParser(description="Kraken Translation Batch Runner")
parser.add_argument("--SourceFile", dest="SourceFile", required=True, help="Path to input text file")
parser.add_argument("--starting_block", type=int, default=None, help="Block number to start from")
parser.add_argument("--blocks_per_batch", type=int, default=None, help="Blocks per batch")
parser.add_argument("--total_blocks", type=int, default=None, help="Total blocks to process")
args = parser.parse_args()

input_file = args.SourceFile
base_name = os.path.basename(input_file)
name_without_ext = os.path.splitext(base_name)[0]

relative_path = os.path.relpath(os.path.abspath(input_file), start=os.path.abspath(txt_base))
if relative_path.startswith("rc" + os.sep):
    relative_path = "arc" + relative_path[2:]
relative_dir = os.path.dirname(relative_path)
output_dir = os.path.join(OUTPUT_FOLDER, relative_dir)

os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"{name_without_ext}.txt")
log_file = os.path.join(output_dir, f"{name_without_ext}.log")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

BLOCKS_PER_BATCH = args.blocks_per_batch if args.blocks_per_batch else BLOCKS_PER_BATCH

if args.starting_block:
    start_block = args.starting_block
else:
    last_block = detect_last_translated_block(output_file)
    start_block = last_block + 1
    if os.path.exists(output_file):
        total_blocks_in_input = sum(1 for line in open(input_file, encoding="utf-8") if line.strip() == "--- BLOCK ---")
        if last_block >= total_blocks_in_input:
            print(f"[INFO] Translation already complete ({last_block} blocks). Nothing to do.")
            sys.exit(0)
    if last_block > 0:
        print(f"[INFO] Detected {last_block} blocks already translated. Resuming from block {start_block}.")


end_block = start_block + args.total_blocks - 1 if args.total_blocks is not None else float('inf')

# Load environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Environment variable OPENAI_API_KEY not found.")

prompt_dir = os.getenv("PROMPTS_GPT")
if not prompt_dir:
    raise ValueError("Environment variable PROMPTS_GPT not found.")

prompt_path = os.path.join(prompt_dir, f"{name_without_ext}.prompt.txt")
if not os.path.exists(prompt_path):
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    sys.exit()

with open(prompt_path, "r", encoding="utf-8") as pf:
    PROMPT_STYLE = pf.read().strip()
    print(f"[INFO] Using prompt loaded from: {prompt_path}")


client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========== LOAD INPUT ===========
with open(input_file, "r", encoding="utf-8-sig") as f:
    lines = [line.rstrip('\n') for line in f]

# ========== MAIN EXECUTION ===========
def process_blocks(lines, out_f, log_f):
    batch = []
    current_block = []
    block_number = 0

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        log_output_stdout(f"[TRACE] At line {idx}, block_number={block_number}, start_block={start_block}, end_block={end_block}", 0, log_f)

        if stripped == "--- BLOCK ---":
            if current_block:
                block_number += 1

                if block_number < start_block:
                    log_output_stdout(f"[DEBUG] Block #{block_number} SKIPPED: Less than defined start_block={start_block}.", 2, log_f)
                    current_block = []
                    continue

                if block_number > end_block:
                    log_output_stdout(f"[INFO] Reached end_block {end_block}. Stopping main loop.", 3, log_f)
                    break

                log_output_stdout(f"[DEBUG] Block {block_number} will be considered: {current_block}", 2, log_f)

                combined_text = " ".join(current_block)
                if is_uppercase_identifier(current_block) or is_placeholder_or_symbolic(combined_text):
                    # identifier or symbolic - no translation needed
                    log_output_stdout(f"[DEBUG] Testing classification for block {block_number}: {combined_text}. Classification: identifier", 2, log_f)
                    batch.append(("identifier", combined_text, len(current_block), block_number))
                    #out_f.write(combined_text + "\n")
                    #out_f.write("--- BLOCK ---\n")
                    #out_f.flush()

                    #log_output_stdout(f"File: {base_name} - BLOCK {block_number} (identifier) SAVED", 3, log_f)
                    log_output_stdout(f"[SUCCESS] Block {block_number} (identifier) added to queue.", 2, log_f)
                elif TAG_PATTERN.search(combined_text):
                    log_output_stdout(f"[DEBUG] Testing classification for block {block_number}: {combined_text}. Classification: tagged_text", 2, log_f)

                    # Split into text + tags
                    pattern = re.compile(r"(<[^>]+>)")
                    parts = [p for p in pattern.split(combined_text) if p != '']

                    segments = []
                    tag_map = []

                    for i, part in enumerate(parts):
                        if pattern.fullmatch(part):
                            tag_map.append((len(segments), part))
                        elif part.strip():
                            segments.append(part.strip())

                    if segments:
                        # Prepare prompt and translate segments now
                        batch_text = "\n\n".join([f"TEXT {i+1}: {s}" for i, s in enumerate(segments)])
                        translated_segments = translate_batch(batch_text, log_f)
                        #print(f"segments: {segments}")
                        #print(f"tag_map: {tag_map}")
                        #print(f"batch_text: {batch_text}")                        
                        #print(f"translated_segments: {translated_segments}")

                        if len(translated_segments) != len(segments):
                            log_output_stdout(f"[ERROR] GPT returned {len(translated_segments)} segments, expected {len(segments)}. Block {block_number} skipped.", 3, log_f)
                            translated_result = combined_text + " [UNTRANSLATED]"
                        else:
                            # Merge back in original tag positions
                            for idx, tag in reversed(tag_map):
                                translated_segments.insert(idx, f" {tag}")
                            translated_result = "".join(translated_segments)
                    else:
                        translated_result = combined_text  # fallback, no segments to translate

                    batch.append(("tagged_text", translated_result, len(current_block), block_number))
                    #log_output_stdout(f"File: {base_name} - BLOCK {block_number} (tagged_text) SAVED", 3, log_f)
                    log_output_stdout(f"[SUCCESS] Block {block_number} (tagged_text) added to queue.", 2, log_f)
                else:
                    log_output_stdout(f"[DEBUG] Testing classification for block {block_number}: {combined_text}. Classification: text", 2, log_f)
                    batch.append(("text", combined_text, len(current_block), block_number))
                    log_output_stdout(f"[SUCCESS] Block {block_number} (text) added to queue.", 2, log_f)
                    # here, you would collect for translation
                    #out_f.write(combined_text + " [text]\n")
                    #out_f.write("--- BLOCK ---\n")
                    
                current_block = []

        else:
            current_block.append(stripped)
            
    return block_number, batch

with open(output_file, "a", encoding="utf-8") as out_f, open(log_file, "w", encoding="utf-8") as log_f:  # write mode, truncates log each run
    log_output_stdout(f"- Starting execution", 3, log_f)
    log_output_stdout(f"[INFO] Will process from block {start_block} to {end_block if end_block != float('inf') else 'EOF'}", 3, log_f)
    processed, batch = process_blocks(lines, out_f, log_f)
    process_batch_output(batch, out_f, log_f)
    log_output_stdout(f"[SUCCESS] Translation completed! Processed {processed} block(s). Output file saved at: {output_file}", 3, log_f)

# Check for lines longer than 43 characters
    with open(output_file, "r", encoding="utf-8") as out_check:
        long_lines = [(i+1, line.strip()) for i, line in enumerate(out_check) if len(line.strip()) > 43 and line.strip() != '--- BLOCK ---']
    if long_lines:
        log_output_stdout("[WARNING] The following lines exceed 43 characters:", 3, log_f)
        for lineno, content in long_lines:
            log_output_stdout(f"Line {lineno}: {content}", 3, log_f)
    else:
        log_output_stdout("[INFO] No lines exceed 43 characters:", 3, log_f)
    log_output_stdout(f"[INFO] Input File: {input_file}", 3, log_f) 
    log_output_stdout(f"[INFO] Log file saved at: {log_file}", 3, log_f) 
    print(f".\\find_lines.ps1 {input_file} {output_file}")
