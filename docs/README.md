# Documents du projet Innovation Radar v2

## Les documents de conception

Ils sont dans ce dossier (copie du projet claude.ai « Netvibes de l'innovation » au 14 novembre 2026). En cas de modification, mettez à jour les deux. Les consignes de classement de L2 et les 20 exemples de référence sont dans `config/consignes/` et `tests/`.

| Fichier | Contenu |
|---|---|
| `decisions-sprint0.md` | Décisions validées : il l'emporte sur les autres |
| `L1-grille.md` | La grille d'analyse : tous les codes |
| `L2-classement.md` | Les consignes de classement (Albert, Haiku) |
| `L3-agents.md` | Les consignes des agents d'analyse |
| `L5-cahier-des-charges.md` | Architecture, données, sprints, tests d'acceptation |
| `04-presentation-interrogation.md` | Description des écrans (annexe de L5) |

## Les documents du Sprint 1

- `verifications.md` : les quatre vérifications préalables.
- `journal-sprint1.md` : les choix faits pendant le sprint et le constat principal.

## Mise en route du Sprint 2 (collecte automatique)

1. **Fusionner** les demandes `v2-sprint1` puis `v2-sprint2` dans `main` (les tâches planifiées ne tournent que depuis `main`).
2. **Hugging Face** : créer un compte sur huggingface.co (gratuit). Menu de votre profil > Settings > Access Tokens > « Create new token », type **Write**, nom `innovation-radar`. Copier le jeton (il commence par `hf_`).
3. **GitHub** : dépôt > Settings > Secrets and variables > Actions > « New repository secret ». Nom : `HF_TOKEN`, valeur : le jeton.
4. **Premier passage** : onglet Actions > « Collecte » > Run workflow. Durée : 5 à 15 minutes. Le jeu de données privé `<votre-identifiant>/innovation-radar-fiches` est créé tout seul.
5. **Streamlit** : à la création de l'application (fichier principal `v2/Accueil.py`), ou plus tard dans Settings > Secrets, coller :
   ```
   HF_TOKEN = "hf_..."
   ```
   Un second jeton en lecture seule (type **Read**) suffit ici et limite les risques.
6. Ouvrir la page **État du système**.

Ne jamais coller un jeton dans la conversation avec Claude, dans un fichier du dépôt ou dans un carnet Colab partagé.

## Séries chiffrées (Sprint 2 bis)

La tâche « Series » tourne chaque soir (21 h 37 UTC). Elle lit les séries listées dans `config/series.csv` (une ligne par série) pour les pays de `config/series_pays.yaml`, et les range dans le stockage Hugging Face (`series/donnees.parquet`). La page « Marchés et séries » de l'application les affiche ; l'état de chaque série est dans `journal/series_etat.csv`.

Sources sans clé : Banque centrale européenne (changes), FMI (réserves de change, COFER), Banque mondiale, Our World in Data, INSEE.

**Bourses et matières premières (Stooq) : une clé gratuite à demander une fois.**
1. Ouvrir https://stooq.com/q/d/?s=spy.us&get_apikey et recopier le code de l'image (captcha).
2. En bas de la page, le lien « Download data in .csv file » contient `apikey=…` : copier la valeur après le signe égal.
3. GitHub : Settings > Secrets and variables > Actions > New repository secret. Nom : `STOOQ_API_KEY`.
4. Onglet Actions > « Series » > Run workflow.

Stooq est gratuit pour un usage non commercial. Certains symboles de bourses (Jakarta, Istanbul, Johannesburg, Moscou) sont à vérifier : l'état des séries le dira au premier passage, et je les corrigerai.
