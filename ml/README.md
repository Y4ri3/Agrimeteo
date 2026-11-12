# ml : indicateurs et moteur de règles (lot 2)

Pas de machine learning, c'est définitif : aucune variable cible fiable (rendement, résultat de semis), voir `docs/decisions.md`.
Le moteur est un moteur de règles, vérifié par des scénarios et des bornes (P-01 à P-07), pas par un taux de réussite.

```text
src/agrimeteo_ml/indicators.py   les 11 indicateurs du cahier §7.3 (fonctions pures, une valeur manquante n'est jamais 0)
src/agrimeteo_ml/profiles.py     lecture et validation des profils YAML (P-06)
src/agrimeteo_ml/engine.py       moteur : critères -> niveau, explications en français, confiance
rules/*.yaml                     profils de culture : tomate, riz, arachide, mil
data/sample/                     extrait de données réelles pour la démonstration hors ligne
```

```bash
make setup test        # ou : make ci
```

## Origine
Les profils et les règles du moteur viennent du notebook définitif du lot 2 (`devoir_devops.ipynb`). Le moteur a été
recoupé avec lui : sur 12 localités × 4 cultures au 15 septembre 2025, les 48 résultats sont identiques.

## Profils de culture
Un critère = un indicateur calculé sur une fenêtre (`window_days`), un sens (`lower_is_worse` ou `higher_is_worse`),
un seuil de vigilance et/ou un seuil défavorable, une source, et un caractère bloquant ou non. Un seuil est « franchi »
dès qu'il est atteint : valeur ≥ seuil pour un maximum, valeur ≤ seuil pour un minimum. Tout seuil exige une source
(`make check`). `status: a_valider` plafonne le résultat à « favorable sous réserve » ; `valide_par_source` permet
« favorable » et exige seuils et source pour tous les critères.

| Culture | Critères (vigilance / défavorable) |
|---|---|
| Arachide | jour le plus chaud (38 / 42 °C, bloquant) ; plus longue période sans pluie (10 / 20 jours, bloquant) ; pluie cumulée (60 mm ou moins) |
| Mil | jour le plus chaud (40 / 45 °C, bloquant) ; plus longue période sans pluie (15 / 25 jours, bloquant) ; pluie cumulée (50 mm ou moins) |
| Riz | jour le plus chaud (35 / 38 °C, bloquant) ; nuit la plus froide (18 / 15 °C, bloquant) ; pluie cumulée (150 mm ou moins) ; gel (1 jour, bloquant) |
| Tomate | jour le plus chaud (35 / 40 °C, bloquant) ; nuit la plus froide (12 / 10 °C, bloquant) ; gel (1 jour, bloquant) ; bilan pluie moins ET0 (-150 mm ou moins) ; humidité (80 % ou plus) |

Toutes les fenêtres sont de 30 jours. Les sources sont celles du notebook (FAO EcoCrop, IRRI, FAO 56…) et sont écrites dans
chaque fichier YAML. **Plusieurs sont des références générales, pas des citations précises** (par exemple
« Tolérance du mil à la sécheresse ») : c'est la raison du statut `a_valider`.

## Différences assumées avec le notebook
- Un jour manquant ne rend pas tout l'indicateur indéfini : les valeurs connues sont utilisées et le critère n'est
  « indéterminé » que si la complétude des variables essentielles passe sous 90 % (le notebook met NaN dès qu'un jour manque).
- La confiance tient compte de la résolution et du statut du profil, comme le demande le cahier (§7.4), en plus de la
  complétude. Elle est donc « moyenne » au mieux avec des profils à valider ; le notebook allait jusqu'à « élevée ».
- Le statut `a_valider` n'existe pas dans le notebook : il plafonne le niveau (P-07).

## Limites
- Pas d'humidité du sol modélisée : le bloc reste « non disponible ».
- Pas d'interpolation des trous de température : un trou rend le critère non évaluable.
- Les 12 localités du notebook ont une Tmin toujours au-dessus de 12 °C : les critères de gel ne se déclenchent jamais au Sénégal.
