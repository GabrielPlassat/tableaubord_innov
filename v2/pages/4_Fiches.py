"""Fiches classées : filtres par lentille, aire du sujet, iceberg et nature (Sprint 3)."""
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

import importlib

import commun

importlib.reload(commun)  # Streamlit Cloud garde parfois l'ancienne version de commun.py en memoire
from commun import NOMS_AIRES, ORDRE_AIRES, charger_fiches

st.set_page_config(page_title="Fiches", page_icon="◈", layout="wide")
st.title("Fiches")

LENTILLES = {"TEC": "Techniques", "INF": "Infrastructures", "MON": "Monnaies et flux", "PUI": "Puissance",
             "SOC": "Sociétés", "SOL": "Solutions", "MIL": "Milieux"}
ICEBERG = {"N1": "N1 événement", "N2": "N2 évolution", "N3": "N3 structure", "N4": "N4 croyance"}

c1, c2 = st.columns([3, 1])
mois = c1.text_input("Mois (AAAA-MM)", datetime.now(timezone.utc).strftime("%Y-%m"))
if c2.button("Recharger"):
    charger_fiches.clear()
fiches, info = charger_fiches(mois)
if fiches is None:
    st.warning(info)
    st.stop()
if "classe" not in fiches or "lentille_principale" not in fiches:
    st.info("Aucune fiche classée pour l'instant : le classement démarre avec le Sprint 3.")
    st.stop()
classees = fiches[fiches["classe"].astype(str).str.lower() == "true"].copy()
st.caption(f"{len(classees)} fiches classées sur {len(fiches)} articles collectés ce mois-ci · "
           f"tri : {(fiches.get('tri', pd.Series(dtype=str)) == 'NON').sum()} écartés")
if classees.empty:
    st.stop()

f1, f2, f3, f4 = st.columns(4)
lent = f1.multiselect("Lentille", list(LENTILLES), format_func=lambda k: f"{k} {LENTILLES[k]}")
aires = f2.multiselect("Aire du sujet", ORDRE_AIRES, format_func=lambda k: f"{k} {NOMS_AIRES[k]}")
ice = f3.multiselect("Iceberg", list(ICEBERG), format_func=ICEBERG.get)
nat = f4.multiselect("Nature", ["FAIT", "ANALYSE", "OPINION", "COMMUNICATION"])
q = st.text_input("Chercher dans le titre et le résumé", "")

v = classees
if lent:
    v = v[v["lentille_principale"].isin(lent) | v["lentille_secondaire"].isin(lent)]
if aires:
    v = v[v["aire_sujet"].fillna("").apply(lambda s: any(a in s.split(";") for a in aires))]
if ice:
    v = v[v["iceberg"].isin(ice)]
if nat:
    v = v[v["nature"].isin(nat)]
if q:
    v = v[(v["titre_fr"].fillna("") + " " + v["resume"].fillna("")).str.contains(q, case=False, regex=False)]
st.caption(f"{len(v)} fiches correspondent.")

for _, r in v.sort_values("date_classement", ascending=False).head(100).iterrows():
    with st.container(border=True):
        st.markdown(f"**[{r['titre_fr'] or r['titre_original']}]({r['url']})**")
        st.caption(f"{r['source_nom']} · source {r['aire_source']} · sujet {r['aire_sujet']} · "
                   f"{r['lentille_principale']}{('/' + r['lentille_secondaire']) if r['lentille_secondaire'] else ''} · "
                   f"{r['iceberg']} · {r['nature']} · langue {r['langue']} · confiance {r['confiance']}")
        st.write(r["resume"])
