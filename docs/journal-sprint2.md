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
