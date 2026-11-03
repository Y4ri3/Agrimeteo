# Registre des risques (vivant)
| ID | Risque | Proba | Impact | Action | État |
|---|---|---|---|---|---|
| R-A | Workflow GitHub Actions jamais exécuté (images Docker prouvées le 2026-11-02, voir `docs/preuves/J01/lots-5-6/`) | Moyenne | Haute | Premier run vert dans l’onglet Actions (T5-02) | Ouvert |
| R-B | Seuils agronomiques non fournis | Haute | Haute | Lot 2 : sources + validation, profil « a_valider » tant que non fait | Ouvert |
| R-C | Fournisseur météo non branché | Moyenne | Haute | T1-01 | Ouvert |
| R-D | Exigence ML de l'enseignant inconnue | Moyenne | Haute | ADR-003 | Ouvert |
| R-E | Compose < 2.24 sur un poste de dev (le runner GitHub est à jour) | Moyenne | Moyenne | Vérifier `docker compose version` | Ouvert |
| R-G | Déploiement cible non défini (un runner GitHub ne joint pas le localhost) | Haute | Moyenne | ADR-005 : job `deploy` prêt pour un runner auto-hébergé ; trancher avec le prof | Ouvert |
| R-H | Quota de minutes Actions (dépôt privé) | Faible | Moyenne | Vérifier la facturation GitHub ; dépôt public si autorisé | Ouvert |
| R-I | Versions Python non figées (`fastapi>=0.110`) : une nouvelle version peut changer le contrat et faire échouer la CI | Moyenne | Moyenne | Figer les versions (fichier de verrouillage), lot 3 | Ouvert |
| R-J | Migration testée sur un historique de test seulement | Moyenne | Faible | Refaire l'essai sur le vrai dépôt (T6-03) | Ouvert |
