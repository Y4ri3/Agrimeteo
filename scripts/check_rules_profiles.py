"""Un profil non validé ne doit avoir aucune source déclarée « valide » ; un profil valide exige une source et des seuils."""
import pathlib, sys
import yaml
root = pathlib.Path(__file__).resolve().parent.parent
errs = []
for f in sorted((root / "ml/rules").glob("*.yaml")):
    p = yaml.safe_load(f.read_text(encoding="utf-8"))
    if p.get("status") not in ("a_valider", "valide"):
        errs.append(f"{f.name}: status invalide")
    if p.get("status") == "valide":
        if not p.get("source"):
            errs.append(f"{f.name}: 'valide' sans source")
        if any(c.get("threshold") is None for c in p.get("criteria", [])):
            errs.append(f"{f.name}: 'valide' avec seuil null")
print("erreurs :", errs or "aucune")
sys.exit(1 if errs else 0)
