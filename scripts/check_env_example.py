"""Échoue si une variable lue par le code Python (backend, ml) manque dans .env.example (critère C-05)."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
READS = re.compile(r"""(?:environ\.get\(|environ\[|getenv\(|_int\()\s*["']([A-Z][A-Z0-9_]+)["']""")
used = set()
for folder in ("backend/app", "ml/src"):
    for f in (root / folder).rglob("*.py"):
        used.update(READS.findall(f.read_text(encoding="utf-8")))
declared = {l.split("=")[0].strip() for l in (root / ".env.example").read_text(encoding="utf-8").splitlines() if "=" in l}
missing = used - declared
print(f"{len(used)} variables lues ; manquantes dans .env.example :", sorted(missing) or "aucune")
sys.exit(1 if missing else 0)
