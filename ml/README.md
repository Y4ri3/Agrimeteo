# ml : indicateurs et moteur de règles (lot 2)

Pas de machine learning : aucune variable cible fiable (rendement, résultat de semis), voir `docs/decisions.md`.

```text
src/agrimeteo_ml/indicators.py   indicateurs du cahier §7.3 (fonctions pures, une valeur manquante n'est jamais 0)
src/agrimeteo_ml/profiles.py     lecture et validation des profils YAML (P-06)
src/agrimeteo_ml/engine.py       moteur : critères -> niveau, explications en français, confiance (P-01 à P-07)
rules/*.yaml                     profils de culture : arachide, mil
data/sample/                     extrait de données réelles pour la démonstration hors ligne
```

```bash
make setup test        # ou : make ci
```

## Profils de culture
Un critère = un indicateur, un sens (`lower_is_worse` ou `higher_is_worse`), deux seuils (`vigilance`, `unfavorable`),
une source, et un caractère bloquant ou non. Une valeur « trop basse » est défavorable **sous** le seuil ; une valeur
« trop haute » l'est **à partir** du seuil. Tout seuil exige une source (`make check`).
`status: a_valider` plafonne le résultat à « favorable sous réserve » ; `valide_par_source` permet « favorable »
et exige que tous les critères aient seuils et source.

## Sources des seuils
| Critère | Seuils (vigilance / défavorable) | Source |
|---|---|---|
| Plus forte pluie sur 3 jours | 20 mm / 10 mm | Sivakumar (1988) : 20 mm sur 2-3 jours déclenchent le semis ; étude sur le semis du mil au Niger (HAL hal-00584850) : les agriculteurs sèment dès 10 mm en 2 jours |
| Plus longue période sèche | 7 jours / 10 jours | Sivakumar (1988) : pas de pause sèche de 7 jours ou plus après le semis ; même étude Niger : 23 % des semis échouent après une pause de plus de 9 jours |
| Température moyenne, chaleur (arachide) | 28 °C / 33 °C | [FAO, fiche arachide](https://www.fao.org/land-water/databases-and-software/crop-information/groundnut/en/) : optimum 22-28 °C, rendement en baisse au-delà de 33 °C |
| Température moyenne, fraîcheur (arachide) | 22 °C / 18 °C | même fiche FAO : rendement en baisse en dessous de 18 °C |

Jour sec : moins de 1 mm de pluie (seuil de jour pluvieux des études sahéliennes).

## Limites assumées (profils « à valider »)
- La règle de Sivakumar décrit le **début de saison des pluies**, avec une pause sèche observée *après* l'épisode
  pluvieux. L'application analyse une fenêtre **passée** : on utilise donc la plus forte pluie sur 3 jours et la plus
  longue période sèche **de la fenêtre**. C'est une adaptation de l'équipe, d'où le statut `a_valider`.
- Les seuils d'arachide et de mil sont identiques pour la pluie. Le mil n'a aucun critère de température : aucun seuil
  sourcé n'a été retenu. Il n'y a pas de critère de gel (rare au Sénégal).
- Pas d'humidité du sol modélisée : le bloc reste « non disponible ».
- Pas d'interpolation des trous de température : un trou rend le critère non évaluable.
