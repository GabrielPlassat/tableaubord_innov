# Journal du Sprint 2 – Collecte continue et stockage

*14 novembre 2026, branche `v2-sprint2`.*

## Ce qui est livré

| Élément | Fichier |
|---|---|
| Tâche de collecte toutes les 6 heures (0 h 23, 6 h 23, 12 h 23, 18 h 23 UTC) | `.github/workflows/collecte.yml`, `scripts/collecte.py` |
| Requêtes GDELT pour CN, JK, GO, MO (10 requêtes, une toutes les 6 secondes) | `config/gdelt.yaml` |
| Plafond par aire et par jour, réglages du dédoublonnage et de la lecture des pages | `config/seuils.yaml`, section `collecte` |
| Stockage des fiches sur Hugging Face, jeu de données privé créé automatiquement | `config/stockage.yaml` |
| Journal des collectes et suivi de chaque source | `journal/executions.csv`, `journal/collecte_sources.csv` |
| Page « État du système » | `v2/pages/2_Etat_du_systeme.py` |

## Choix faits

- **Texte du flux d'abord.** Si le flux donne moins de 500 caractères, la page est lue (300 au plus par passage) pour **mesurer** la longueur du texte disponible ; le texte est jeté aussitôt. Chaque fiche porte `texte_source` (FLUX, PAGE, TITRE) et `longueur_texte` : on saura au Sprint 3 quelle part des articles peut être classée sur un vrai texte.
- **Droits d'auteur.** Seul un extrait du flux est conservé (280 caractères au plus, réglable), avec le titre et l'URL.
- **Dédoublonnage** : URL canonique (sans `www`, sans paramètres de suivi), puis titres à 80 % de mots communs à moins de 3 jours. La fiche gardée est celle de la source la mieux ancrée (LOCAL d'abord) ; elle compte ses `reprises` et garde la liste des sources et des URL reprises, pour ne pas les recompter au passage suivant. Le troisième filet (vecteurs, doublons entre langues) arrive au Sprint 3 avec les vecteurs.
- **Plafond par aire** : 150 articles par aire et par jour, 120 pour EU, 100 pour US. Les articles écartés sont comptés dans le journal.
- **Sources en échec** : 7 jours de suite → « SIGNALEE » ; 30 jours → désactivée automatiquement dans `config/sources.csv`, avec une remarque. Le décompte part du premier échec constaté par la collecte : les 71 flux morts de la v1 ne seront donc pas retirés avant 30 jours, ce qui vous laisse le temps de décider.
- **GDELT** : les articles portent `source_id = gdelt-<domaine>` et `lien_pouvoir = INCONNU`, faute de connaître le propriétaire du site. Citation de GDELT affichée sur la page.
- **Sans classement** : la colonne `classe` vaut `False`. Le classement (Ministral, puis Mistral Small) s'ajoutera dans la même tâche au Sprint 3, pour que le texte lu n'ait jamais à être stocké.

## Essai

Essai hors ligne (flux simulés, 138 sources, deux passages) : 390 fiches au premier passage, aucune au second, une dépêche reprise par 83 sources gardée une seule fois avec 83 reprises, plafond EU et US appliqué, identifiants uniques. Les trois pages de l'application s'affichent sans erreur. Le bac à sable de Claude n'a pas accès aux flux réels : le premier vrai passage se fera dans GitHub.

## À faire par Gabriel

Voir `docs/README.md`, section « Mise en route du Sprint 2 ».

## 15 novembre : GDELT passe aux fichiers bruts

Bilan des trois premiers passages réels :

| Passage (UTC) | Durée | Vus | Nouvelles fiches | GDELT |
|---|---|---|---|---|
| 14/11 20 h 49 (manuel) | 3 min 38 | 2 171 | 1 347 | 11 articles, 10 requêtes refusées sur 10 |
| 14/11 21 h 15 (manuel) | 27 min | 1 457 | 28 | 24 articles, 7 refus |
| 15/11 6 h 51 (planifié) | 4 min 39 | 1 515 | 685 | 0 article (requêtes groupées : réponses vides ou refus) |

Constats : l'API de GDELT refuse les adresses partagées de GitHub ; les requêtes groupées par pays ne renvoient rien. La collecte planifiée de 0 h 23 n'a pas eu lieu : GitHub retarde ou saute parfois les tâches planifiées aux heures chargées (celle de 6 h 23 est partie à 6 h 51). 74 sources sur 138 répondent.

Décision : lecture des **fichiers bruts GKG 2.1** (`data.gdeltproject.org/gdeltv2/`), en anglais et traduits, toutes les tranches de 15 minutes depuis le dernier passage (`journal/gdelt_dernier_fichier.txt`). On garde les articles des aires non occidentales qui portent au moins 3 thèmes utiles (énergie, économie, technologie, Banque mondiale…), 40 au plus par aire et par passage. L'aire se déduit d'une liste de sites connus, puis de l'extension nationale, puis de la langue d'origine (`config/gdelt.yaml`). `zones_pays.csv` est complété de 67 pays.

## 15 novembre : jeu de référence de 100 articles (préparation du Sprint 3)

`tests/reference_100.csv` : 100 articles tirés du stock réel (6 à 11 par aire, 15 langues, un tiers GDELT), pré-étiquetés par Claude, relus et validés par Gabriel (23 corrections). Champs : pertinent, lentille principale, iceberg, aire du sujet, nature ; plusieurs réponses acceptables séparées par `|`. Résultat : 67 OUI, 22 NON, 11 cas laissés ouverts.

Leçon pour le tri : sur les 31 cas limites, Gabriel en a tranché 20, dont 14 en OUI. Il garde tout ce qui touche au pouvoir, aux institutions et aux règles, même sans décision (registre électoral, débat, propagande, répression, sanction, sport comme terrain géopolitique, programme d'aide publique), ainsi que les recherches techniques pointues. Il écarte l'anecdote sans enjeu (protocole, incident de conférence de presse, curiosité naturaliste, commémoration, promotion de produit). D'où `config/consignes/passe1_v2.txt`, plus inclusive que la v1, à comparer au Sprint 3.
