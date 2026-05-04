import re

with open("data/sist_info.txt", "r", encoding="utf-8") as f:
    text = f.read()

# remove too many spaces/new lines
lines = text.splitlines()

clean_lines = []
seen = set()

for line in lines:
    line = line.strip()

    # skip empty lines
    if not line:
        continue

    # skip very short useless lines
    if len(line) < 4:
        continue

    # skip duplicates
    if line.lower() in seen:
        continue

    seen.add(line.lower())
    clean_lines.append(line)

clean_text = "\n".join(clean_lines)

with open("data/sist_info_clean.txt", "w", encoding="utf-8") as f:
    f.write(clean_text)

print("Cleaning complete!")
print(f"Original lines: {len(lines)}")
print(f"Clean lines: {len(clean_lines)}")