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
