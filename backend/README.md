# backend : API FastAPI (lot 3)

État : **squelette**. Les 6 endpoints du contrat existent et répondent avec des données factices
(`app/services/stub.py`). Le travail du lot 3 est de les brancher sur les fournisseurs (lot 1)
et sur le moteur (lot 2) **sans changer le contrat** (sinon : voir `docs/decisions/` et prévenir le lot 6).

```bash
make setup          # installe ml et backend en mode éditable
make test           # tests + rapports dans reports/
uvicorn app.main:app --reload     # http://localhost:8000/docs
make openapi        # régénère docs/api/openapi.json (à committer si le contrat change)
```
Règle : toute modification de route ou de schéma = `make openapi` + commit du fichier.
`scripts/check_openapi.py` fait échouer la CI si les deux divergent (critère A-02).
