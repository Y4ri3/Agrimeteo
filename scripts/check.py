"""Contrôles du dépôt (une seule commande : `python scripts/check.py`).

I-04 imports entre modules · C-05 .env.example · P-06 profils de règles · C-04 secrets.
Le contrat OpenAPI (A-02) est vérifié à part par check_openapi.py : il voyage avec le dépôt backend.
"""
import ast, pathlib, re, subprocess, sys

root = pathlib.Path(__file__).resolve().parent.parent
SKIPPED = {".git", ".venv", "node_modules", "dist", "reports", "__pycache__", "test-results", "deploy"}


def files(folder, *patterns):
    for pattern in patterns:
        for f in (root / folder).rglob(pattern):
            if not SKIPPED.intersection(f.relative_to(root).parts):
                yield f


# --- I-04 : aucune dépendance interdite entre modules (cahier, 4.2) ---------------------------------
FORBIDDEN_PY = {"backend": {"frontend", "e2e", "infra"}, "ml": {"app", "backend", "frontend", "e2e", "infra"}}
TS_IMPORT = re.compile(r"""(?:from\s+|import\s*\(?\s*|require\(\s*)["']([^"']+)["']""")


def check_imports():
    bad = []
    for folder, forbidden in FORBIDDEN_PY.items():
        for f in files(folder, "*.py"):
            text = f.read_text(encoding="utf-8")
            rel = f.relative_to(root)
            if re.search(r"\.\./(frontend|e2e|infra|backend|ml)\b|sys\.path\.(append|insert)", text):
                bad.append(f"{rel} : contourne les modules par un chemin")
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = [node.module or ""]
                else:
                    continue
                bad += [f"{rel} : importe {n}" for n in names if n.split(".")[0] in forbidden]
    for f in files("frontend", "*.ts", "*.tsx", "*.js"):
        for target in TS_IMPORT.findall(f.read_text(encoding="utf-8")):
            if target.startswith(".") and not (f.parent / target).resolve().is_relative_to(root / "frontend"):
                bad.append(f"{f.relative_to(root)} : importe {target}, hors du frontend")
    return bad


# --- C-05 : toute variable lue par le code figure dans .env.example ----------------------------------
READS = re.compile(r"""(?:environ\.get\(|environ\[|getenv\(|_int\()\s*["']([A-Z][A-Z0-9_]+)["']""")


def check_env_example():
    used = set()
    for folder in ("backend/app", "ml/src"):
        for f in files(folder, "*.py"):
            used.update(READS.findall(f.read_text(encoding="utf-8")))
    lines = (root / ".env.example").read_text(encoding="utf-8").splitlines()
    declared = {l.split("=")[0].strip() for l in lines if "=" in l}
    return [f".env.example : variable manquante {v}" for v in sorted(used - declared)]


# --- P-06 : chaque seuil d'un profil a une source (règles de validation du module ml) ---------------
def check_rules_profiles():
    import yaml
    from agrimeteo_ml.profiles import problems

    errs = []
    for f in sorted((root / "ml/rules").glob("*.yaml")):
        errs += [f"{f.name} : {p}" for p in problems(yaml.safe_load(f.read_text(encoding="utf-8")) or {})]
    return errs


# --- C-04 : aucun secret dans le dépôt, .env jamais suivi par Git ------------------------------------
TEXT_SUFFIXES = {"", ".py", ".ts", ".tsx", ".js", ".json", ".yml", ".yaml", ".toml", ".sh", ".md", ".conf", ".example", ".txt"}
SECRETS = {
    "clé privée": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "jeton GitHub": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "clé AWS": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "valeur sensible": re.compile(
        r"""(?i)\b[A-Z0-9_]*(?:password|passwd|secret|token|api_?key)\b\s*[:=]\s*["']?(?!\$|<|\{)[A-Za-z0-9/+_.-]{8,}"""
    ),
}


def check_secrets():
    bad = []
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout
        bad += [f"{l} : suivi par Git" for l in tracked.splitlines() if pathlib.PurePosixPath(l).name == ".env"]
    except (OSError, subprocess.CalledProcessError):
        pass  # hors dépôt Git : rien à vérifier
    for f in root.rglob("*"):
        rel = f.relative_to(root)
        if not f.is_file() or SKIPPED.intersection(rel.parts) or f.name in {".env", "package-lock.json"}:
            continue
        if f.suffix not in TEXT_SUFFIXES or f == pathlib.Path(__file__).resolve():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRETS.items():
            for m in pattern.finditer(text):
                bad.append(f"{rel}:{text.count(chr(10), 0, m.start()) + 1} : {label}")  # valeur jamais affichée
    return bad


CHECKS = {
    "imports (I-04)": check_imports,
    ".env.example (C-05)": check_env_example,
    "profils de règles (P-06)": check_rules_profiles,
    "secrets (C-04)": check_secrets,
}

if __name__ == "__main__":
    failed = False
    for name, check in CHECKS.items():
        problems = check()
        print(f"{name} : {'OK' if not problems else 'ÉCHEC'}")
        for p in problems:
            print("  -", p)
        failed |= bool(problems)
    sys.exit(1 if failed else 0)
