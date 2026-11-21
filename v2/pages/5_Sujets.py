"""Sujets : articles regroupés par le sens, quelle que soit leur langue (Sprint 3)."""
import streamlit as st

import importlib

import commun

importlib.reload(commun)  # Streamlit Cloud garde parfois l'ancienne version de commun.py en memoire
from commun import NOMS_AIRES, charger_sujets

st.set_page_config(page_title="Sujets", page_icon="◈", layout="wide")
st.title("Sujets des 14 derniers jours")
st.markdown(
    "Chaque nuit, chaque article jugé pertinent reçoit une **empreinte de sens**, calculée par un modèle "
    "qui comprend une centaine de langues (bge-m3, sur Albert). Deux articles dont les empreintes se ressemblent "
    "parlent du même sujet, même s'ils sont écrits l'un en chinois, l'autre en portugais. Un **sujet** réunit "
    "au moins 3 articles des 14 derniers jours.\n\n"
    "- Un sujet repris par des sources de **plusieurs aires du monde** est un sujet qui **circule** : "
    "comparez comment chacune le raconte.\n"
    "- Un sujet couvert par une **seule aire** est peut-être un **angle mort** pour les autres."
)
if st.button("Recharger"):
    charger_sujets.clear()
g, info = charger_sujets()
if g is None:
    st.info(info)
    st.stop()

c1, c2 = st.columns(2)
vue = c1.radio("Afficher", ["Sujets qui circulent entre les aires", "Sujets vus d'une seule aire"], horizontal=False)
q = c2.text_input("Chercher dans les titres", "")
if vue.startswith("Sujets qui circulent"):
    min_aires = st.slider("Couverts par des sources d'au moins … aires du monde", 2, 12, 3,
                          help="Aire de la source : d'où vient le média (Europe, Chine, Afrique subsaharienne…), "
                               "pas le pays dont parle l'article.")
    v = g[g["nb_aires_source"] >= min_aires]
else:
    v = g[g["nb_aires_source"] == 1].sort_values("taille", ascending=False)
if q:
    v = v[v["titres"].str.contains(q, case=False, regex=False)]
st.caption(f"{len(v)} sujets sur {len(g)}.")

for _, r in v.head(60).iterrows():
    with st.container(border=True):
        st.markdown(f"**{r['titre']}**")
        aires = ", ".join(NOMS_AIRES.get(a, a) for a in r["aires_source"].split(";"))
        st.caption(f"{r['taille']} articles · {r['nb_sources']} sources · {r['nb_aires_source']} aires : {aires} · "
                   f"langues {r['langues']} · lentilles {r['lentilles']} · du {r['premier'][:10]} au {r['dernier'][:10]}")
        with st.expander("Titres"):
            for t in r["titres"].split(" | "):
                st.write("–", t)
