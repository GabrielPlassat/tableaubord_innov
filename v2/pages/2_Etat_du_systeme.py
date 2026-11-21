"""État du système : collectes, sources en échec, fiches du mois (Sprint 2)."""
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

import importlib

import commun

importlib.reload(commun)  # Streamlit Cloud garde parfois l'ancienne version de commun.py en memoire
from commun import (NOMS_AIRES, ORDRE_AIRES, charger_executions, charger_fiches, charger_seuils,
                    charger_sources, charger_suivi_sources, regles_diversite)

st.set_page_config(page_title="État du système", page_icon="◈", layout="wide")
st.title("État du système")

# ------------------------------------------------------------ dernières collectes
ex = charger_executions()
if ex is None or ex.empty:
    st.info("Aucune collecte encore. Lancez-la depuis GitHub : onglet Actions > « Collecte » > Run workflow.")
    st.stop()

ex = ex[ex["tache"] == "collecte"].copy()
derniere = ex.iloc[-1]
fin = pd.to_datetime(derniere.get("fin") or derniere["debut"], utc=True)
age_h = (datetime.now(timezone.utc) - fin).total_seconds() / 3600
if age_h > 48:
    st.error(f"Dernière collecte il y a {age_h / 24:.1f} jours : la tâche planifiée ne tourne plus. "
             "Vérifiez l'onglet Actions de GitHub.")
elif derniere.get("erreurs", "").startswith("ECHEC"):
    st.error(f"La dernière collecte a échoué : {derniere['erreurs']}")
else:
    st.success(f"Dernière collecte il y a {age_h:.1f} heures.")

def nombre(col):
    return pd.to_numeric(ex.get(col, 0), errors="coerce").fillna(0).astype(int)

c = st.columns(5)
c[0].metric("Articles vus (dernière)", nombre("articles_vus").iloc[-1])
c[1].metric("Nouvelles fiches (dernière)", nombre("nouveaux").iloc[-1])
c[2].metric("Doublons écartés", nombre("deja_connus").iloc[-1] + nombre("doublons_titre").iloc[-1])
c[3].metric("Écartés par le plafond", nombre("ecartes_plafond").iloc[-1])
c[4].metric("Sources en échec", f'{nombre("sources_erreur").iloc[-1]} / {nombre("sources_lues").iloc[-1]}')

st.subheader("Historique des collectes")
vue = ex.rename(columns={
    "debut": "Début (UTC)", "duree_s": "Durée (s)", "sources_lues": "Sources", "sources_erreur": "En échec",
    "articles_vus": "Vus", "deja_connus": "Déjà connus", "doublons_titre": "Reprises", "ecartes_plafond": "Plafond",
    "nouveaux": "Nouvelles", "gdelt_articles": "Dont GDELT", "tri_non": "Écartées au tri",
    "fiches": "Fiches classées", "fiches_reportees": "Classement reporté", "erreurs": "Erreurs"})
colonnes = [k for k in ["Début (UTC)", "Durée (s)", "Sources", "En échec", "Vus", "Déjà connus", "Reprises",
                        "Plafond", "Nouvelles", "Dont GDELT", "Écartées au tri", "Fiches classées",
                        "Classement reporté", "Erreurs"] if k in vue]
st.dataframe(vue[colonnes].iloc[::-1], width="stretch", hide_index=True)

# ------------------------------------------------------------ sources en échec
st.subheader("Sources en échec")
suivi = charger_suivi_sources()
if suivi is not None:
    noms = charger_sources().set_index("id")["nom"]
    ko = suivi[suivi["statut"] != "OK"].copy()
    ko["nom"] = ko["id"].map(noms).fillna(ko["id"])
    ordre = {"DESACTIVEE": 0, "SIGNALEE": 1, "ECHEC": 2}
    ko = ko.sort_values("statut", key=lambda s: s.map(ordre))
    st.caption("ECHEC : moins de 7 jours · SIGNALEE : 7 jours de suite · DESACTIVEE : 30 jours, "
               "retirée automatiquement du registre.")
    st.dataframe(ko[["nom", "statut", "derniere_erreur", "premier_echec", "dernier_succes"]].rename(columns={
        "nom": "Source", "statut": "Statut", "derniere_erreur": "Erreur", "premier_echec": "En échec depuis",
        "dernier_succes": "Dernier succès"}), width="stretch", hide_index=True)

# ------------------------------------------------------------ fiches du mois
st.subheader("Fiches collectées")
m1, m2 = st.columns([3, 1])
mois = m1.text_input("Mois (AAAA-MM)", datetime.now(timezone.utc).strftime("%Y-%m"))
if m2.button("Recharger les fiches"):
    charger_fiches.clear()
fiches, info = charger_fiches(mois)
if fiches is None:
    st.warning(info)
    st.stop()
st.caption(f"{len(fiches)} fiches · stockage : {info}")
st.download_button("Télécharger toutes les fiches du mois (CSV)",
                   fiches.drop(columns=["urls_reprises"], errors="ignore").to_csv(index=False).encode("utf-8"),
                   file_name=f"fiches_{mois}.csv", mime="text/csv")

parts = fiches["aire_source"].value_counts(normalize=True).reindex(ORDRE_AIRES, fill_value=0)
fig = px.bar(x=[NOMS_AIRES[a] for a in parts.index], y=parts.values, labels={"x": "", "y": "Part des fiches"})
fig.update_layout(yaxis_tickformat=".0%", height=320, margin=dict(t=10, b=10))
st.plotly_chart(fig, width="stretch")
with st.expander("Règles de diversité (L1, section 9.3) appliquées aux articles"):
    for regle, valeur, ok in regles_diversite(fiches, charger_seuils()):
        st.write(("✅ " if ok else "❌ ") + f"{regle} : {valeur}")

st.markdown("**Articles repris par plusieurs sources**")
reprises = fiches[fiches["reprises"].astype(int) > 0].sort_values("reprises", ascending=False)
st.dataframe(reprises[["titre_original", "source_nom", "reprises", "sources_reprises", "url"]].head(50),
             width="stretch", hide_index=True, column_config={"url": st.column_config.LinkColumn("Lien")})

st.markdown("**Parcourir les fiches**")
f1, f2, f3 = st.columns([1, 1, 2])
origine = f1.selectbox("Origine", ["Toutes", "Flux RSS", "GDELT"])
aire = f2.selectbox("Aire de la source", ["Toutes"] + [a for a in ORDRE_AIRES if a in set(fiches["aire_source"])])
q = f3.text_input("Mot à chercher (titre ou nom de la source)", "")
liste = fiches
if origine == "GDELT":
    liste = liste[liste["type_source"] == "GDELT"]
elif origine == "Flux RSS":
    liste = liste[liste["type_source"] != "GDELT"]
if aire != "Toutes":
    liste = liste[liste["aire_source"] == aire]
if q:
    texte = liste["titre_original"].fillna("") + " " + liste["source_nom"].fillna("")
    liste = liste[texte.str.contains(q, case=False, regex=False)]
st.caption(f"{len(liste)} fiches correspondent (300 premières affichées).")
st.dataframe(liste.sort_values("date_collecte", ascending=False)[
    ["date_collecte", "titre_original", "langue", "aire_source", "source_nom", "texte_source", "longueur_texte", "url"]
].head(300), width="stretch", hide_index=True, column_config={"url": st.column_config.LinkColumn("Lien")})
st.caption(f"Droits d'auteur : seul un extrait du flux est conservé (au plus "
           f"{int(fiches['extrait'].str.len().max() or 0)} caractères ici). Le texte des pages est mesuré puis jeté. "
           "Articles GDELT : The GDELT Project (gdeltproject.org).")
