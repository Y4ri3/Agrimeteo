"""Échoue si docs/api/openapi.json diverge de l'API réelle (critère A-02)."""
import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "backend"))
from app.export_openapi import render  # noqa: E402
ok = (root / "docs/api/openapi.json").read_text(encoding="utf-8") == render()
print("openapi.json à jour" if ok else "openapi.json DIVERGE : lancer `make -C backend openapi` et committer")
sys.exit(0 if ok else 1)
