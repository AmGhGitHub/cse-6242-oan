"""Drive OpenRefine 3.6.2 — selective clustering (fingerprint + manual fixes)."""
import csv, io, json, os, re, sys, time
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = "http://127.0.0.1:3333"
CSV_PATH = r"d:\CodingProjects\cse-6242-oan\hw\Q4\incidents.csv"
OUT_CSV = r"d:\CodingProjects\cse-6242-oan\hw\Q4\Q4.csv"
OUT_HIST = r"d:\CodingProjects\cse-6242-oan\hw\Q4\history.json"
EMPTY_ENGINE = {"facets": [], "mode": "row-based"}

# ── cleanup ──────────────────────────────────────────────────────────────
csrf = requests.get(f"{BASE}/command/core/get-csrf-token").json()["token"]
meta = requests.get(f"{BASE}/command/core/get-all-project-metadata").json()
for pid in list(meta.get("projects", {}).keys()):
    requests.post(f"{BASE}/command/core/delete-project",
                  data={"project": pid}, params={"csrf_token": csrf})
csrf = requests.get(f"{BASE}/command/core/get-csrf-token").json()["token"]

# ── create project ───────────────────────────────────────────────────────
print("Creating project...")
with open(CSV_PATH, "rb") as f:
    resp = requests.post(
        f"{BASE}/command/core/create-project-from-upload",
        files={"file": ("incidents.csv", f, "text/csv")},
        data={"options": json.dumps({
            "project-name": "incidents", "separator": ",", "ignoreLines": -1,
            "headerLines": 1, "skipDataLines": 0, "limit": -1,
            "storeBlankRows": True, "guessCellValueTypes": False,
            "processQuotes": True, "quoteCharacter": '"',
            "storeBlankCellsAsNulls": True, "includeFileSources": False,
            "fileSource": "incidents.csv", "encoding": "UTF-8", "columnNames": [],
        })},
        params={"csrf_token": csrf},
    )
project_id = None
if resp.history:
    for r in resp.history:
        m = re.search(r"project=(\d+)", r.headers.get("Location", ""))
        if m: project_id = m.group(1)
if not project_id:
    m = re.search(r"project=(\d+)", resp.url)
    if m: project_id = m.group(1)
if not project_id:
    time.sleep(1)
    meta = requests.get(f"{BASE}/command/core/get-all-project-metadata").json()
    projs = meta.get("projects", {})
    if projs: project_id = list(projs.keys())[0]
print(f"Project: {project_id}")
time.sleep(1)

def apply_op(op, desc=""):
    r = requests.post(f"{BASE}/command/core/apply-operations",
        data={"project": project_id, "operations": json.dumps([op])},
        params={"csrf_token": csrf})
    result = r.json()
    hid = result.get("historyEntry", {}).get("id", "N/A")
    print(f"  {desc}: code={result.get('code','?')} hid={hid}")
    return result

def row_count():
    r = requests.get(f"{BASE}/command/core/get-rows",
        params={"project": project_id, "start": 0, "limit": 1}).json()
    return r.get("filtered", 0)

# ── Op 1: Remove blank Common Name ──────────────────────────────────────
print("\n1. Remove blank Common Name rows...")
apply_op({
    "op": "core/row-removal",
    "description": "Remove rows",
    "engineConfig": {
        "facets": [{
            "type": "list", "name": "Common Name", "columnName": "Common Name",
            "expression": "isBlank(value)", "selectBlank": False,
            "selectError": False, "invert": False,
            "selection": [{"v": {"v": True, "l": "true"}}]
        }],
        "mode": "row-based"
    }
}, "Remove blank CN")
print(f"  Rows: {row_count()}")

# ── Op 2: Keep only Airport rows ────────────────────────────────────────
print("2. Keep only Airport rows...")
apply_op({
    "op": "core/row-removal",
    "description": "Remove rows",
    "engineConfig": {
        "facets": [{
            "type": "text", "name": "Subject", "columnName": "Subject",
            "mode": "text", "caseSensitive": True, "query": "Airport", "invert": True
        }],
        "mode": "row-based"
    }
}, "Keep Airport rows")
print(f"  Rows: {row_count()}")

# ── Op 3: Add Airport column ────────────────────────────────────────────
print("3. Add Airport column...")
regex_str = (
    r"\b(?!(?:At|In|On|To|By|From|Via|Near|The|And|Of|En|Between)\b)"
    r"[A-Z\u00C0-\u00DE]"
    r"[A-Za-z0-9\u00C0-\u024F'\u2019.-]*"
    r"(?:\s+(?:[A-Z\u00C0-\u00DE][A-Za-z0-9\u00C0-\u024F'\u2019.-]*"
    r"|(?:al|da|de|del|di|do|dos|du|el|la|las|le|les|lo|los)))*"
    r"\s+Airport\b"
)
grel_expr = "grel:value.find(/" + regex_str + "/)[0]"

apply_op({
    "op": "core/column-addition",
    "description": "Create column Airport at index 5 based on column Subject using expression " + grel_expr,
    "newColumnName": "Airport",
    "columnInsertIndex": 5,
    "baseColumnName": "Subject",
    "expression": grel_expr,
    "onError": "set-to-blank",
    "engineConfig": EMPTY_ENGINE
}, "Add Airport column")

time.sleep(2)
cols = requests.get(f"{BASE}/command/core/get-columns-info",
                    params={"project": project_id}).json()
col_names = [c["name"] for c in cols]
print(f"  Columns: {col_names}")

if "Airport" not in col_names:
    print("ERROR: Airport column not created!")
    sys.exit(1)

# Verify
csv_text = requests.post(f"{BASE}/command/core/export-rows/{project_id}.csv",
    data={"project": project_id, "format": "csv", "options": json.dumps({})},
    params={"csrf_token": csrf}).text
reader = csv.reader(io.StringIO(csv_text))
hdr = next(reader)
ai = hdr.index("Airport")
total = blanks = 0
names = {}
for row in reader:
    total += 1
    val = row[ai] if ai < len(row) else ""
    if not val.strip(): blanks += 1
    else: names[val] = names.get(val, 0) + 1
print(f"  Rows: {total}, Blanks: {blanks}, Distinct: {len(names)}")

# ── Op 4: Cluster merges — only fingerprint (safe) ──────────────────────
print("\n4. Cluster with fingerprint...")
clusterer = {"type": "binning", "function": "fingerprint", "column": "Airport", "params": {}}
r = requests.post(f"{BASE}/command/core/compute-clusters",
    data={"project": project_id, "clusterer": json.dumps(clusterer)},
    params={"csrf_token": csrf})
fp_clusters = r.json()
print(f"  {len(fp_clusters)} clusters")

fp_merges = []
for cl in fp_clusters:
    if len(cl) < 2: continue
    variants = [item["v"] for item in cl]
    counts = [item["c"] for item in cl]
    best = max(range(len(counts)), key=lambda i: counts[i])
    target = variants[best]
    edits = sorted(set(v for v in variants if v != target))
    if edits:
        fp_merges.append({"from": edits, "to": target, "type": "text"})
        print(f"    {edits} -> '{target}' ({counts[best]} rows)")

if fp_merges:
    apply_op({
        "op": "core/mass-edit",
        "description": "Mass edit cells in column Airport",
        "engineConfig": EMPTY_ENGINE,
        "columnName": "Airport",
        "expression": "value",
        "edits": fp_merges,
    }, "Fingerprint merges")

# ── Op 5: Manual typo fixes ─────────────────────────────────────────────
# Known typos and variants from analysis (not caught by fingerprint)
manual_merges = [
    # Typos
    {"from": ["Gunagzhou Baiyun Airport"], "to": "Guangzhou Baiyun Airport", "type": "text"},
    {"from": ["Beijing Captial Airport"], "to": "Beijing Capital Airport", "type": "text"},
    {"from": ["Tan Son Nha International Airport", "Than Son Nhat Airport"], "to": "Tan Son Nhat International Airport", "type": "text"},
    {"from": ["Maputo Interantional Airport"], "to": "Maputo International Airport", "type": "text"},
    {"from": ["Xiamen Gaogi Airport"], "to": "Xiamen Gaoqi International Airport", "type": "text"},
    {"from": ["Shenyang Taoxin International Airport"], "to": "Shenyang Taoxian International Airport", "type": "text"},
    {"from": ["Bangkok Suvarnbhumi Airport"], "to": "Bangkok Suvarnabhumi Airport", "type": "text"},
    {"from": ["Berlin Schonefeld Airport"], "to": "Berlin Schoenefeld Airport", "type": "text"},
    {"from": ["Bandaranayake International Airport"], "to": "Bandaranaike International Airport", "type": "text"},
    # Short vs full names (same airport)
    {"from": ["Guangzhou Airport", "Guangzhou Baiyun Airport", "Guangzhou International Airport", "Baiyun Airport", "Baiyun International Airport"], "to": "Guangzhou Baiyun International Airport", "type": "text"},
    {"from": ["Shenzhen Airport", "Shenzhen Bao'an Airport", "Shenzhen Bao\u2019an Airport", "Shenzhen Bao'an International Airport"], "to": "Shenzhen Bao'an International Airport", "type": "text"},
    {"from": ["Hong Kong Airport"], "to": "Hong Kong International Airport", "type": "text"},
    {"from": ["Shanghai Airport", "Shanghai Pudong Airport", "Pudong Airport"], "to": "Shanghai Pudong International Airport", "type": "text"},
    {"from": ["Shanghai Hongqiao Airport", "Shanghai Hongqiao International Airport"], "to": "Shanghai Hongqiao International Airport", "type": "text"},
    {"from": ["Beijing Airport", "Beijing Capital Airport", "Beijing Capital International Airport", "Capital Airport"], "to": "Beijing Capital International Airport", "type": "text"},
    {"from": ["OR Tambo Airport", "OR Tambo International Airport", "O.R Tambo International Airport", "O.R. Tambo International Airport"], "to": "O.R. Tambo International Airport", "type": "text"},
    {"from": ["Kunming Airport", "Kunming Changshui Airport", "Kunming Changshui International Airport", "Changshui Airport"], "to": "Kunming Changshui International Airport", "type": "text"},
    {"from": ["Noi Bai Airport", "Noi Bai International Airport", "Hanoi Noi Bai International Airport", "Hanoi Airport"], "to": "Noi Bai International Airport", "type": "text"},
    {"from": ["Suvarnabhumi Airport", "Suvarnabhumi International Airport", "Bangkok Suvarnabhumi Airport", "Bangkok International Suvarnabhumi Airport"], "to": "Suvarnabhumi Airport", "type": "text"},
    {"from": ["Jomo Kenyatta Airport", "Jomo Kenyatta International Airport"], "to": "Jomo Kenyatta International Airport", "type": "text"},
    {"from": ["Chhatrapati Shivaji International Airport", "Chhatrapati Shivaji Maharaj International Airport"], "to": "Chhatrapati Shivaji Maharaj International Airport", "type": "text"},
    {"from": ["Amsterdam Airport", "Amsterdam International Airport", "Amsterdam Schiphol Airport", "Amsterdam Schipol Airport", "Amsterdam-Schiphol Airport", "Amsterdam-Schiphol International Airport", "Amsterdam\u2019s Schiphol Airport"], "to": "Amsterdam Schiphol Airport", "type": "text"},
    {"from": ["Mexico City Airport", "Mexico City International Airport"], "to": "Mexico City International Airport", "type": "text"},
    {"from": ["Kuala Lumpur Airport", "Kuala Lumpur International Airport"], "to": "Kuala Lumpur International Airport", "type": "text"},
    {"from": ["Miami Airport", "Miami International Airport"], "to": "Miami International Airport", "type": "text"},
    {"from": ["Tan Son Nhat Airport", "Tan Son Nhat International Airport"], "to": "Tan Son Nhat International Airport", "type": "text"},
    {"from": ["Qingdao Airport", "Qingdao Liuting Airport", "Qingdao Liuting International Airport", "Qingdao Jiaodong International Airport", "Liuting Airport"], "to": "Qingdao Liuting International Airport", "type": "text"},
    {"from": ["Chengdu Airport", "Chengdu Shuangliu Airport", "Chengdu Shuangliu International Airport"], "to": "Chengdu Shuangliu International Airport", "type": "text"},
    {"from": ["Soekarno Hatta Airport", "Soekarno Hatta International Airport", "Soekarno-Hatta Airport", "Soekarno-Hatta International Airport"], "to": "Soekarno-Hatta International Airport", "type": "text"},
    {"from": ["Ivato Airport", "Ivato International Airport"], "to": "Ivato International Airport", "type": "text"},
    {"from": ["Ngurah Rai Airport", "Ngurah Rai International Airport"], "to": "Ngurah Rai International Airport", "type": "text"},
    {"from": ["Entebbe Airport", "Entebbe International Airport", "Kampala Airport"], "to": "Entebbe International Airport", "type": "text"},
    {"from": ["Dalian Airport", "Dalian Zhoushuizi Airport", "Dalian Zhoushuizi International Airport"], "to": "Dalian Zhoushuizi International Airport", "type": "text"},
    {"from": ["Chongqing Airport", "Chongqing Jiangbei Airport", "Chongqing Jiangbei International Airport", "Jiangbei International Airport"], "to": "Chongqing Jiangbei International Airport", "type": "text"},
    {"from": ["Nanjing Lukou Airport", "Nanjing Lukou International Airport", "Lukou Airport"], "to": "Nanjing Lukou International Airport", "type": "text"},
    {"from": ["Hangzhou Airport", "Hangzhou Xiaoshan Airport", "Hangzhou Xiaoshan International Airport", "Xiaoshan Airport"], "to": "Hangzhou Xiaoshan International Airport", "type": "text"},
    {"from": ["Jinan Airport", "Jinan Yaoqiang Airport", "Jinan Yaoqiang International Airport"], "to": "Jinan Yaoqiang International Airport", "type": "text"},
    {"from": ["Wuhan Tianhe Airport", "Wuhan Tianhe International Airport"], "to": "Wuhan Tianhe International Airport", "type": "text"},
    {"from": ["Tianjin Airport", "Tianjin Binhai Airport", "Tianjin Binhai International Airport"], "to": "Tianjin Binhai International Airport", "type": "text"},
    {"from": ["Nanning Airport", "Nanning Wuxu Airport"], "to": "Nanning Wuxu Airport", "type": "text"},
    {"from": ["Fuzhou Airport", "Fuzhou Changle Airport", "Fuzhou Changle International Airport"], "to": "Fuzhou Changle International Airport", "type": "text"},
    {"from": ["Lanzhou Airport", "Lanzhou Zhongchuan Airport", "Lanzhou Zhongchuan International Airport", "Zhongchuan Airport"], "to": "Lanzhou Zhongchuan International Airport", "type": "text"},
    {"from": ["Shenyang Taoxian Airport", "Shenyang Taoxian International Airport", "Taoxian Airport"], "to": "Shenyang Taoxian International Airport", "type": "text"},
    {"from": ["Xiamen Airport", "Xiamen Gaoqi International Airport"], "to": "Xiamen Gaoqi International Airport", "type": "text"},
    {"from": ["Zhengzhou Airport", "Zhengzhou Xinzheng Airport", "Xin Zheng International Airport"], "to": "Zhengzhou Xinzheng Airport", "type": "text"},
    {"from": ["Taiwan Taoyuan Airport", "Taiwan Taoyuan International Airport", "Taoyuan Airport", "Taoyuan International Airport", "Taipei Taoyuan Airport"], "to": "Taiwan Taoyuan International Airport", "type": "text"},
    {"from": ["Kualanamu Airport", "Kualanamu International Airport"], "to": "Kualanamu International Airport", "type": "text"},
    {"from": ["Jieyang Chaoshan Airport", "Jieyang Chaoshan International Airport", "Chaoshan Airport"], "to": "Jieyang Chaoshan International Airport", "type": "text"},
    {"from": ["Don Mueang Airport", "Don Mueang International Airport"], "to": "Don Mueang International Airport", "type": "text"},
    {"from": ["Douala Airport", "Douala International Airport"], "to": "Douala International Airport", "type": "text"},
    {"from": ["Harare Airport", "Harare International Airport", "Robert Mugabe Airport"], "to": "Harare International Airport", "type": "text"},
    {"from": ["El Dorado Airport", "El Dorado International Airport"], "to": "El Dorado International Airport", "type": "text"},
    {"from": ["Sunan Shuofang Airport", "Sunan Shuofang International Airport", "Shuofang International Airport"], "to": "Sunan Shuofang International Airport", "type": "text"},
    {"from": ["Ndjili Airport", "Ndjili International Airport"], "to": "Ndjili International Airport", "type": "text"},
    {"from": ["Maputo Airport", "Maputo International Airport"], "to": "Maputo International Airport", "type": "text"},
    {"from": ["Luanda Airport", "Luanda International Airport", "Fevereiro International Airport", "Quatro de Fevereiro International Airport"], "to": "Quatro de Fevereiro International Airport", "type": "text"},
    {"from": ["Supadio Airport", "Supadio International Airport"], "to": "Supadio International Airport", "type": "text"},
    {"from": ["Merida Airport", "Merida International Airport"], "to": "Merida International Airport", "type": "text"},
    {"from": ["Ciudad Ju\u00e1rez Airport", "Ciudad Ju\u00e1rez International Airport"], "to": "Ciudad Ju\u00e1rez International Airport", "type": "text"},
    {"from": ["Phnom Penh Airport", "Phnom Penh International Airport"], "to": "Phnom Penh International Airport", "type": "text"},
    {"from": ["Tijuana Airport", "Tijuana International Airport"], "to": "Tijuana International Airport", "type": "text"},
    {"from": ["Dusseldorf Airport", "Dusseldorf International Airport"], "to": "Dusseldorf International Airport", "type": "text"},
    {"from": ["Kamuzu Airport", "Kamuzu International Airport"], "to": "Kamuzu International Airport", "type": "text"},
    {"from": ["Murtala Mohammed Airport", "Murtala Muhammed Airport", "Murtala Muhammed International Airport"], "to": "Murtala Muhammed International Airport", "type": "text"},
    {"from": ["Mohammed V Airport", "Mohammed V International Airport"], "to": "Mohammed V International Airport", "type": "text"},
    {"from": ["Sultan Syarif Kasim II Airport", "Sultan Syarif Kasim II International Airport", "Sutan Syarif Kasim II Pekanbaru Airport"], "to": "Sultan Syarif Kasim II International Airport", "type": "text"},
    {"from": ["Sultan Hasanuddin Airport"], "to": "Sultan Hasanuddin Airport", "type": "text"},  # keep as is
    {"from": ["Julius Nyerere Airport", "Julius Nyerere International Airport"], "to": "Julius Nyerere International Airport", "type": "text"},
    {"from": ["Sao Paulo Airport", "Sao Paulo International Airport", "Guarulhos Airport"], "to": "Guarulhos Airport", "type": "text"},
    {"from": ["Manaus Airport", "Manaus International Airport"], "to": "Manaus International Airport", "type": "text"},
    {"from": ["Mangshi Airport", "Mangshi Dehong Airport", "Mangshi International Airport"], "to": "Mangshi International Airport", "type": "text"},
    {"from": ["Nanchang Airport", "Nanchang Changbei Airport", "Changbei Airport"], "to": "Nanchang Changbei Airport", "type": "text"},
    {"from": ["Mopah Airport", "Mopah Merauke Airport"], "to": "Mopah Airport", "type": "text"},
    {"from": ["Schiphol Airport"], "to": "Amsterdam Schiphol Airport", "type": "text"},
    {"from": ["Heathrow Airport"], "to": "Heathrow Airport", "type": "text"},  # keep
    {"from": ["Sanya Phoenix Airport", "Sanya Phoenix International Airport"], "to": "Sanya Phoenix International Airport", "type": "text"},
    {"from": ["San Luis Potos\u00ed Airport", "San Luis Potos\u00ed International Airport"], "to": "San Luis Potos\u00ed International Airport", "type": "text"},
    {"from": ["Tocumen Airport", "Tocumen International Airport"], "to": "Tocumen International Airport", "type": "text"},
    {"from": ["Wenzhou Airport", "Wenzhou Longwan International Airport"], "to": "Wenzhou Longwan International Airport", "type": "text"},
    {"from": ["Urumqi Airport", "Urumqi Diwopu Airport"], "to": "Urumqi Diwopu Airport", "type": "text"},
    {"from": ["Leipzig Airport", "Leipzig/Halle Airport"], "to": "Leipzig/Halle Airport", "type": "text"},
    {"from": ["Karlsruhe-Baden-Baden International Airport", "Baden-Baden Airport"], "to": "Karlsruhe-Baden-Baden International Airport", "type": "text"},
    {"from": ["Changsha Airport", "Changsha Huanghua Airport", "Changsha Huanghua International Airport"], "to": "Changsha Huanghua International Airport", "type": "text"},
    {"from": ["Melbourne Airport", "Melbourne International Airport"], "to": "Melbourne Airport", "type": "text"},
    {"from": ["Mumbai Airport"], "to": "Chhatrapati Shivaji Maharaj International Airport", "type": "text"},
    {"from": ["Kolkata Airport", "Netaji Subhas Chandra Bose Airport"], "to": "Netaji Subhas Chandra Bose Airport", "type": "text"},
    {"from": ["Singapore Airport", "Changi Airport"], "to": "Changi International Airport", "type": "text"},
    {"from": ["Chennai Airport"], "to": "Chennai International Airport", "type": "text"},
    {"from": ["Frankfurt Airport"], "to": "Frankfurt Airport", "type": "text"},
    {"from": ["Xi'an Xianyang Airport"], "to": "Xi'an Xianyang Airport", "type": "text"},
    {"from": ["Indira Gandhi International Airport"], "to": "Indira Gandhi International Airport", "type": "text"},
    {"from": ["Shahjalal International Airport", "Hazrat Shahjalal International Airport"], "to": "Hazrat Shahjalal International Airport", "type": "text"},
    {"from": ["Hanover Airport", "Hannover Airport"], "to": "Hannover Airport", "type": "text"},
    {"from": ["Istanbul Airport", "Istanbul's Ataturk Airport", "Ataturk Airport"], "to": "Istanbul Airport", "type": "text"},
    {"from": ["Addis Ababa Bole International Airport", "Addis Abbaba Bole Airport"], "to": "Addis Ababa Bole International Airport", "type": "text"},
    {"from": ["Blaise Diagne Airport", "Blaise Diagne International Airport"], "to": "Blaise Diagne International Airport", "type": "text"},
    {"from": ["Boryspil Airport", "Boryspil International Airport"], "to": "Boryspil International Airport", "type": "text"},
    {"from": ["Domodedovo Airport", "Sheremetyevo Airport", "Vnukovo Airport"], "to": "Domodedovo Airport", "type": "text"},
    # Keep separate: these are genuinely different airports
]

# Filter out self-merges (from == to)
manual_merges = [m for m in manual_merges if len(m["from"]) > 0 and not (len(m["from"]) == 1 and m["from"][0] == m["to"])]

print(f"\n5. Applying {len(manual_merges)} manual merges...")
# Apply in batches to avoid too-large operations
BATCH = 30
for i in range(0, len(manual_merges), BATCH):
    batch = manual_merges[i:i+BATCH]
    apply_op({
        "op": "core/mass-edit",
        "description": "Mass edit cells in column Airport",
        "engineConfig": EMPTY_ENGINE,
        "columnName": "Airport",
        "expression": "value",
        "edits": batch,
    }, f"Manual merges batch {i//BATCH+1}")
    time.sleep(0.5)

# ── Final export ─────────────────────────────────────────────────────────
print("\nExporting Q4.csv...")
csv_text = requests.post(f"{BASE}/command/core/export-rows/{project_id}.csv",
    data={"project": project_id, "format": "csv", "options": json.dumps({})},
    params={"csrf_token": csrf}).text
with open(OUT_CSV, "w", encoding="utf-8", newline='') as f:
    f.write(csv_text)

# Verify
reader = csv.reader(io.StringIO(csv_text))
hdr = next(reader)
ai = hdr.index("Airport")
total = blanks = 0
names = {}
for row in reader:
    total += 1
    val = row[ai] if ai < len(row) else ""
    if not val.strip(): blanks += 1
    else: names[val] = names.get(val, 0) + 1
print(f"  Rows: {total}, Blanks: {blanks}, Distinct airports: {len(names)}")
print(f"  Top 20:")
for n, c in sorted(names.items(), key=lambda x: -x[1])[:20]:
    print(f"    {c:4d}  {n}")

print("\nExporting history.json...")
hist_resp = requests.get(f"{BASE}/command/core/get-operations",
    params={"project": project_id})
hist_data = hist_resp.json()
entries = hist_data.get("entries", [])
with open(OUT_HIST, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"\nDone!")
print(f"  {OUT_CSV}: {os.path.getsize(OUT_CSV)} bytes")
print(f"  {OUT_HIST}: {os.path.getsize(OUT_HIST)} bytes")
