# backend : API FastAPI (lot 3)

Les 6 endpoints du contrat sont branchés sur une interface de fournisseurs (`app/providers/`), un contrôle
qualité, un cache de fichiers et des indicateurs. Fournisseurs : `open_meteo` (réel), `csv` (extrait réel hors ligne,
`CSV_PATH`) et `fixture` (**factice**, défaut, sans réseau). Aucun test n'appelle Internet. Le moteur de décision
(`app/services/engine.py`) et les profils de culture (`app/services/crops.py`) sont **provisoires** en
attendant le module `ml` (lot 2) : sans seuil validé, le niveau est toujours « indéterminé ».

```bash
make setup          # installe ml et backend en mode éditable
make test           # tests + rapports dans reports/ (aucun accès réseau)
uvicorn app.main:app --reload     # http://localhost:8000/docs
make openapi        # régénère docs/api/openapi.json (à committer si le contrat change)
```

Brancher un fournisseur (lot 1) : implémenter `WeatherProvider` (`providers/base.py`) et l'ajouter à
`providers.REGISTRY` ; il devient disponible via `WEATHER_PROVIDER` ou `?source=`. Les pannes se signalent en
levant `ProviderUnavailable` (502), `ProviderRateLimited` (503) ou `ProviderTimeout` (504).

Règle : toute modification de route ou de schéma = `make openapi` + commit du fichier.
`scripts/check_openapi.py` fait échouer la CI si les deux divergent (critère A-02).
