"""Innovation Radar v2 - page d'accueil (sera le cockpit a partir du Sprint 5)."""
import streamlit as st

from commun import charger_seuils, charger_sources, indicateur_diversite, parts_par_aire

st.set_page_config(page_title="Innovation Radar v2", page_icon="◈", layout="wide")

sources = charger_sources()
actives = sources[sources["actif"].str.lower() == "oui"]
seuils = charger_seuils()
texte, *_ = indicateur_diversite(parts_par_aire(actives), seuils["diversite"]["seuil_aire_visible"])

st.title("◈ Innovation Radar v2")
st.caption(f"Diversité des sources actives : {texte}")

st.markdown(
    """
Version 2 en construction. **Sprint 1 : le registre des sources.**

- **Miroir** (menu de gauche) : d'où viennent les sources, dans quelles langues, avec quel lien au pouvoir.
- Le registre se modifie dans `config/sources.csv`, depuis le site de GitHub.
- L'état des flux est mis à jour chaque lundi par la tâche « Audit des sources » (onglet Actions du dépôt).

Les autres écrans arrivent aux sprints suivants (voir `docs/`).
"""
)
c1, c2, c3 = st.columns(3)
c1.metric("Sources actives", len(actives))
c2.metric("Langues", actives["langue"].nunique())
c3.metric("Pays", actives.loc[actives["pays"] != "", "pays"].nunique())
