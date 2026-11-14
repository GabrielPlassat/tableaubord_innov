"""Fonctions partagees par les pages de l'application v2."""
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

RACINE = Path(__file__).resolve().parents[1]

NOMS_AIRES = {
    "EU": "Europe", "US": "Amérique du Nord", "CN": "Chine", "JK": "Japon, Corée, Taïwan",
    "IN": "Asie du Sud", "ASE": "Asie du Sud-Est", "RU": "Russie et Eurasie", "GO": "Golfe",
    "MO": "Moyen-Orient et Afrique du Nord", "AF": "Afrique subsaharienne",
    "LA": "Amérique latine", "OC": "Océanie", "GLO": "Global",
}
ORDRE_AIRES = list(NOMS_AIRES)
AIRES_OCCIDENT = {"EU", "US", "OC"}


@st.cache_data(ttl=600)
def charger_sources():
    return pd.read_csv(RACINE / "config" / "sources.csv", dtype=str).fillna("")


@st.cache_data(ttl=600)
def charger_audit():
    chemin = RACINE / "journal" / "audit_sources.csv"
    if not chemin.exists():
        return None
    return pd.read_csv(chemin, dtype=str).fillna("")


@st.cache_data(ttl=600)
def charger_seuils():
    with open(RACINE / "config" / "seuils.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parts_par_aire(df):
    """Part de chaque aire (fractions), dans l'ordre fixe des zones."""
    if df.empty:
        return pd.Series(0.0, index=ORDRE_AIRES)
    return df["aire_source"].value_counts(normalize=True).reindex(ORDRE_AIRES, fill_value=0.0)


def indicateur_diversite(parts, seuil=0.05):
    visibles = int((parts > seuil).sum())
    dominante = parts.idxmax()
    return f"{visibles} aires · dominante {dominante} {parts.max():.0%}", visibles, dominante, parts.max()


def regles_diversite(df, seuils):
    """Applique les regles de L1 (section 9.3) au tableau fourni. Renvoie une liste de lignes."""
    d = seuils["diversite"]
    parts = parts_par_aire(df)
    lignes = []
    dom = parts.idxmax()
    lignes.append(("Aucune aire au-dessus de {:.0%}".format(d["part_max_une_aire"]),
                   f"{dom} : {parts.max():.0%}", parts.max() <= d["part_max_une_aire"]))
    occ = parts[list(AIRES_OCCIDENT)].sum()
    lignes.append(("EU + US + OC au plus {:.0%}".format(d["part_max_eu_us_oc"]),
                   f"{occ:.0%}", occ <= d["part_max_eu_us_oc"]))
    for aire in d["aires_cibles"]:
        if aire == "MO_GO":
            v, nom = parts["MO"] + parts["GO"], "MO + GO"
        else:
            v, nom = parts[aire], aire
        lignes.append((f"{nom} au moins {d['part_min_aires_cibles']:.0%}", f"{v:.0%}",
                       v >= d["part_min_aires_cibles"]))
    non_occ = df[~df["aire_source"].isin(AIRES_OCCIDENT | {"GLO"})]
    if len(non_occ):
        hors_en_fr = (~non_occ["langue"].isin(["en", "fr"])).mean()
        lignes.append((f"Sources non occidentales en langue d'origine : au moins {d['part_min_langue_origine']:.0%}",
                       f"{hors_en_fr:.0%}", hors_en_fr >= d["part_min_langue_origine"]))
    return lignes
