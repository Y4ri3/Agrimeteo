"""Échoue si un secret semble présent dans le dépôt ou si .env est suivi par Git (critère C-04, risque R8)."""
import pathlib, re, subprocess, sys

root = pathlib.Path(__file__).resolve().parent.parent
SKIPPED_DIRS = {".git", ".venv", "node_modules", "dist", "reports", "__pycache__", "test-results", "deploy"}
SKIPPED_NAMES = {".env", "package-lock.json"}
TEXT_SUFFIXES = {"", ".py", ".ts", ".tsx", ".js", ".json", ".yml", ".yaml", ".toml", ".sh", ".md", ".csv", ".conf", ".example", ".txt"}
PATTERNS = {
    "clé privée": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "jeton GitHub": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "clé AWS": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "valeur sensible": re.compile(
        r"""(?i)\b[A-Z0-9_]*(?:password|passwd|secret|token|api_?key)\b\s*[:=]\s*["']?(?!\$|<|\{)[A-Za-z0-9/+_.-]{8,}"""
    ),
}


def tracked_env_files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []  # hors dépôt Git : rien à vérifier
    return [l for l in out.splitlines() if pathlib.PurePosixPath(l).name == ".env"]


def main():
    bad = [f"{f} : suivi par Git" for f in tracked_env_files()]
    for f in root.rglob("*"):
        rel = f.relative_to(root)
        if not f.is_file() or SKIPPED_DIRS.intersection(rel.parts) or f.name in SKIPPED_NAMES:
            continue
        if f.suffix not in TEXT_SUFFIXES or f == pathlib.Path(__file__).resolve():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                bad.append(f"{rel}:{line} : {label}")  # la valeur n'est jamais affichée
    print("secrets possibles :", bad or "aucun")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
