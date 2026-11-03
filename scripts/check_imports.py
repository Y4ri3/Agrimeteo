"""Garde-fou multirepo (critère I-04) : aucune dépendance interdite entre modules (cahier, 4.2)."""
import ast, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN_PY = {"backend": {"frontend", "e2e", "infra"}, "ml": {"app", "backend", "frontend", "e2e", "infra"}}
SKIPPED = {".venv", "node_modules", "dist", "reports"}
TS_IMPORT = re.compile(r"""(?:from\s+|import\s*\(?\s*|require\(\s*)["']([^"']+)["']""")


def sources(folder, *patterns):
    for pattern in patterns:
        for f in (root / folder).rglob(pattern):
            if not SKIPPED.intersection(f.parts):
                yield f


def check_python(f, forbidden):
    text = f.read_text(encoding="utf-8")
    rel = f.relative_to(root)
    if re.search(r"\.\./(frontend|e2e|infra|backend|ml)\b|sys\.path\.(append|insert)", text):
        yield f"{rel} : contourne les modules par un chemin"
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names = [node.module or ""]
        else:
            continue
        for name in names:
            if name.split(".")[0] in forbidden:
                yield f"{rel} : importe {name}"


def check_frontend(f):
    for target in TS_IMPORT.findall(f.read_text(encoding="utf-8")):
        if not target.startswith("."):
            continue
        resolved = (f.parent / target).resolve()
        if not resolved.is_relative_to(root / "frontend"):
            yield f"{f.relative_to(root)} : importe {target}, hors du frontend"


def main():
    bad = []
    for folder, forbidden in FORBIDDEN_PY.items():
        for f in sources(folder, "*.py"):
            bad.extend(check_python(f, forbidden))
    for f in sources("frontend", "*.ts", "*.tsx", "*.js"):
        bad.extend(check_frontend(f))
    print("violations :", bad or "aucune")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
