"""Series chiffrees : bourses, changes, reserves, demographie, energie (Sprint 2 bis).

Lit config/series.csv et config/series_pays.yaml, interroge les API ouvertes
(Stooq, BCE, FMI, Banque mondiale, Our World in Data, INSEE), et range tout dans
le jeu de donnees Hugging Face prive : series/donnees.parquet (format long :
serie_id, pays, date, valeur). Sans HF_TOKEN : donnees_locales/series/.

Journal : journal/series_etat.csv (une ligne par serie : statut, derniere date,
derniere valeur, nombre de points, message).
"""
from __future__ import annotations

import io
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import yaml

RACINE = Path(__file__).resolve().parents[1]
CONFIG = RACINE / "config"
JOURNAL = RACINE / "journal"
LOCAL = RACINE / "donnees_locales" / "series"
ENTETES = {"User-Agent": "InnovationRadar/2.0 (+https://github.com/GabrielPlassat/tableaubord_innov)"}
DEPUIS = "2015-01-01"
OWID_CODES = {"WLD": "OWID_WRL"}


def get(url, essais=4, **kw):
    """GET avec nouvel essai sur les erreurs passageres (503, coupure)."""
    kw.setdefault("timeout", 60)
    kw.setdefault("headers", ENTETES)
    for i in range(essais):
        try:
            r = requests.get(url, **kw)
            if r.status_code in (429, 500, 502, 503, 504) and i < essais - 1:
                time.sleep(10 * (i + 1))
                continue
            r.raise_for_status()
            return r
        except (requests.ConnectionError, requests.Timeout):
            if i == essais - 1:
                raise
            time.sleep(10 * (i + 1))


# ---------------------------------------------------------------- une fonction par source
# Chacune renvoie un tableau (pays, date, valeur). pays = "" pour une serie unique.

def stooq(code, _pays):
    cle = os.environ.get("STOOQ_API_KEY", "").strip()
    if not cle:
        raise RuntimeError("secret STOOQ_API_KEY absent")
    r = get("https://stooq.com/q/d/l/", params={"s": code, "i": "d", "d1": DEPUIS.replace("-", ""), "apikey": cle})
    if not r.text.startswith("Date"):
        raise RuntimeError(f"reponse inattendue : {r.text[:80]!r}")
    df = pd.read_csv(io.StringIO(r.text))
    return pd.DataFrame({"pays": "", "date": df["Date"], "valeur": df["Close"]})


def ecb(code, _pays):
    r = get(f"https://data-api.ecb.europa.eu/service/data/EXR/D.{code}.EUR.SP00.A",
            params={"format": "csvdata", "startPeriod": DEPUIS})
    df = pd.read_csv(io.StringIO(r.text))
    return pd.DataFrame({"pays": "", "date": df["TIME_PERIOD"], "valeur": df["OBS_VALUE"]})


def imf(code, _pays):
    flux, cle = code.split("/", 1)
    r = get(f"https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/{flux}/+/{cle}",
            headers={**ENTETES, "Accept": "application/vnd.sdmx.data+csv;version=2.0.0"})
    df = pd.read_csv(io.StringIO(r.text))
    if "TIME_PERIOD" not in df or "OBS_VALUE" not in df:
        raise RuntimeError(f"colonnes inattendues : {list(df.columns)[:8]}")
    return pd.DataFrame({"pays": "", "date": df["TIME_PERIOD"], "valeur": df["OBS_VALUE"]})


def worldbank(code, pays):
    lignes = []
    for i in range(0, len(pays), 8):          # par paquets : l'API refuse parfois les longues listes
        r = get(f"https://api.worldbank.org/v2/country/{';'.join(pays[i:i + 8])}/indicator/{code}",
                essais=2, timeout=30, params={"format": "json", "per_page": 5000, "date": f"{DEPUIS[:4]}:2030"})
        donnees = r.json()
        if len(donnees) < 2 or not donnees[1]:
            continue
        lignes += [(d["countryiso3code"] or d["country"]["id"], d["date"], d["value"])
                   for d in donnees[1] if d["value"] is not None]
    if not lignes:
        raise RuntimeError("aucune donnee")
    return pd.DataFrame(lignes, columns=["pays", "date", "valeur"])


def owid(code, pays):
    r = get(f"https://ourworldindata.org/grapher/{code}.csv", params={"v": 1, "csvType": "full", "useColumnShortNames": "true"})
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.lower() for c in df.columns]
    col = [c for c in df.columns if c not in ("entity", "code", "year")][0]
    codes = {OWID_CODES.get(p, p): p for p in pays}
    df = df[df["code"].isin(codes) & (df["year"] >= int(DEPUIS[:4]))]
    return pd.DataFrame({"pays": df["code"].map(codes), "date": df["year"].astype(str), "valeur": df[col]})


def insee(code, _pays):
    r = get(f"https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/{code}", params={"startPeriod": DEPUIS[:4]})
    import xml.etree.ElementTree as ET
    racine = ET.fromstring(r.content)
    obs = [(o.get("TIME_PERIOD"), o.get("OBS_VALUE")) for o in racine.iter() if o.tag.endswith("Obs")]
    if not obs:
        raise RuntimeError("aucune observation")
    return pd.DataFrame({"pays": "", "date": [o[0] for o in obs], "valeur": [o[1] for o in obs]})


SOURCES = {"stooq": stooq, "ecb": ecb, "imf": imf, "worldbank": worldbank, "owid": owid, "insee": insee}


# ---------------------------------------------------------------- stockage

def ecrire(df: pd.DataFrame):
    jeton = os.environ.get("HF_TOKEN", "").strip()
    if not jeton:
        LOCAL.mkdir(parents=True, exist_ok=True)
        df.to_parquet(LOCAL / "donnees.parquet", index=False)
        return "local"
    from huggingface_hub import HfApi
    api = HfApi(token=jeton)
    conf = yaml.safe_load(open(CONFIG / "stockage.yaml", encoding="utf-8"))
    depot = conf.get("depot_hf") or f'{api.whoami()["name"]}/{conf["nom_par_defaut"]}'
    api.create_repo(depot, repo_type="dataset", private=True, exist_ok=True)
    tmp = Path("/tmp/series_donnees.parquet")
    df.to_parquet(tmp, index=False)
    api.upload_file(path_or_fileobj=str(tmp), path_in_repo="series/donnees.parquet", repo_id=depot,
                    repo_type="dataset", commit_message=f"Series du {datetime.now(timezone.utc):%Y-%m-%d}")
    return depot


def main():
    series = pd.read_csv(CONFIG / "series.csv", dtype=str).fillna("")
    series = series[series["actif"] == "oui"]
    pays = list(yaml.safe_load(open(CONFIG / "series_pays.yaml", encoding="utf-8"))["pays"])
    tout, etat = [], []
    limite = time.time() + 12 * 60            # le tout doit tenir en 12 minutes
    for s in series.to_dict("records"):
        debut = time.time()
        print(s["id"], "...", flush=True)
        try:
            if debut > limite:
                raise RuntimeError("temps total depasse, serie reportee au prochain passage")
            df = SOURCES[s["source"]](s["code"], pays)
            df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
            df = df.dropna(subset=["valeur"])
            if df.empty:
                raise RuntimeError("aucune valeur numerique")
            df["date"] = df["date"].astype(str)
            df.insert(0, "serie_id", s["id"])
            tout.append(df)
            dernier = df.sort_values("date").iloc[-1]
            etat.append({"id": s["id"], "statut": "OK", "points": len(df), "derniere_date": dernier["date"],
                         "derniere_valeur": dernier["valeur"], "message": "", "duree_s": round(time.time() - debut, 1)})
        except Exception as e:  # noqa: BLE001 : une serie en panne ne bloque pas les autres
            etat.append({"id": s["id"], "statut": "ERREUR", "points": 0, "derniere_date": "", "derniere_valeur": "",
                         "message": f"{type(e).__name__} : {e}"[:200], "duree_s": round(time.time() - debut, 1)})
        if s["source"] == "stooq":
            time.sleep(1)
    JOURNAL.mkdir(exist_ok=True)
    etat = pd.DataFrame(etat)
    etat.insert(1, "date_controle", datetime.now(timezone.utc).date().isoformat())
    etat.to_csv(JOURNAL / "series_etat.csv", index=False)
    print(etat[["id", "statut", "points", "derniere_date", "message"]].to_string())
    if tout:
        print("stockage :", ecrire(pd.concat(tout, ignore_index=True)))
    if (etat["statut"] == "OK").sum() == 0:
        sys.exit("aucune serie lue")


if __name__ == "__main__":
    main()
