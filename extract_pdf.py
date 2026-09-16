import sys
import io
from pypdf import PdfReader

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = sys.argv[1] if len(sys.argv) > 1 else r"d:\CodingProjects\cse-6242-oan\hw\HW1.pdf"
reader = PdfReader(path)
print(f"### {path} - {len(reader.pages)} pages ###")
for i, page in enumerate(reader.pages):
    print(f"\n========== PAGE {i + 1} ==========")
    print(page.extract_text())
