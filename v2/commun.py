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


# ---------------------------------------------------------------- Sprint 2 : collecte

@st.cache_data(ttl=600)
def charger_executions():
    chemin = RACINE / "journal" / "executions.csv"
    if not chemin.exists():
        return None
    return pd.read_csv(chemin, dtype=str).fillna("")


@st.cache_data(ttl=600)
def charger_suivi_sources():
    chemin = RACINE / "journal" / "collecte_sources.csv"
    if not chemin.exists():
        return None
    return pd.read_csv(chemin, dtype=str).fillna("")


def _jeton_hf():
    try:
        return st.secrets.get("HF_TOKEN", "")
    except Exception:  # pas de fichier de secrets
        return ""


@st.cache_data(ttl=1800, show_spinner="Lecture des fiches sur Hugging Face…")
def charger_fiches(mois: str):
    """Fiches d'un mois (AAAA-MM). Renvoie (tableau ou None, message)."""
    jeton = _jeton_hf()
    if not jeton:
        locale = RACINE / "donnees_locales" / "fiches" / f"{mois}.parquet"
        if locale.exists():
            return pd.read_parquet(locale), "local"
        return None, "Secret HF_TOKEN absent des réglages de l'application Streamlit."
    from huggingface_hub import HfApi, hf_hub_download
    with open(RACINE / "config" / "stockage.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    try:
        depot = conf.get("depot_hf") or f'{HfApi(token=jeton).whoami()["name"]}/{conf["nom_par_defaut"]}'
        fichier = hf_hub_download(depot, f"fiches/{mois}.parquet", repo_type="dataset", token=jeton)
    except Exception as e:  # noqa: BLE001
        return None, f"Pas de fiches pour {mois} ({type(e).__name__})."
    return pd.read_parquet(fichier), depot


# ---------------------------------------------------------------- Sprint 2 bis : series

@st.cache_data(ttl=3600, show_spinner="Lecture des séries…")
def charger_series():
    """Series chiffrees (format long) et leur description. Renvoie (donnees ou None, catalogue, message)."""
    catalogue = pd.read_csv(RACINE / "config" / "series.csv", dtype=str).fillna("")
    jeton = _jeton_hf()
    if not jeton:
        locale = RACINE / "donnees_locales" / "series" / "donnees.parquet"
        if locale.exists():
            return pd.read_parquet(locale), catalogue, "local"
        return None, catalogue, "Secret HF_TOKEN absent des réglages de l'application Streamlit."
    from huggingface_hub import HfApi, hf_hub_download
    with open(RACINE / "config" / "stockage.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    try:
        depot = conf.get("depot_hf") or f'{HfApi(token=jeton).whoami()["name"]}/{conf["nom_par_defaut"]}'
        fichier = hf_hub_download(depot, "series/donnees.parquet", repo_type="dataset", token=jeton)
    except Exception as e:  # noqa: BLE001
        return None, catalogue, f"Pas encore de séries ({type(e).__name__})."
    return pd.read_parquet(fichier), catalogue, depot


@st.cache_data(ttl=1800, show_spinner="Lecture des sujets…")
def charger_sujets():
    """Groupes de sujets calcules chaque nuit (sujets/groupes.parquet). Renvoie (tableau ou None, message)."""
    jeton = _jeton_hf()
    if not jeton:
        locale = RACINE / "donnees_locales" / "sujets" / "groupes.parquet"
        return (pd.read_parquet(locale), "local") if locale.exists() else (None, "Secret HF_TOKEN absent.")
    from huggingface_hub import HfApi, hf_hub_download
    with open(RACINE / "config" / "stockage.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    try:
        depot = conf.get("depot_hf") or f'{HfApi(token=jeton).whoami()["name"]}/{conf["nom_par_defaut"]}'
        return pd.read_parquet(hf_hub_download(depot, "sujets/groupes.parquet", repo_type="dataset", token=jeton)), depot
    except Exception as e:  # noqa: BLE001
        return None, f"Pas encore de sujets ({type(e).__name__}) : ils sont calculés chaque nuit."


@st.cache_data(ttl=1800, show_spinner="Lecture des étiquettes des agents…")
def charger_etiquettes():
    """Sujets de la semaine étiquetés par Opus (sujets/etiquettes.parquet). Renvoie (tableau ou None, message)."""
    jeton = _jeton_hf()
    if not jeton:
        locale = RACINE / "donnees_locales" / "sujets" / "etiquettes.parquet"
        return (pd.read_parquet(locale), "local") if locale.exists() else (None, "Secret HF_TOKEN absent.")
    from huggingface_hub import HfApi, hf_hub_download
    with open(RACINE / "config" / "stockage.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    try:
        depot = conf.get("depot_hf") or f'{HfApi(token=jeton).whoami()["name"]}/{conf["nom_par_defaut"]}'
        return pd.read_parquet(hf_hub_download(depot, "sujets/etiquettes.parquet", repo_type="dataset", token=jeton)), depot
    except Exception as e:  # noqa: BLE001
        return None, f"Pas encore d'étiquettes ({type(e).__name__}) : elles sont produites chaque lundi."
