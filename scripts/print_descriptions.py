import os
import re

def extract_description_4_from_dir(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, encoding="utf-8") as file:
                content = file.read()

            match = re.search(r"^DESCRIPTIONS_4=(.*)", content, re.MULTILINE)
            if match:
                print(f"{filename}: {match.group(1)}")
            else:
                print(f"{filename}: DESCRIPTIONS_4 not found")

# Example usage:
extract_description_4_from_dir("C:\\tmp\\mh3u_ptbr\\qtds_texts\\arc\\quest\\us\\quest00.arc\\quest\\us\\")
