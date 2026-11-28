"""Sujets : articles regroupés par le sens, quelle que soit leur langue (Sprint 3)."""
import streamlit as st

import importlib

import commun

importlib.reload(commun)  # Streamlit Cloud garde parfois l'ancienne version de commun.py en memoire
import json

from commun import NOMS_AIRES, charger_etiquettes, charger_sujets

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
    charger_etiquettes.clear()

AXES = {"T01": "urgence écologique ↔ urgence sociale", "T02": "croissance ↔ autres finalités",
        "T03": "technique ↔ sobriété", "T04": "marché ↔ État stratège", "T05": "propriété ↔ communs",
        "T06": "performance ↔ robustesse", "T07": "ordre universel ↔ monde pluriel",
        "T08": "interdépendance ↔ souveraineté", "T09": "accomplissement de soi ↔ appartenances",
        "T10": "centres ↔ périphéries", "T11": "contrôle ↔ libertés", "T12": "automatisation ↔ travail humain",
        "T13": "générations installées ↔ entrantes", "T14": "natalisme ↔ émancipation"}
POLES = {"A": "pôle A", "B": "pôle B", "LES_DEUX": "les deux", "DEPASSEMENT": "dépassement"}

et, info_et = charger_etiquettes()
if et is not None and len(et):
    st.subheader("Lus par les agents cette semaine")
    st.caption(f"{len(et)} sujets étiquetés par Opus le {et['date_etiquetage'].iloc[0]} : comment chaque aire "
               "raconte le sujet, ce qu'une aire dit et que les autres taisent, les axes de tension en jeu. "
               "Les identifiants entre crochets renvoient aux fiches.")
    axes_vus = sorted({c for c in et["axe1"].dropna() if c})
    choix_axe = st.selectbox("Axe de tension", ["Tous"] + axes_vus, format_func=lambda c: c if c == "Tous" else f"{c} {AXES.get(c, '')}")
    vue_et = et if choix_axe == "Tous" else et[et["axes"].str.contains(f'"{choix_axe}"', regex=False)]
    for _, r in vue_et.iterrows():
        with st.container(border=True):
            st.markdown(f"**{r['titre']}**")
            st.caption(f"{r['taille']} articles · aires {r['aires_source']} · lentille {r['lentille_principale']} · "
                       f"{r['iceberg']} · précipitation {r['precipitation']} · confiance {r['confiance']}")
            st.write(r["resume"])
            for l in json.loads(r["lectures_par_aire"] or "[]"):
                st.markdown(f"- **{NOMS_AIRES.get(l.get('aire'), l.get('aire'))}** : {l.get('lecture', '')}")
            if r["angle_mort"]:
                st.markdown(f"*Angle mort* : {r['angle_mort']}")
            for a in json.loads(r["axes"] or "[]"):
                par = ", ".join(f"{p.get('aire')} {POLES.get(p.get('pole'), p.get('pole'))}" for p in a.get("par_aire", []))
                st.markdown(f"*Tension {a.get('code')} ({AXES.get(a.get('code'), '')})* : {par}")
            if r["tension_libre"]:
                st.markdown(f"*Tension hors grille* : {r['tension_libre']}")
            if r["ce_qu_on_ne_sait_pas"]:
                st.caption(f"Ce qu'on ne sait pas : {r['ce_qu_on_ne_sait_pas']}")
    st.divider()
    st.subheader("Tous les sujets des 14 derniers jours")
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
