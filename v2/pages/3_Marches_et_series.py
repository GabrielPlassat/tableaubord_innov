"""Marchés et séries : bourses, monnaies, réserves de change, indicateurs par pays (Sprint 2 bis)."""
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml

import importlib

import commun

importlib.reload(commun)  # Streamlit Cloud garde parfois l'ancienne version de commun.py en memoire
from commun import NOMS_AIRES, RACINE, charger_series

st.set_page_config(page_title="Marchés et séries", page_icon="◈", layout="wide")
st.title("Marchés et séries")

donnees, cat, info = charger_series()
if donnees is None:
    st.warning(info)
    st.stop()
if st.button("Recharger"):
    charger_series.clear()
    st.rerun()
noms = cat.set_index("id")["nom"].to_dict()
donnees = donnees.assign(nom=donnees["serie_id"].map(noms))
pays_aire = yaml.safe_load(open(RACINE / "config" / "series_pays.yaml", encoding="utf-8"))["pays"]

onglets = st.tabs(["Bourses et matières premières", "Monnaies", "Indicateurs par pays", "Toutes les séries"])

# ------------------------------------------------------------ bourses
with onglets[0]:
    ids = cat[cat["id"].str.startswith(("bourse-", "matiere-"))]["id"]
    d = donnees[donnees["serie_id"].isin(ids)].copy()
    if d.empty:
        st.info("Pas encore de données de bourse : il faut le secret STOOQ_API_KEY dans GitHub (voir docs/README.md).")
    else:
        d["date"] = pd.to_datetime(d["date"])
        lignes = []
        for sid, g in d.sort_values("date").groupby("serie_id"):
            g = g.set_index("date")["valeur"]
            fin = g.iloc[-1]
            def var(jours):
                avant = g[g.index <= g.index[-1] - pd.Timedelta(days=jours)]
                return fin / avant.iloc[-1] - 1 if len(avant) else None
            zone = cat.set_index("id").at[sid, "zone"]
            lignes.append({"Série": noms.get(sid, sid), "Aire": NOMS_AIRES.get(zone, zone), "Dernière valeur": fin,
                           "Date": g.index[-1].date(), "1 mois": var(30), "1 an": var(365), "5 ans": var(1826)})
        tab = pd.DataFrame(lignes)
        st.dataframe(tab, width="stretch", hide_index=True, column_config={
            "Dernière valeur": st.column_config.NumberColumn(format="%.0f"),
            **{k: st.column_config.NumberColumn(format="percent") for k in ["1 mois", "1 an", "5 ans"]}})
        choix = st.multiselect("Comparer (base 100 au début de la période)", tab["Série"].tolist(),
                               default=tab["Série"].tolist()[:6])
        periode = st.select_slider("Période", ["6 mois", "1 an", "3 ans", "5 ans", "10 ans"], value="3 ans")
        jours = {"6 mois": 182, "1 an": 365, "3 ans": 1096, "5 ans": 1826, "10 ans": 3652}[periode]
        c = d[d["nom"].isin(choix) & (d["date"] >= d["date"].max() - pd.Timedelta(days=jours))].sort_values("date")
        c["base 100"] = c.groupby("nom")["valeur"].transform(lambda v: 100 * v / v.iloc[0])
        st.plotly_chart(px.line(c, x="date", y="base 100", color="nom", labels={"date": "", "nom": ""}), width="stretch")

# ------------------------------------------------------------ monnaies
with onglets[1]:
    r = donnees[donnees["serie_id"].str.startswith("reserves-")]
    if len(r):
        st.markdown("**Composition des réserves de change mondiales (FMI, COFER)**")
        st.plotly_chart(px.line(r.sort_values("date"), x="date", y="valeur", color="nom",
                                labels={"date": "", "valeur": "%", "nom": ""}), width="stretch")
    ch = donnees[donnees["serie_id"].str.startswith("change-")].copy()
    if len(ch):
        ch["date"] = pd.to_datetime(ch["date"])
        ch = ch.sort_values("date")
        ch["base 100"] = ch.groupby("nom")["valeur"].transform(lambda v: 100 * v / v.iloc[0])
        st.markdown("**Taux de change contre l'euro, base 100 en 2015 (BCE)** : au-dessus de 100, la devise s'est affaiblie face à l'euro.")
        st.plotly_chart(px.line(ch, x="date", y="base 100", color="nom", labels={"date": "", "nom": ""}), width="stretch")

# ------------------------------------------------------------ indicateurs par pays
with onglets[2]:
    ids = cat[cat["source"].isin(["worldbank", "owid"])]
    d = donnees[donnees["serie_id"].isin(ids["id"])]
    if d.empty:
        st.info("Pas encore d'indicateurs par pays.")
    else:
        nom = st.selectbox("Indicateur", ids["nom"].tolist())
        sid = ids.set_index("nom").at[nom, "id"]
        g = d[d["serie_id"] == sid].copy()
        g["aire"] = g["pays"].map(pays_aire).map(NOMS_AIRES)
        retenus = st.multiselect("Pays", sorted(g["pays"].unique()),
                                 default=[p for p in ["WLD", "USA", "CHN", "IND", "NGA", "BRA", "IDN", "FRA"] if p in set(g["pays"])])
        g = g[g["pays"].isin(retenus)].sort_values("date")
        st.plotly_chart(px.line(g, x="date", y="valeur", color="pays", hover_data=["aire"],
                                labels={"date": "", "valeur": cat.set_index("id").at[sid, "unite"]}), width="stretch")
        st.caption(cat.set_index("id").at[sid, "remarque"])

# ------------------------------------------------------------ catalogue
with onglets[3]:
    etat = RACINE / "journal" / "series_etat.csv"
    vue = cat[["id", "nom", "source", "zone", "lentille", "frequence", "unite"]]
    if etat.exists():
        vue = vue.merge(pd.read_csv(etat, dtype=str)[["id", "statut", "derniere_date", "message"]], on="id", how="left")
    st.dataframe(vue, width="stretch", hide_index=True)
    st.caption("Sources : Stooq, Banque centrale européenne, FMI (COFER), Banque mondiale, Our World in Data, INSEE. "
               "Ajouter une série : une ligne dans config/series.csv.")
