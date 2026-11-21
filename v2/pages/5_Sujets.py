"""Sujets : articles regroupés par le sens, quelle que soit leur langue (Sprint 3)."""
import streamlit as st

from commun import NOMS_AIRES, charger_sujets

st.set_page_config(page_title="Sujets", page_icon="◈", layout="wide")
st.title("Sujets des 14 derniers jours")
st.caption("Articles regroupés par la proximité de leur sens (vecteurs bge-m3), quelle que soit leur langue. "
           "En tête : les sujets traités par le plus d'aires différentes.")
if st.button("Recharger"):
    charger_sujets.clear()
g, info = charger_sujets()
if g is None:
    st.info(info)
    st.stop()

c1, c2 = st.columns(2)
min_aires = c1.slider("Nombre minimal d'aires de source", 1, 12, 3)
q = c2.text_input("Chercher dans les titres", "")
v = g[g["nb_aires_source"] >= min_aires]
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
