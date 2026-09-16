"""Ground-truth verification for Q2 part 8.c using pure Python text processing."""
import csv
import re

path = r"d:\CodingProjects\cse-6242-oan\hw\Q2\data\details.csv"
# unicode61 tokenizer: split on non-alphanumeric characters, case-fold
count = 0
matched = []
with open(path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tokens = [t.lower() for t in re.split(r'[^0-9A-Za-z]+', row['subject']) if t]
        pos_dead = [i for i, t in enumerate(tokens) if t == 'dead']
        pos_pan = [i for i, t in enumerate(tokens) if t == 'pangolin']
        ok = False
        for i in pos_dead:
            for j in pos_pan:
                # number of tokens strictly between the two words
                if abs(j - i) - 1 <= 2:
                    ok = True
        if ok:
            count += 1
            matched.append(row['subject'][:90])

print("Ground truth count (<=2 intervening tokens, either order, whole words):", count)
for m in matched[:15]:
    print("  -", m)
