# L5 – Cahier des charges technique (Innovation Radar v2)

*Version 1.0 du 14 novembre 2026. Destinataire : Claude Code (Opus 5.5 ou Sonnet 5.5) pour les sprints 1 à 6.*

> **Mises à jour par `decisions-sprint0.md`** : application Streamlit privée ; fiches sur Hugging Face dans un jeu de données privé ; budget avec alerte à 50 $ et arrêt à 60 $ (au lieu de 60 $ et 90 $). Choix du Sprint 1 : voir `journal-sprint1.md` (la v1 reste à la racine ; la v2 vit dans `v2/`).

**À lire avec** : `L1-grille.md` (vocabulaire et codes), `L2-classement.md` (consignes de classement), `L3-agents.md` (consignes des agents), `04-presentation-interrogation.md` (description détaillée des écrans, intégrée ici comme annexe A, avec les amendements du chapitre 6).

**Règle de lecture pour Claude Code** : en cas de contradiction, `decisions-sprint0.md` l'emporte, puis L1 sur les codes, ce document sur l'architecture, l'annexe A sur le détail visuel. Toute question de conception non couverte se résout par l'option la plus simple, signalée dans le journal du sprint.

---

## 0. Ce que je change par rapport au cadrage

| Constat | Proposition |
|---|---|
| **Seize modules** pour un utilisateur seul, non développeur : la v2 ne sortira pas. | Une **v2 à 9 écrans**. Sept modules sont renvoyés en v3 (chapitre 6.2). |
| **L'évaluation des modèles au Sprint 6**, après trois mois de classement : s'il faut changer de modèle, tout est à reclasser. | L'évaluation passe **au début du Sprint 3**. |
| **Rien de visible avant le Sprint 4.** | Chaque sprint se termine par **un écran utilisable**. |
| **Le curseur de temps « recalcule l'affichage »** à toute date : lourd. | Des **photographies mensuelles** des objets. « Comparer » lit deux photographies. |
| **Les brevets chaque semaine** : aucune source gratuite simple. | Renvoyés en v3. En v2, les publications scientifiques par pays (OpenAlex) servent d'indice. |
| **Stocker l'historique dans le dépôt** : il grossira au-delà du raisonnable. | Les **fiches** sur Hugging Face ; les **objets**, petits et modifiables à la main, dans le dépôt GitHub, où chaque modification est déjà historisée. |

---

## 1. Contexte et contraintes

| Contrainte | Conséquence |
|---|---|
| Utilisateur non développeur, sans droits d'administration | Rien ne s'installe sur son poste. Tout se fait dans un navigateur : GitHub, Streamlit Community Cloud, Colab, Claude Code en ligne. |
| Infrastructure gratuite | GitHub Actions sur dépôt public, Streamlit Community Cloud, Hugging Face Datasets, sources ouvertes. |
| Albert en priorité | Classement, résumés, vecteurs. API compatible OpenAI, adresse `https://albert.api.etalab.gouv.fr/v1`. Les identifiants de modèles se lisent par `GET /v1/models`, jamais en dur dans le code. |
| Budget API Claude | **Alerte à 50 $, arrêt des appels non essentiels à 60 $** (`decisions-sprint0.md`). |
| Droits d'auteur | On ne conserve que le titre, l'URL, un résumé rédigé par le modèle et les étiquettes. Le texte lu est jeté après le classement. |
| Maintenance par l'utilisateur | Tout réglage est une ligne dans un fichier CSV ou YAML modifiable depuis GitHub. Aucun réglage dans le code. |

Les quatre vérifications préalables sont faites : voir `verifications.md`.

---

## 2. Ce qu'on garde et ce qu'on remplace de la v1

| Élément de la v1 | Sort |
|---|---|
| Les 7 fichiers `*_rss.csv` (environ 120 flux) | **Fusionnés** dans le registre unique `config/sources.csv` (fait au Sprint 1). Les anciens fichiers restent en place tant que la v1 tourne. |
| `personnes.csv`, `personnes_rss.csv` | Gardés : les personnes deviennent des sources de type `PERSONNE`. |
| `projets.csv`, `projets_historique.csv` (TRL, Gartner, 2024) | Servent d'amorce à la table des technologies, marqués « à réviser ». |
| `signaux_faibles.csv` | Importé comme 7 fiches manuelles. |
| Thème sombre, graphiques Plotly, courbe de Gartner | Gardés. |
| Cartes de prix (énergie, matières) | Gardées sur une page « Marchés », inchangée. |
| Collecte à l'ouverture de l'application, cache d'une heure | **Remplacée** par la collecte planifiée. |
| Synthèse Gemini sur les titres | **Remplacée** par les agents de L3. |
| `app.py` de 1 150 lignes en un seul fichier | **Remplacé** par une application à plusieurs pages (`v2/`). L'ancien fichier continue de fonctionner jusqu'à la fin du Sprint 4, puis est déplacé dans `v1/`. |

---

## 3. Architecture et calendrier

### 3.1 Schéma

```
GitHub Actions (planifié)                      Hugging Face Datasets (privé)
┌──────────────────────────┐                   ┌──────────────────────────┐
│ collecter → dédoublonner │── fiches ────────▶│ fiches/AAAA-MM.parquet   │
│ → passe 1 → passe 2      │                   │ rejets/AAAA-MM.parquet   │
│ → vecteurs → regrouper   │                   │ vecteurs/AAAA-MM.npy     │
│                          │                   │ series/*.parquet         │
│ agents A1 à A10          │── objets ──┐      └────────────┬─────────────┘
└──────────┬───────────────┘            ▼                   │
           │                 Dépôt GitHub (public)          │
           │                 ┌──────────────────────────┐   │
           │                 │ config/   réglages CSV   │   │
           └── journal ─────▶│ objets/   CSV et JSONL   │   │
                             │ photos/   AAAA-MM/       │   │
                             │ syntheses/ Markdown      │   │
                             │ annotations/             │   │
                             │ journal/  exécutions,    │   │
                             │           coûts          │   │
                             └────────────┬─────────────┘   │
                                          ▼                 ▼
                             Streamlit Community Cloud (privé ; lecture seule,
                             sauf annotations et assistant)
```

### 3.2 Les tâches planifiées

| Tâche | Rythme | Contenu | Modèle |
|---|---|---|---|
| `collecte` | Toutes les 6 heures | Flux RSS, pages, extraction du texte, dédoublonnage, passe 1, passe 2, vecteurs | Albert ; Haiku si échec |
| `quotidien` | Chaque jour | Volumes GDELT par marqueur de tension et par technologie ; publications OpenAlex ; contrôles de qualité ; indicateurs du Miroir | Aucun |
| `hebdo` | Lundi | Regroupement des sujets ; tensions libres ; calcul du baromètre ; agents A1, A2, A10 | Opus |
| `mensuel` | Le 1er | Séries lentes ; agents A3, A4, A5, A6, A8, A9, A10 ; photographie des objets | Opus, Fable (Batch) |
| `trimestriel` | 1er janvier, avril, juillet, octobre | Agent A7 | Fable (Batch) |
| `annotations` | Chaque nuit | Applique les annotations de la veille aux objets | Aucun |
| `dossier` | À la demande | Un dossier sur une question | Fable |
| `audit_sources` | Lundi, à la demande, et à chaque modification du registre | Teste tous les flux (fait au Sprint 1) | Aucun |

Chaque tâche peut aussi être lancée à la main depuis l'onglet Actions de GitHub.

**Séries lentes collectées chaque mois** : Banque mondiale, FMI (dont COFER), Our World in Data, ONU (population), Energy Institute, Ember. Les enquêtes de valeurs sont chargées à la main à chaque nouvelle vague.

### 3.3 Briques logicielles (Python)

| Besoin | Brique |
|---|---|
| Lecture des flux | `feedparser` (déjà en v1) |
| Extraction du texte d'une page | `trafilatura` |
| Appels à Albert | Bibliothèque `openai`, avec l'adresse d'Albert |
| Appels à Claude | Bibliothèque `anthropic`, avec cache sur les préambules et traitement différé (Batch) pour les agents mensuels |
| Stockage | `pandas`, `pyarrow`, `huggingface_hub` |
| Regroupement des sujets | `scikit-learn` (regroupement hiérarchique sur distance cosinus) |
| Recherche par le sens dans l'application | Produit matriciel `numpy` sur les vecteurs des 6 derniers mois |
| Écriture des annotations | API de GitHub (`PyGithub`) |
| Interface | `streamlit` multipage, `plotly` |

Pas de base de données à administrer. Si le volume dépasse 150 000 fiches actives, on envisagera une base vectorielle hébergée gratuite ; pas avant.

### 3.4 Le dédoublonnage

Trois filets successifs : URL canonique identique ; titre quasi identique dans les 72 heures ; distance entre vecteurs sous un seuil réglable. On conserve la fiche de la source la plus proche du fait (ancrage LOCAL d'abord), et on incrémente son champ `reprises`.

### 3.5 Plafond par aire à la collecte (ajout du Sprint 1)

Pour respecter la règle des 30 % de L1 (section 9.3) sur les articles, la collecte plafonne le nombre d'articles retenus par aire de source et par jour (réglage dans `config/seuils.yaml`). Les articles écartés par ce plafond sont comptés dans le Miroir.

---

## 4. Le modèle de données

### 4.1 Les fiches (Hugging Face, un fichier par mois)

| Champ | Origine |
|---|---|
| `id` (forme `F-AAAAMMJJ-NNNN`), `url`, `titre_original`, `langue`, `date_publication`, `date_collecte` | Collecte |
| `source_id`, `aire_source`, `ancrage`, `lien_pouvoir` | Registre des sources |
| Tous les champs de la passe 2 (`config/consignes/passe2_v1.txt`) | Classement |
| `modele`, `version_consigne` | Classement |
| `groupe_sujet`, `reprises` | Regroupement, dédoublonnage |
| `corrige_par_humain` (oui, non), `etiquettes_avant_correction` | Annotations |

Les rejets de la passe 1 sont stockés à part : `url`, `titre`, `source_id`, `motif`, `date`.

### 4.2 Les objets (dépôt GitHub, dossier `objets/`)

Un fichier par type, au format CSV quand la structure est plate, JSONL sinon. Les champs sont ceux de L1, section 10.

| Fichier | Une ligne = |
|---|---|
| `axes.csv` | Un axe (code, pôles, statut, marqueurs par langue) |
| `positions_axes.csv` | Axe × zone × voix × mois (position, intensité, fiches) |
| `tensions_libres.csv` | Un groupe candidat (pôles proposés, décomptes, aires, statut, décision) |
| `technologies.csv` | Une technologie (nom, variantes, classe de lenteur, TRL) |
| `horloge.csv` | Technologie × zone × mois (G, A, saut, fiches) |
| `precipitations.jsonl` | Une précipitation, avec une entrée par zone et par mois |
| `tendances.jsonl`, `mutations.jsonl`, `cas.jsonl`, `hypotheses.jsonl` | Un objet |
| `matrice.csv` | Zone × dimension × trimestre (autonomie, levier, tendances, confiance, indicateurs, lecture contradictoire) |
| `acteurs.csv`, `infrastructures.csv`, `flux.csv` | Une entité |
| `relations.csv` | Origine, relation, destination, fiches, date |
| `sujets_suivis.csv` | Un sujet épinglé |

**Historique** : chaque écriture est un enregistrement Git daté. En complément, le 1er du mois, tout le dossier est copié dans `photos/AAAA-MM/`. Le mode « comparer » lit deux de ces dossiers.

### 4.3 Les réglages (dossier `config/`)

`sources.csv`, `zones_pays.csv`, `technologies.csv`, `materiaux.csv`, `seuils.yaml` (tous les seuils chiffrés de L1 : quotas d'aires, détection des tensions, statuts de précipitation, création des objets), `budget.yaml`, `modeles.yaml` (quel modèle pour quelle tâche), `consignes/` (les textes de L2 et de L3, un fichier par consigne, avec un numéro de version).

---

## 5. Le registre des sources

Fichier unique `config/sources.csv`.

| Colonne | Valeurs |
|---|---|
| `id`, `nom`, `url` | – |
| `type` | RSS, PAGE, API, GDELT, PERSONNE, SERIE |
| `langue` | Code ISO |
| `pays`, `aire_source` | Code ISO (ou `EU` pour les institutions européennes) ; code de zone (L1) |
| `ancrage` | LOCAL, DIASPORA, CORRESPONDANT, INTERNATIONAL |
| `lien_pouvoir`, `proprietaire` | Codes de L1, section 7.3 ; texte libre |
| `lentilles_attendues` | Codes, séparés par des points-virgules |
| `frequence` | 6h, jour, semaine, mois |
| `fiabilite` | 1 à 3 : 3 = cite ses sources et corrige ses erreurs ; 2 = par défaut ; 1 = erreurs factuelles constatées par Gabriel. La note porte sur l'exactitude, pas sur l'orientation. Aucune agence de notation externe n'est utilisée. |
| `actif`, `date_ajout`, `remarque` | – |
| `articles_30j`, `taux_pertinence_30j`, `dernier_succes` | **Calculés**, en lecture seule |

Une source qui échoue 7 jours de suite est signalée ; au bout de 30 jours, elle est désactivée automatiquement, avec une ligne au journal.

---

## 6. Présentation et interrogation

L'annexe A (`04-presentation-interrogation.md`, sections 1 à 4) fait foi pour la description des écrans. Ce chapitre tranche ses points ouverts (sa section 5) et l'amende.

### 6.1 Décisions sur les points ouverts

| Point ouvert | Décision |
|---|---|
| Liste des axes et détection des tensions | L1, section 4 : 11 axes validés, 3 observés, seuils en 4.3 |
| Échelles des précipitations | L1, section 5 : O0 à O5, B0 à B5, sept types de catalyseur, six statuts |
| Dimensions et méthode de la matrice | L1, section 8 : 13 dimensions, deux notes par case, pas de score global |
| Zones et codes | L1, section 7.1 : 12 zones et GLO. **Le code JP devient JK ; MO est scindé en GO et MO ; OC est ajouté.** |
| Boutons de recul | Section 6.4 ci-dessous |
| v2 ou v3 | Section 6.2 ci-dessous |

### 6.2 Périmètre de la v2 et de la v3

| Écran | v2 | Simplification en v2 | v3 |
|---|---|---|---|
| Cockpit | Oui | Les blocs apparaissent au fil des sprints | – |
| Baromètre des tensions | Oui | Vue axes, vue tensions émergentes, fiche tension. Une seule voix par zone au départ. | Tableau croisé, deuxième voix |
| Zones de précipitation | Oui | Nuage de bulles, traînée sur 6 mois, fiche | Traînée sur 24 mois |
| Horloge des technologies | Oui | Courbe des attentes par zone ; tableau attentes × adoption ; alertes | Couloirs des classes de lenteur, frise détaillée |
| Matrice de puissance, fiche zone | Oui | Matrice, fiche zone avec SWOT, carte du monde simple colorée par dimension | Comparateur radar, graphe des dépendances |
| Tendances et mutations | Oui | Un seul écran : cartes de tendance, galerie de mutations | Vue rivière |
| Galerie des solutions | Oui | Cartes de cas, tri, validation | – |
| Synthèses et journal d'hypothèses | Oui | Pages de lecture ; tableau des hypothèses | – |
| Miroir des angles morts | Oui (Sprint 1) | Répartition par aire et langue, zones muettes, vos lectures | Suggestions de sources |
| Assistant contextuel | Oui | Panneau latéral, réponses depuis la base, boutons de recul | Mode web élargi dans l'application |
| Demande de dossier | Oui, simplifiée | Lancée depuis GitHub Actions avec un formulaire ; résultat affiché dans Synthèses | Formulaire dans l'application |
| Carte du monde à couches | Partiel | Une carte colorée (dimension de puissance ou position sur un axe) | Couches infrastructures, arcs de flux, fond Todd, événements géolocalisés |
| Passerelles (graphe) | Non | Les relations `utilise` et `migre_vers` sont **enregistrées dès la v2** | Affichage du réseau |
| Monnaies et richesses | Non | Les séries sont **collectées dès la v2** et lues par les agents | Écran dédié |
| Sociétés et modes de vie | Non | Idem | Écran dédié |
| Curseur de temps global | Partiel | Mode « comparer » entre deux photographies mensuelles | Curseur continu |

### 6.3 Amendements à la grammaire visuelle

- **Lentilles** : les 7 couleurs correspondent à TEC, INF, MON, PUI, SOC, SOL, MIL. Le Miroir n'a pas de couleur.
- **Rebond** : pastille de R0 à R3, avec la lettre S (suffisance) ou X (surconsommation) ; pastille vide pour R?.
- **Notes absentes** : toute valeur « non noté » (G?, A?, R?, case grise de la matrice) est affichée comme telle, jamais masquée ni remplacée par une valeur par défaut.
- **Indicateur de diversité** dans l'en-tête de toutes les pages : « 9 aires · dominante EU 27 % ». Rouge si une règle de L1, section 9.3, est enfreinte.
- **Lien au pouvoir** : une icône discrète à côté de chaque source citée, la même pour toutes les valeurs autres que INDEPENDANT, avec le détail au survol.

### 6.4 Liste définitive des boutons de recul

| Bouton | Consigne ajoutée à la question |
|---|---|
| Vu depuis… (aire au choix) | Réponds à partir des seules sources de l'aire choisie ; dis ce qui manque si elles sont moins de 3 |
| Quels effets rebond ? | Types DIR, IND, ECO, SYS, TRA ; nature SUF ou SUR ; garde-fous |
| Qui paie, qui gagne ? | Gagnants et perdants nommés, par zone |
| Quelles tensions en jeu ? | Axes, pôles, zones, et tentatives de dépassement |
| À quel niveau de l'iceberg ? | N1 à N4, et ce qu'il faudrait pour descendre d'un niveau |
| Quel levier de Meadows ? | Numéro, justification, levier plus profond envisageable |
| Comparer avec… | Autre zone ou autre photographie mensuelle |
| Lecture par… | Applique la question opérationnelle associée à l'auteur (L1, section 9.2) |
| Contre-argument | La meilleure objection, depuis l'aire la moins citée |
| Qu'est-ce qui pourrait précipiter ici ? | Offre, besoin, catalyseur attendu |
| Approfondir | Prépare une demande de dossier |

### 6.5 L'assistant

Règles de l'annexe A, section 4.3, et règles communes de L3, section 1. Précisions techniques :
- la question est transformée en vecteur par Albert ; recherche parmi les fiches des 6 derniers mois (filtres de l'écran appliqués), plus tous les objets et les synthèses ;
- 30 fiches au plus sont transmises au modèle, avec l'objet ouvert à l'écran ;
- chaque réponse affiche la confiance et la répartition des aires des sources citées ;
- **modèle** : Sonnet 5.5 par défaut, Opus sur demande ; **plafond** de 150 questions par mois, réglable (`config/budget.yaml`).

### 6.6 Les annotations

Depuis toute fiche ou tout objet, en mode édition : corriger une étiquette, ajouter une note, valider, observer ou rejeter un candidat, suivre un sujet, créer une hypothèse. Chaque action ajoute une ligne à `annotations/AAAA-MM.csv` (qui, quand, quoi, valeur avant, valeur après). La tâche de nuit applique ces lignes. Les fiches corrigées alimentent le contrôle continu de L2, section 6.5.

---

## 7. Exigences non fonctionnelles

| Exigence | Traduction |
|---|---|
| **Traçabilité** | Tout élément affiché mène en deux clics aux fiches, et de là à l'URL d'origine. Toute sortie d'agent conserve la liste des fiches reçues, le modèle et la version de la consigne. |
| **Droits d'auteur** | Aucun texte d'article sur disque après le classement. Résumés de 900 caractères au plus. |
| **Secrets** | Clés Albert, Anthropic, Hugging Face et GitHub dans les secrets de GitHub Actions et de Streamlit. Jamais dans le code ni dans le dépôt. Un contrôle automatique refuse tout enregistrement contenant une chaîne ressemblant à une clé. |
| **Journal d'exécution** | `journal/executions.csv` : tâche, début, fin, articles vus, classés, rejetés, erreurs, coût. Affiché dans une page « État du système », avec une alerte si la dernière exécution date de plus de 2 jours. |
| **Reprise après erreur** | Chaque étape note ce qu'elle a traité. Une relance reprend là où elle s'est arrêtée. Une source en panne ne bloque pas les autres. Albert indisponible : file d'attente de 24 heures, puis Haiku. |
| **Suivi des coûts** | `journal/couts.csv` : une ligne par appel à Claude (tâche, modèle, tokens en entrée et en sortie, coût). Avant chaque appel, le cumul du mois est comparé à `budget.yaml`. À 50 $ : alerte (ouverture d'un ticket GitHub, qui envoie un courriel). À 60 $ : seuls A1 et A2 continuent. **Un plafond de dépense de 60 $ est aussi fixé dans la console Anthropic** : c'est le seul vrai verrou. |
| **Qualité du classement** | Taux de JSON valide, taux de recours à Haiku, taux de OUI en passe 1 et accord avec les corrections, suivis chaque semaine sur la page « État du système ». |
| **Désoccidentalisation** | Les cinq règles de L1, section 9.3, calculées chaque nuit, affichées partout. |
| **Versions des consignes** | Toute modification d'une consigne change son numéro. Les fiches gardent le numéro qui les a produites. |
| **Sobriété** | L'affichage ne déclenche ni collecte ni appel à un modèle, hors assistant. Les pages se chargent en moins de 5 secondes. |
| **Citation de GDELT** | « The GDELT Project » avec un lien vers gdeltproject.org, affiché dans l'application. |

---

## 8. Le plan des sprints

Chaque test d'acceptation est une action que Gabriel peut faire lui-même dans un navigateur.

### Sprint 1 – Registre des sources et vérifications (fait le 14 novembre 2026)

Contenu : structure du dépôt ; fusion des 7 fichiers RSS dans `sources.csv` ; audit des flux ; ajout de 30 à 50 sources non occidentales ; vérifications de la section 1 ; carnet Colab qui passe les 20 exemples de L2 dans un modèle d'Albert ; première page « Miroir » calculée sur le registre.

Tests d'acceptation :
1. J'ouvre `config/sources.csv` dans GitHub : chaque ligne a une aire, une langue, un ancrage et un lien au pouvoir.
2. La page Miroir affiche la part de chaque aire dans les sources actives, et aucune ne dépasse 30 %.
3. J'ajoute une ligne au fichier depuis GitHub ; le lendemain, la source apparaît dans le Miroir.
4. Le carnet Colab affiche, pour les 20 exemples, la fiche produite par Albert à côté de la mienne.
5. Un fichier `docs/verifications.md` répond aux 4 points à vérifier.

### Sprint 2 – Collecte continue et stockage

Contenu : tâche `collecte` (sans classement) ; extraction du texte ; dédoublonnage ; plafond par aire ; stockage sur Hugging Face (privé) ; journal ; page « État du système » ; requêtes GDELT pour renforcer les aires faibles (CN, JK, MO).

Tests d'acceptation :
1. Sans que j'ouvre l'application, de nouveaux articles apparaissent toutes les 6 heures pendant 3 jours.
2. La page État du système montre, pour chaque exécution, le nombre d'articles vus et les sources en erreur.
3. Je désactive une source dans le fichier ; elle n'est plus collectée le lendemain.
4. Une dépêche reprise par plusieurs sites n'apparaît qu'une fois, avec son nombre de reprises.
5. Je cherche dans le stockage : aucun texte complet d'article n'y figure.

### Sprint 3 – Évaluation des modèles, puis classement

Contenu : jeu de référence de 100 articles (avec réponses acceptables) ; comparaison des modèles (L2, section 6) ; choix ; passes 1 et 2 ; contrôles automatiques ; vecteurs ; regroupement des sujets ; page « Fiches » avec filtres et correction d'étiquettes.

Tests d'acceptation :
1. Un tableau compare les modèles champ par champ, avec coût et durée ; le modèle retenu atteint les seuils de L2.
2. J'ouvre une fiche : résumé en français, étiquettes, lien vers l'article.
3. Je filtre par lentille MIL et par aire AF : la liste change en conséquence.
4. Je corrige une étiquette ; le lendemain, la fiche porte ma correction et l'ancienne valeur est conservée.
5. Le taux de OUI en passe 1 se situe entre 25 et 35 % sur une semaine.
6. Le coût de la semaine apparaît dans `journal/couts.csv`.

### Sprint 4 – Objets et modules : tensions, précipitations, horloge

Contenu : calcul hebdomadaire du baromètre et des tensions libres ; volumes GDELT ; agents A3, A4, A5 ; écrans Tensions, Précipitations, Horloge ; fiches objet ; annotations (valider, rejeter). En fin de sprint, la v1 est déplacée dans `v1/`.

Tests d'acceptation :
1. L'écran Tensions affiche les 11 axes avec, pour chacun, les zones positionnées et les fiches qui le justifient.
2. Une tension candidate m'est présentée avec ses deux pôles, ses décomptes et 5 extraits ; je clique « rejeter », elle disparaît et ne revient pas.
3. L'écran Précipitations affiche au moins 5 bulles ; je clique sur l'une : 3 preuves d'offre et 3 de besoin, toutes cliquables.
4. L'écran Horloge montre au moins une technologie placée différemment dans deux zones.
5. Aucune note n'apparaît sans fiche à l'appui ; les notes absentes s'affichent « non noté ».

### Sprint 5 – Synthèses, curateur, assistant, journal, galerie, mutations

Contenu : agents A1, A2, A6, A10 ; écrans Synthèses, Journal d'hypothèses, Galerie, Tendances et mutations ; assistant et boutons de recul ; sujets suivis ; cockpit (première version).

Tests d'acceptation :
1. Lundi matin, une synthèse de 900 mots au plus est en ligne, avec la relecture du contradicteur dessous.
2. Je clique sur une affirmation de la synthèse : j'arrive aux fiches, puis à l'article.
3. Ma file de validation contient 10 éléments au plus, et je la vide en moins de 45 minutes.
4. Je pose une question à l'assistant sur la fiche ouverte : la réponse cite des fiches et affiche la répartition des aires.
5. Je pose une question hors de la base : l'assistant dit qu'il n'a pas assez d'éléments.
6. J'inscris une hypothèse avec une échéance ; elle apparaît au journal avec ma confiance initiale.

### Sprint 6 – Matrice, grand recul, lecture croisée, dossiers, bilan

Contenu : séries lentes ; agents A7, A8, A9 ; écran Matrice et fiche zone ; carte simple ; demande de dossier ; photographies mensuelles et mode comparer ; cockpit complet ; bilan des coûts et de la qualité ; liste des sujets pour la v3.

Tests d'acceptation :
1. La matrice affiche 12 zones et 13 dimensions ; chaque case notée montre ses indicateurs et leurs sources ; les cases sans preuve sont grises.
2. Aucun classement général des zones n'apparaît nulle part.
3. Le grand recul du mois est en ligne et commente mes hypothèses.
4. Une lecture croisée présente un même sujet vu par 3 aires, avec les mots d'origine.
5. Je lance un dossier depuis GitHub ; il apparaît dans Synthèses quelques heures plus tard, avec son coût.
6. Le cockpit se lit en 5 minutes et tous ses blocs sont remplis.
7. Le coût du mois écoulé est inférieur à 60 $, et un document compare ce coût aux estimations.

---

## 9. Mode d'emploi de maintenance

Tout se fait depuis le site de GitHub, sans rien installer.

| Je veux… | Je fais… |
|---|---|
| **Ajouter une source** | J'ouvre `config/sources.csv`, je clique sur le crayon, j'ajoute une ligne (nom, URL, type, langue, pays, aire, ancrage, lien au pouvoir), j'enregistre. L'audit se relance tout seul. |
| **Désactiver une source** | Même fichier : `actif` passe à `non`. |
| **Corriger une étiquette** | Dans l'application, en mode édition : bouton « Annoter » de la fiche. |
| **Valider ou rejeter un candidat** | Dans l'application : file de validation du cockpit. |
| **Relancer une tâche** | Onglet Actions du dépôt, je choisis la tâche, « Run workflow ». |
| **Savoir pourquoi une tâche a échoué** | Page État du système de l'application ; sinon, onglet Actions, clic sur la ligne rouge. Je peux copier le message d'erreur dans Claude. |
| **Changer un seuil** | `config/seuils.yaml` : chaque ligne est commentée en français. |
| **Changer de modèle pour une tâche** | `config/modeles.yaml`. |
| **Modifier une consigne** | Fichier correspondant dans `config/consignes/` ; j'augmente son numéro de version. |
| **Ajouter une technologie ou un axe** | `config/technologies.csv` ; pour un axe, par l'écran Tensions (pour garder l'historique). |
| **Changer le plafond de dépense** | `config/budget.yaml`, **et** la console Anthropic. |
| **Demander un dossier** | Onglet Actions, tâche `dossier`, je remplis la question, le périmètre et la profondeur. |
| **Revenir en arrière après une erreur** | Onglet « History » du fichier dans GitHub, puis restauration de la version précédente. |
| **Changer une clé** | Paramètres du dépôt, « Secrets and variables » ; et paramètres de l'application Streamlit. |

---

## Points à tester

1. Une collecte à blanc de 48 heures sur les flux qui fonctionnent, pour connaître le volume réel d'articles par jour.
2. La mémoire consommée par l'application avec 6 mois de vecteurs chargés.
3. L'écriture d'une annotation depuis l'application vers GitHub, de bout en bout.
4. L'alerte de budget : la déclencher volontairement avec un seuil à 1 $.
5. La restauration d'un fichier d'objets après une erreur volontaire.
