"""Iterate on the airport extraction regex for Q4 - v4: anchored capitalized phrase."""
import csv
import io
import re
import sys
import collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = r'd:\CodingProjects\cse-6242-oan\hw\Q4\incidents.csv'
with open(path, encoding='utf-8') as f:
    rows = list(csv.reader(f))
hdr = rows[0]
ci = {h: i for i, h in enumerate(hdr)}
data = [r for r in rows[1:] if r[ci['Common Name']].strip() and 'Airport' in r[ci['Subject']]]
subs = [r[ci['Subject']] for r in data]
print('rows to extract from:', len(subs))

CAP = r"[A-Z\u00C0-\u00DE]"
LETTER = r"[A-Za-z0-9\u00C0-\u024F'\u2019.\-/]"
TOKEN = CAP + LETTER + "*"
CONNECTIVE = r"(?:al|da|de|del|di|do|dos|du|el|la|las|le|les|lo|los)"
# first token must not be a capitalized English preposition/article
FIRST = r"(?!(?:At|In|On|To|By|From|Via|Near|The|And|Of|En|Between)\b)" + TOKEN
PHRASE = (r"(?:" + FIRST + r")"
          r"(?:\s+(?:" + TOKEN + r"|" + CONNECTIVE + r"))*"
          r"\s+Airport")
RE4 = re.compile(r"\b" + PHRASE + r"\b")

fails, names, examples = [], collections.Counter(), collections.defaultdict(list)
for s in subs:
    m = RE4.search(s)
    if not m:
        fails.append(s)
    else:
        names[m.group(0)] += 1
        examples[m.group(0)].append(s)

print('regex4: matched', len(subs) - len(fails), 'of', len(subs), '| failures:', len(fails))
for s in fails:
    print('  FAIL:', s[:170])

print()
print('distinct airport names:', len(names))
# flag suspicious extractions (contain non-name-like words)
SUSPICIOUS = re.compile(
    r"(?i)\b(seized|seizure|customs|parcel|luggage|suitcase|found|arrested|discovered|"
    r"suspect|national|passenger|flight|cargo|kg|grams|ivory|birds|reptiles|tortoises|"
    r"turtles|scales|horn|horns|skins|skin|teeth|claws|live|dead|parts|products|plants|"
    r"travellers|transfer|possession|route|smuggl|export|import|convicted|charged|"
    r"man|woman|men|women|cub|cubs|package|bag|bags|check|detected|detainee)\b")
print('--- suspicious names (contain commodity/action words) ---')
for n in sorted(names):
    if SUSPICIOUS.search(n):
        print(f'  {names[n]:4d}  {n}   e.g. {examples[n][0][:120]}')
print('--- all distinct names (sorted) ---')
for n in sorted(names):
    print(f'  {names[n]:4d}  {n}')
