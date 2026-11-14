"""Miroir des angles morts - Sprint 1 : calcule sur le registre des sources.

A partir du Sprint 3, les memes calculs porteront sur les articles classes."""
import pandas as pd
import plotly.express as px
import streamlit as st

from commun import (NOMS_AIRES, ORDRE_AIRES, charger_audit, charger_seuils,
                    charger_sources, indicateur_diversite, parts_par_aire,
                    regles_diversite)

st.set_page_config(page_title="Miroir · Innovation Radar", page_icon="◈", layout="wide")

sources = charger_sources()
seuils = charger_seuils()
audit = charger_audit()

st.title("Miroir des angles morts")
st.caption("Sprint 1 : calculé sur le registre des sources. Au Sprint 3, il portera sur les articles lus.")

# --- Filtre : actives seulement, ou seulement celles dont le flux fonctionne
base = sources[sources["actif"].str.lower() == "oui"].copy()
choix = ["Toutes les sources actives"]
if audit is not None:
    choix.append("Seulement les flux qui fonctionnent (dernier audit)")
mode = st.radio("Périmètre", choix, horizontal=True)
if audit is not None and mode != choix[0]:
    ok = set(audit.loc[audit["statut"] == "OK", "id"])
    base = base[base["id"].isin(ok)]

parts = parts_par_aire(base)
texte, visibles, dominante, part_dom = indicateur_diversite(parts, seuils["diversite"]["seuil_aire_visible"])
st.subheader(texte)
st.caption(f"{len(base)} sources · une aire « compte » au-delà de "
           f"{seuils['diversite']['seuil_aire_visible']:.0%} des sources")

# --- Regles de diversite (L1, section 9.3)
st.markdown("#### Règles de diversité")
regles = regles_diversite(base, seuils)
tableau = pd.DataFrame(regles, columns=["Règle", "Valeur", "Respectée"])
tableau["Respectée"] = tableau["Respectée"].map({True: "✅ oui", False: "❌ non"})
st.dataframe(tableau, hide_index=True, width="stretch")
st.caption("Ces règles s'appliqueront aux articles classés. Sur le registre, elles indiquent "
           "les aires où il manque des sources.")

# --- Repartition par aire
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Par aire de source")
    df_aires = pd.DataFrame({"aire": ORDRE_AIRES, "part": parts.values,
                             "nom": [NOMS_AIRES[a] for a in ORDRE_AIRES]})
    fig = px.bar(df_aires, x="part", y="aire", orientation="h", hover_name="nom",
                 text=df_aires["part"].map("{:.0%}".format))
    fig.add_vline(x=seuils["diversite"]["part_max_une_aire"], line_dash="dash",
                  annotation_text="plafond 30 %")
    fig.update_layout(yaxis={"categoryorder": "array", "categoryarray": ORDRE_AIRES[::-1]},
                      xaxis_tickformat=".0%", height=420, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width="stretch")
with col2:
    st.markdown("#### Par langue")
    langues = base["langue"].value_counts().reset_index()
    langues.columns = ["langue", "sources"]
    fig2 = px.bar(langues, x="sources", y="langue", orientation="h", text="sources")
    fig2.update_layout(yaxis={"categoryorder": "total ascending"}, height=420,
                       margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, width="stretch")

col3, col4 = st.columns(2)
with col3:
    st.markdown("#### Par lien au pouvoir")
    st.caption("Noté de la même façon pour toutes les sources, occidentales comprises.")
    st.dataframe(base["lien_pouvoir"].value_counts().rename("sources"), width="stretch")
with col4:
    st.markdown("#### Par ancrage")
    st.dataframe(base["ancrage"].value_counts().rename("sources"), width="stretch")

# --- Zones muettes
st.markdown("#### Aires sans source ou presque")
muettes = [f"{a} ({NOMS_AIRES[a]}) : {int((base['aire_source'] == a).sum())} source(s)"
           for a in ORDRE_AIRES if a != "GLO" and (base["aire_source"] == a).sum() < 3]
st.write("\n".join(f"- {m}" for m in muettes) if muettes else "Aucune.")

# --- Etat des flux
st.markdown("#### État des flux (dernier audit)")
if audit is None:
    st.info("Pas encore d'audit. Lancez la tâche « Audit des sources » dans l'onglet Actions du dépôt GitHub.")
else:
    st.caption(f"Audit du {audit['date_audit'].max()}")
    st.dataframe(audit["statut"].value_counts().rename("sources"), width="stretch")
    en_echec = audit[audit["statut"] != "OK"][["nom", "aire_source", "statut", "message", "url"]]
    with st.expander(f"Flux à corriger ({len(en_echec)})"):
        st.dataframe(en_echec, hide_index=True, width="stretch")

# --- Registre complet
with st.expander("Voir le registre complet"):
    st.dataframe(sources, hide_index=True, width="stretch")
