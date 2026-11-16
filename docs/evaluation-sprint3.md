# Évaluation du classement (Sprint 3)

*16/11/2026 09:25 UTC · jeu de référence de 100 articles · pages lues : 90% · appels à Albert : 305*

Modèle de tri : `ministral-3-8b-instruct-2512` · modèle de fiche : `mistral-small-3-2-24b-instruct-2506` · consignes : passe1 v1, v2, lot v2 ; passe2 v3.

## Tri (passe 1)

|                                     | article par article, v1   | article par article, v2   | par lots de 20, v2   |
|:------------------------------------|:--------------------------|:--------------------------|:---------------------|
| accord (cas ouverts comptés justes) | 87 %                      | 80 %                      | 91 %                 |
| OUI retrouvés (rappel)              | 100 %                     | 100 %                     | 99 %                 |
| NON écartés                         | 41 %                      | 9 %                       | 64 %                 |
| réponses illisibles                 | 0 %                       | 0 %                       | 0 %                  |


Durée moyenne : 0.3 s par article et par consigne ; par lots : 4 s pour les 100 articles.

## Fiche (passe 2), sur les 85 articles étiquetés

|                                   | accord   |
|:----------------------------------|:---------|
| JSON valide                       | 100 %    |
| lentille principale               | 75 %     |
| lentille principale ou secondaire | 93 %     |
| iceberg                           | 67 %     |
| aire du sujet                     | 84 %     |
| nature                            | 82 %     |


Durée moyenne : 8.8 s par fiche. Seuils visés (L2) : lentille 80 %, iceberg 65 %, aire 90 %, nature 80 %, JSON 98 %.

Détail article par article : `journal/evaluation_sprint3.csv`.
