# Évaluation du classement (Sprint 3)

*21/11/2026 16:09 UTC · jeu de référence de 100 articles · pages lues : 90% · appels à Albert : 305*

Modèle de tri : `ministral-3-8b-instruct-2512` · modèle de fiche : `mistral-small-3-2-24b-instruct-2506` · consignes : passe1 v1, v2, lot v2 ; passe2 v5.

## Tri (passe 1)

|                                     | article par article, v1   | article par article, v2   | par lots de 20, v2   |
|:------------------------------------|:--------------------------|:--------------------------|:---------------------|
| accord (cas ouverts comptés justes) | 87 %                      | 80 %                      | 92 %                 |
| OUI retrouvés (rappel)              | 100 %                     | 100 %                     | 100 %                |
| NON écartés                         | 41 %                      | 9 %                       | 64 %                 |
| réponses illisibles                 | 0 %                       | 0 %                       | 0 %                  |


Durée moyenne : 0.2 s par article et par consigne ; par lots : 4 s pour les 100 articles.

## Fiche (passe 2), sur les 85 articles étiquetés

|                                   | accord   |
|:----------------------------------|:---------|
| JSON valide                       | 100 %    |
| lentille principale               | 87 %     |
| lentille principale ou secondaire | 95 %     |
| iceberg                           | 73 %     |
| aire du sujet                     | 85 %     |
| nature                            | 79 %     |


Durée moyenne : 7.9 s par fiche. Seuils visés (L2) : lentille 80 %, iceberg 65 %, aire 90 %, nature 80 %, JSON 98 %.

Répartition des lentilles principales proposées : PUI 36, SOC 22, MON 15, TEC 11, MIL 6, SOL 5, INF 5

Détail article par article : `journal/evaluation_sprint3.csv`.
