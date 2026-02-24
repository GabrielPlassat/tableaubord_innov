# ◈ Innovation Radar

Tableau de bord prospectif — Sprints 1 & 2

## Déploiement en 5 minutes sur Streamlit Cloud

### 1. Mettre le projet sur GitHub

1. Va sur [github.com](https://github.com) et connecte-toi
2. Clique sur **New repository**
3. Nomme-le `innovation-radar`, coche **Public**, clique **Create**
4. Sur la page du repo, clique **uploading an existing file**
5. Glisse-dépose **tous les fichiers** (app.py, requirements.txt, et le dossier `data/`)

### 2. Déployer sur Streamlit Cloud

1. Va sur [share.streamlit.io](https://share.streamlit.io) et connecte-toi avec GitHub
2. Clique **New app**
3. Sélectionne ton repo `innovation-radar`
4. **Main file path** : `app.py`
5. Clique **Deploy** — ton app sera live en 2 minutes ✓

---

## Structure des fichiers

```
innovation-radar/
├── app.py                  ← Application principale
├── requirements.txt        ← Bibliothèques Python
└── data/
    ├── energie.csv         ← Données énergie (à éditer)
    ├── economie.csv        ← Données économie (à éditer)
    ├── projets.csv         ← Projets + positionnement Gartner
    ├── personnes.csv       ← Personnes référentes
    └── signaux_faibles.csv ← Signaux faibles curatés
```

## Comment mettre à jour les données

**Depuis GitHub directement** (sans coder) :
1. Va dans ton repo sur github.com
2. Clique sur le fichier CSV à modifier (ex: `data/projets.csv`)
3. Clique sur le crayon ✏️ en haut à droite
4. Modifie, ajoute des lignes
5. Clique **Commit changes**
→ L'app se met à jour automatiquement en 30 secondes

## Onglets disponibles

| Onglet | Contenu | Données |
|--------|---------|---------|
| ⚡ Énergie | Prix, production, variation | `energie.csv` |
| 📈 Économie | PIB, croissance, inflation | `economie.csv` |
| 🔬 Projets & TRL | Courbe de Gartner interactive | `projets.csv` |
| 👤 Veille Personnes | Profils référents par courant | `personnes.csv` |
| 📡 Signaux Faibles | Signaux curatés avec tags | `signaux_faibles.csv` |

## Sprint 3 (à venir)
- Connexion automatique Our World in Data (énergie)
- Connexion Banque Mondiale API (économie)
- Flux RSS automatiques (personnes)
