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

## 15 novembre : Sprint 2 bis, séries chiffrées

`scripts/series.py`, `config/series.csv` (41 séries), `config/series_pays.yaml` (28 pays), tâche quotidienne `.github/workflows/series.yml`, page `v2/pages/3_Marches_et_series.py`.

Essai réel dans GitHub : 22 séries lues sur 22 hors Stooq (changes BCE, réserves COFER du FMI, 8 indicateurs Banque mondiale, 2 d'Our World in Data, inflation INSEE). La Banque mondiale renvoie souvent des erreurs 503 ou des délais dépassés : requêtes par paquets de 8 pays, deux essais, et une série en échec garde ses valeurs de la veille. Durée totale plafonnée à 12 minutes.

Stooq exige depuis début 2026 une clé gratuite obtenue par captcha : secret `STOOQ_API_KEY` à créer par Gabriel (voir `docs/README.md`).

Bourses : Stooq abandonné (clé par captcha introuvable chez Gabriel), remplacé par Yahoo Finance (`yfinance`, sans clé). Essai : 17 indices et 3 matières premières lus, MOEX désactivé (absent depuis les sanctions), Tadawul et EGX 30 ajoutés avec un historique court. Les séries sont désormais fusionnées avec l'historique stocké : 42 séries lues sur 42 actives. Réserve : Yahoo n'offre pas d'API officielle ; si la bibliothèque cesse de fonctionner, la page l'indiquera et une autre source sera branchée.

## 15 novembre : réparation des flux morts

Sur 65 sources en échec : 13 réparées et vérifiées par l'audit (INSEE publications conjoncturelles et chiffres détaillés, La Tribune, Connaissance des énergies, BRI discours de banquiers centraux, Federal Register toutes agences / Énergie / Transports via son API, Agence européenne de l'environnement, Nature, Commission européenne communiqués et actualités, Scroll.in) ; 18 désactivées parce qu'elles refusent les robots (Parlement européen, Conseil de l'UE, OCDE, AIE, Légifrance, FTC, Usine Nouvelle, Arab News, Addis Standard, Substack…), sans contournement ; 28 désactivées faute de flux trouvé ou en sommeil ; 6 gardées car en erreur passagère (429, 504, délai : VentureBeat, JRC, Atomico, Animal Político, Huxiu, 36Kr à surveiller). Plusieurs désactivées sont déjà couvertes par GDELT (Arab News, Xinhua, Huxiu) ou par la tâche Series (FMI). Pistes suivantes pour les institutions qui bloquent les flux : API open data du Parlement européen, API Légifrance (inscription PISTE), données OCDE en SDMX.

# Sprint 3 – Classement

## 16 novembre : évaluation sur le jeu de référence (`docs/evaluation-sprint3.md`)

Tri (Ministral) : par lots de 20 avec la consigne v2, 92 % d'accord, 100 % des articles pertinents retrouvés, 64 % des hors-sujet écartés ; article par article, la v2 laisse presque tout passer (9 % de NON écartés) et la v1 en écarte 41 %. Le tri par lots est retenu : meilleur et 20 fois moins de requêtes.

Fiche (Mistral Small, consigne v3 sans axe, précipitation ni rebond) : lentille 76 % (95 % en comptant la secondaire), iceberg 68 %, nature 80 %, aire du sujet 84 %, JSON 100 %. Premier passage : aire à 51 % (le modèle mettait GLO partout et confondait JK et CN) ; corrigé en déduisant l'aire des pays cités (`config/zones_pays.csv`) et en précisant la consigne. Sur 85 articles, l'incertitude est d'environ ±5 points.

## 16 novembre : classement dans la collecte

À chaque collecte : tri par lots de tous les nouveaux articles, puis fiche pour les OUI et DOUTE, dans la limite de 700 fiches par jour et 150 par passage (`config/seuils.yaml`, section `classement`), à part égale entre les aires de source. Le texte utilisé est celui du flux, sinon la page lue, gardé en mémoire et jamais stocké. Les articles écartés restent dans le stock avec `tri = NON` (au lieu d'un fichier de rejets à part, plus simple). Les articles en surplus restent sans fiche (`classe = False`) ; un rattrapage pourra les classer plus tard sur leur titre et leur extrait. Page « Fiches » : filtres par lentille, aire du sujet, iceberg et nature.
