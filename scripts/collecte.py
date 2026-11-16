"""Collecte des articles (Sprint 2, sans classement).

Lit les flux du registre (config/sources.csv) et les requetes GDELT (config/gdelt.yaml),
dedoublonne, applique le plafond par aire, mesure le texte disponible sans le conserver,
et range les fiches dans un jeu de donnees Hugging Face prive (fiches/AAAA-MM.parquet).

Sans jeton HF_TOKEN, les fiches sont ecrites dans donnees_locales/ (essai).
Journal : journal/executions.csv et journal/collecte_sources.csv.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import pandas as pd
import requests
import yaml

RACINE = Path(__file__).resolve().parents[1]
CONFIG = RACINE / "config"
JOURNAL = RACINE / "journal"
LOCAL = RACINE / "donnees_locales"
MAINTENANT = datetime.now(timezone.utc)
ENTETES = {"User-Agent": "InnovationRadar/2.0 (+https://github.com/GabrielPlassat/tableaubord_innov)"}
AGE_MAX_JOURS = 7     # remplace par seuils.yaml > collecte > age_max_jours
RANG_ANCRAGE = {"LOCAL": 0, "DIASPORA": 1, "CORRESPONDANT": 2, "INTERNATIONAL": 3}
COLONNES = [
    "id", "url", "url_canonique", "titre_original", "langue", "date_publication", "date_collecte",
    "source_id", "source_nom", "type_source", "aire_source", "ancrage", "lien_pouvoir",
    "extrait", "longueur_texte", "texte_source", "reprises", "sources_reprises", "urls_reprises", "classe",
]


def lire_yaml(nom):
    with open(CONFIG / nom, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------- outils texte

def canoniser(url: str) -> str:
    """URL sans www, sans parametres de suivi, sans ancre ni barre finale."""
    try:
        p = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    hote = p.netloc.lower().removeprefix("www.").removeprefix("m.")
    params = [(k, v) for k, v in parse_qsl(p.query)
              if not k.lower().startswith(("utm_", "fbclid", "gclid", "mc_", "at_", "ref", "cmp"))]
    chemin = p.path.rstrip("/") or "/"
    return urlunsplit(("https", hote, chemin, urlencode(params), ""))


def sans_html(texte: str) -> str:
    texte = re.sub(r"<[^>]+>", " ", texte or "")
    return re.sub(r"\s+", " ", html.unescape(texte)).strip()


def mots_titre(titre: str) -> frozenset:
    t = unicodedata.normalize("NFKD", titre.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^\w\s]", " ", t)
    mots = [m for m in t.split() if len(m) > 2]
    if len(mots) < 3:                 # langues sans espaces (chinois, japonais) : bigrammes
        brut = re.sub(r"\s+", "", t)
        mots = [brut[i:i + 2] for i in range(len(brut) - 1)]
    return frozenset(mots)


def date_iso(entree) -> str:
    for cle in ("published_parsed", "updated_parsed"):
        v = entree.get(cle)
        if v:
            try:
                return datetime(*v[:6], tzinfo=timezone.utc).isoformat()
            except (TypeError, ValueError):
                pass
    return ""


# ---------------------------------------------------------------- lecture des flux

def lire_flux(src: dict) -> tuple[str, list[dict], str]:
    """Renvoie (id, articles, message d'erreur)."""
    try:
        r = requests.get(src["url"], headers=ENTETES, timeout=25)
        if r.status_code >= 400:
            return src["id"], [], f"HTTP {r.status_code}"
        flux = feedparser.parse(r.content)
    except Exception as e:  # noqa: BLE001
        return src["id"], [], type(e).__name__
    articles = []
    limite = (MAINTENANT - timedelta(days=AGE_MAX_JOURS)).isoformat()
    for e in flux.entries[:100]:
        lien = e.get("link") or ""
        titre = sans_html(e.get("title") or "")
        if not lien.startswith("http") or not titre:
            continue
        dpub = date_iso(e)
        if dpub and dpub < limite:      # article trop ancien (archives du flux)
            continue
        contenu = ""
        if e.get("content"):
            contenu = " ".join(c.get("value", "") for c in e["content"])
        texte = sans_html(contenu or e.get("summary") or e.get("description") or "")
        articles.append({
            "url": lien, "titre_original": titre[:500], "date_publication": dpub,
            "langue": src.get("langue", ""), "source_id": src["id"], "source_nom": src["nom"],
            "type_source": src["type"], "aire_source": src["aire_source"],
            "ancrage": src["ancrage"], "lien_pouvoir": src["lien_pouvoir"],
            "_texte": texte,
        })
    if not articles:
        return src["id"], [], ("" if flux.entries else "Aucun article lisible")
    return src["id"], articles, ""


LANGUES_ISO3 = {
    "zho": "zh", "jpn": "ja", "kor": "ko", "ara": "ar", "fas": "fa", "tur": "tr", "rus": "ru",
    "hin": "hi", "ben": "bn", "urd": "ur", "tam": "ta", "ind": "id", "msa": "ms", "vie": "vi",
    "tha": "th", "spa": "es", "por": "pt", "swa": "sw", "amh": "am", "hau": "ha", "fra": "fr",
    "deu": "de", "mon": "mn", "ita": "it", "heb": "he", "ukr": "uk", "pol": "pl", "nld": "nl", "eng": "en",
}
URL_GDELT = "http://data.gdeltproject.org/gdeltv2/"
ETAT_GDELT = JOURNAL / "gdelt_dernier_fichier.txt"


def aire_du_domaine(domaine: str, langue: str, conf: dict, pays_zone: dict) -> str:
    """Aire de la source : liste de domaines connus, puis extension nationale, puis langue."""
    d = domaine.lower().removeprefix("www.")
    for connu, aire in (conf.get("domaines") or {}).items():
        if d == connu or d.endswith("." + connu):
            return aire
    tld = d.rsplit(".", 1)[-1]
    tld = {"uk": "GB"}.get(tld, tld.upper())
    if tld not in set(conf.get("extensions_ignorees", [])) and tld in pays_zone:
        return pays_zone[tld]
    return (conf.get("langue_vers_aire") or {}).get(langue, "")


def horodatages(dernier: str, nb_max: int) -> list[str]:
    """Fichiers de 15 minutes a lire, du plus ancien au plus recent."""
    try:
        r = requests.get(URL_GDELT + "lastupdate.txt", timeout=30)
        recent = re.search(r"/(\d{14})\.", r.text).group(1)
    except Exception:  # noqa: BLE001
        return []
    t = datetime.strptime(recent, "%Y%m%d%H%M%S")
    debut = datetime.strptime(dernier, "%Y%m%d%H%M%S") + timedelta(minutes=15) if dernier else t - timedelta(hours=6)
    debut = max(debut, t - timedelta(minutes=15 * (nb_max - 1)))
    liste = []
    while debut <= t:
        liste.append(debut.strftime("%Y%m%d%H%M%S"))
        debut += timedelta(minutes=15)
    return liste


def lire_un_fichier_gkg(nom: str, conf: dict, pays_zone: dict) -> tuple[list[dict], str]:
    import io
    import zipfile
    try:
        r = requests.get(URL_GDELT + nom, timeout=120)
        if r.status_code == 404:
            return [], ""                       # fichier pas encore publie ou absent : normal
        r.raise_for_status()
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        brut = zf.read(zf.namelist()[0]).decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return [], f"{nom} : {type(e).__name__}"
    themes_ok = tuple(conf.get("themes", []))
    forts = tuple(conf.get("themes_forts", []))
    exclus = [m.lower() for m in conf.get("exclure_si_url_contient", [])]
    cibles = set(conf.get("aires_cibles", []))
    sortie = []
    for ligne in brut.split("\n"):
        c = ligne.split("\t")
        if len(c) < 27 or c[2] != "1":          # 1 = article web
            continue
        themes = [t for t in c[7].split(";") if t]
        utiles = [t for t in themes if t.startswith(themes_ok)]
        if len(utiles) < conf.get("themes_min", 2):
            continue
        fort = (not forts) or any(t.startswith(forts) for t in themes)
        url_min = c[4].lower()
        if exclus and any(m in url_min for m in exclus):
            continue
        titre = re.search(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", c[26], re.S)
        if not titre:
            continue
        m = re.search(r"srclc:(\w{3})", c[25])
        langue = LANGUES_ISO3.get(m.group(1), m.group(1)[:2]) if m else "en"
        aire = aire_du_domaine(c[3], langue, conf, pays_zone)
        if aire not in cibles:
            continue
        try:
            dpub = datetime.strptime(c[1][:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            dpub = ""
        sortie.append({
            "url": c[4], "titre_original": sans_html(titre.group(1))[:500], "date_publication": dpub,
            "langue": langue, "source_id": f"gdelt-{c[3]}", "source_nom": f"{c[3]} (via GDELT)",
            "type_source": "GDELT", "aire_source": aire, "ancrage": "LOCAL", "lien_pouvoir": "INCONNU",
            "_texte": "", "_score": len(utiles), "_fort": fort,
        })
    return sortie, ""


def lire_gdelt(conf: dict) -> tuple[list[dict], int, list[str]]:
    """Fichiers bruts GDELT (GKG 2.1, anglais et traduits), publies toutes les 15 minutes.

    Pas de limite de requetes. On garde les articles des aires cibles qui portent assez de
    themes utiles, au plus `max_par_aire` par passage (les plus riches en themes d'abord).
    """
    if str(conf.get("actif", "oui")).lower() != "oui":
        return [], 0, []
    zones = pd.read_csv(CONFIG / "zones_pays.csv", dtype=str, keep_default_na=False)
    pays_zone = dict(zip(zones["pays"], zones["zone"]))
    dernier = ETAT_GDELT.read_text().strip() if ETAT_GDELT.exists() else ""
    stamps = horodatages(dernier, conf.get("fichiers_max", 28))
    if not stamps:
        return [], 0, ["gdelt : liste des fichiers inaccessible"]
    noms = [f"{t}.gkg.csv.zip" for t in stamps] + [f"{t}.translation.gkg.csv.zip" for t in stamps]
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(lambda n: lire_un_fichier_gkg(n, conf, pays_zone), noms))
    articles, erreurs = [], [e for _, e in res if e]
    for arts, _ in res:
        articles += arts
    vus, uniques = set(), []
    for a in sorted(articles, key=lambda a: -a["_score"]):
        if a["url"] not in vus:
            vus.add(a["url"])
            uniques.append(a)
    # Par aire : une part "dans le champ" (themes forts, les plus riches d'abord) et une part
    # "libre", tiree au hasard, pour garder les evolutions de societe et les projets locaux.
    import random
    part_libre = conf.get("part_libre", 0.25)
    gardes = []
    for aire in {a["aire_source"] for a in uniques}:
        maxi = (conf.get("max_par_aire_specifique") or {}).get(aire, conf.get("max_par_aire", 40))
        dans_aire = [a for a in uniques if a["aire_source"] == aire]
        forts_a = [a for a in dans_aire if a["_fort"]]
        libres_a = [a for a in dans_aire if not a["_fort"]]
        n_libre = min(len(libres_a), round(maxi * part_libre))
        choix = forts_a[: maxi - n_libre]
        choix += random.sample(libres_a, min(len(libres_a), maxi - len(choix)))
        gardes += choix
    for a in gardes:
        del a["_score"], a["_fort"]
    if len(erreurs) < len(noms):
        ETAT_GDELT.write_text(stamps[-1])
    return gardes, len(noms), erreurs[:5]


def mesurer_page(url: str) -> int:
    """Longueur du texte lisible de la page. Le texte n'est jamais conserve."""
    try:
        import trafilatura
        brut = trafilatura.fetch_url(url)
        texte = trafilatura.extract(brut) if brut else None
        return len(texte or "")
    except Exception:  # noqa: BLE001
        return 0


# ---------------------------------------------------------------- stockage

class Stockage:
    """Fichiers mensuels fiches/AAAA-MM.parquet, sur Hugging Face ou en local."""

    def __init__(self):
        self.jeton = os.environ.get("HF_TOKEN", "").strip()
        self.depot = None
        if self.jeton:
            from huggingface_hub import HfApi
            self.api = HfApi(token=self.jeton)
            conf = lire_yaml("stockage.yaml")
            self.depot = conf.get("depot_hf") or f'{self.api.whoami()["name"]}/{conf["nom_par_defaut"]}'
            self.api.create_repo(self.depot, repo_type="dataset", private=True, exist_ok=True)
        else:
            LOCAL.mkdir(exist_ok=True)

    def lire(self, mois: str) -> pd.DataFrame:
        chemin = f"fiches/{mois}.parquet"
        try:
            if self.depot:
                from huggingface_hub import hf_hub_download
                fichier = hf_hub_download(self.depot, chemin, repo_type="dataset", token=self.jeton)
            else:
                fichier = LOCAL / chemin
                if not fichier.exists():
                    return pd.DataFrame(columns=COLONNES)
            return pd.read_parquet(fichier)
        except Exception as e:  # noqa: BLE001
            if "404" in str(e) or "EntryNotFound" in type(e).__name__:
                return pd.DataFrame(columns=COLONNES)
            raise

    def ecrire(self, tables: dict[str, pd.DataFrame], message: str):
        if self.depot:
            from huggingface_hub import CommitOperationAdd
            ops = []
            for mois, df in tables.items():
                tmp = Path("/tmp") / f"{mois}.parquet"
                df.to_parquet(tmp, index=False)
                ops.append(CommitOperationAdd(path_in_repo=f"fiches/{mois}.parquet", path_or_fileobj=str(tmp)))
            self.api.create_commit(self.depot, repo_type="dataset", operations=ops, commit_message=message)
        else:
            (LOCAL / "fiches").mkdir(exist_ok=True)
            for mois, df in tables.items():
                df.to_parquet(LOCAL / "fiches" / f"{mois}.parquet", index=False)


# ---------------------------------------------------------------- dedoublonnage

def dedoublonner(nouveaux: list[dict], existant: pd.DataFrame, seuils: dict) -> tuple[list[dict], dict]:
    """Retire les doublons ; incremente les reprises de la fiche gardee.

    Renvoie les articles a ajouter et des compteurs. `existant` est modifie sur place.
    """
    c = {"deja_connus": 0, "doublons_titre": 0}
    jours = seuils.get("titre_jours_doublon", 3)
    sim_min = seuils.get("titre_similarite_min", 0.8)
    limite = (MAINTENANT - timedelta(days=jours)).isoformat()

    urls = set()
    if len(existant):
        if "urls_reprises" not in existant:
            existant["urls_reprises"] = ""
        existant["urls_reprises"] = existant["urls_reprises"].fillna("")
        urls = set(existant["url_canonique"])
        for liste in existant["urls_reprises"]:
            urls.update(x for x in liste.split(" ") if x)
    # index des titres recents : mot -> positions
    recents = []          # (mots, ("ex", index) ou ("nv", position))
    index_mots: dict[str, list[int]] = {}

    def indexer(mots, cle):
        recents.append((mots, cle))
        for m in mots:
            index_mots.setdefault(m, []).append(len(recents) - 1)

    if len(existant):
        for i, ligne in existant[existant["date_collecte"] >= limite].iterrows():
            indexer(mots_titre(ligne["titre_original"]), ("ex", i))

    gardes: list[dict] = []
    vus_dans_le_passage = set()
    for a in sorted(nouveaux, key=lambda a: RANG_ANCRAGE.get(a["ancrage"], 9)):
        a["url_canonique"] = canoniser(a["url"])
        if a["url_canonique"] in urls or a["url_canonique"] in vus_dans_le_passage:
            c["deja_connus"] += 1
            continue
        vus_dans_le_passage.add(a["url_canonique"])
        mots = mots_titre(a["titre_original"])
        cible = None
        if len(mots) >= 3:
            compte: dict[int, int] = {}
            for m in mots:
                for k in index_mots.get(m, []):
                    compte[k] = compte.get(k, 0) + 1
            for k, communs in sorted(compte.items(), key=lambda x: -x[1]):
                autres = recents[k][0]
                if communs / len(mots | autres) >= sim_min:
                    cible = recents[k][1]
                break
        if cible is None:
            a["reprises"], a["sources_reprises"], a["urls_reprises"] = 0, "", ""
            gardes.append(a)
            indexer(mots, ("nv", len(gardes) - 1))
            continue
        c["doublons_titre"] += 1
        if cible[0] == "ex":
            ligne = existant.loc[cible[1]]
            existant.at[cible[1], "reprises"] = int(ligne["reprises"] or 0) + 1
            existant.at[cible[1], "sources_reprises"] = ";".join(
                x for x in [ligne["sources_reprises"], a["source_id"]] if x)
            existant.at[cible[1], "urls_reprises"] = " ".join(
                x for x in [ligne["urls_reprises"], a["url_canonique"]] if x)
        else:
            g = gardes[cible[1]]
            g["reprises"] += 1
            g["sources_reprises"] = ";".join(x for x in [g["sources_reprises"], a["source_id"]] if x)
            g["urls_reprises"] = " ".join(x for x in [g["urls_reprises"], a["url_canonique"]] if x)
    return gardes, c


def appliquer_plafond(articles: list[dict], existant: pd.DataFrame, plafonds: dict) -> tuple[list[dict], dict]:
    jour = MAINTENANT.date().isoformat()
    deja = {}
    if len(existant):
        du_jour = existant[existant["date_collecte"].str.startswith(jour)]
        deja = du_jour["aire_source"].value_counts().to_dict()
    gardes, ecartes = [], {}
    # les plus recents d'abord, ancrage local en priorite
    articles.sort(key=lambda a: (RANG_ANCRAGE.get(a["ancrage"], 9), a["date_publication"] or ""), reverse=False)
    articles.sort(key=lambda a: a["date_publication"] or "", reverse=True)
    for a in articles:
        aire = a["aire_source"]
        maxi = plafonds.get(aire, plafonds.get("defaut", 150))
        if deja.get(aire, 0) >= maxi:
            ecartes[aire] = ecartes.get(aire, 0) + 1
            continue
        deja[aire] = deja.get(aire, 0) + 1
        gardes.append(a)
    return gardes, ecartes


# ---------------------------------------------------------------- journal

def maj_suivi_sources(resultats: dict[str, tuple[int, str]], sources: pd.DataFrame, conf_src: dict) -> list[str]:
    """Met a jour journal/collecte_sources.csv ; desactive les sources en echec depuis 30 jours."""
    chemin = JOURNAL / "collecte_sources.csv"
    suivi = pd.read_csv(chemin, dtype=str).fillna("") if chemin.exists() else pd.DataFrame(
        columns=["id", "dernier_succes", "premier_echec", "derniere_erreur", "articles_dernier_passage", "statut"])
    suivi = suivi.set_index("id")
    aujourd_hui = MAINTENANT.date().isoformat()
    desactivees = []
    for sid, (n, err) in resultats.items():
        if sid not in suivi.index:
            suivi.loc[sid] = ["", "", "", "0", ""]
        if err:
            if not suivi.at[sid, "premier_echec"]:
                suivi.at[sid, "premier_echec"] = aujourd_hui
            suivi.at[sid, "derniere_erreur"] = err
            jours = (MAINTENANT.date() - datetime.fromisoformat(suivi.at[sid, "premier_echec"]).date()).days
            if jours >= conf_src.get("jours_avant_desactivation", 30):
                suivi.at[sid, "statut"] = "DESACTIVEE"
                desactivees.append(sid)
            elif jours >= conf_src.get("jours_avant_signalement", 7):
                suivi.at[sid, "statut"] = "SIGNALEE"
            else:
                suivi.at[sid, "statut"] = "ECHEC"
        else:
            suivi.at[sid, "dernier_succes"] = aujourd_hui
            suivi.at[sid, "premier_echec"] = ""
            suivi.at[sid, "derniere_erreur"] = ""
            suivi.at[sid, "statut"] = "OK"
        suivi.at[sid, "articles_dernier_passage"] = str(n)
    suivi.reset_index().rename(columns={"index": "id"}).to_csv(chemin, index=False)
    if desactivees:
        regs = pd.read_csv(CONFIG / "sources.csv", dtype=str).fillna("")
        masque = regs["id"].isin(desactivees) & (regs["actif"] == "oui")
        regs.loc[masque, "actif"] = "non"
        regs.loc[masque, "remarque"] = (regs.loc[masque, "remarque"] + f" | desactivee automatiquement le {aujourd_hui} (30 jours d'echec)").str.strip(" |")
        regs.to_csv(CONFIG / "sources.csv", index=False)
    return desactivees


def ecrire_journal(ligne: dict):
    chemin = JOURNAL / "executions.csv"
    df = pd.DataFrame([ligne])
    if chemin.exists():
        df = pd.concat([pd.read_csv(chemin, dtype=str), df.astype(str)], ignore_index=True)
    df.to_csv(chemin, index=False)


# ---------------------------------------------------------------- programme

def main():
    debut = time.time()
    JOURNAL.mkdir(exist_ok=True)
    seuils = lire_yaml("seuils.yaml")
    sc = seuils.get("collecte", {})
    global AGE_MAX_JOURS
    AGE_MAX_JOURS = sc.get("age_max_jours", 7)
    sources = pd.read_csv(CONFIG / "sources.csv", dtype=str).fillna("")
    actives = sources[(sources["actif"] == "oui") & sources["type"].isin(["RSS", "PERSONNE"])]
    journal = {"tache": "collecte", "debut": MAINTENANT.isoformat(timespec="seconds"), "erreurs": ""}
    erreurs: list[str] = []

    # 1. Flux RSS
    with ThreadPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(lire_flux, actives.to_dict("records")))
    bruts, resultats = [], {}
    for sid, arts, err in res:
        bruts += arts
        resultats[sid] = (len(arts), err)
    en_erreur = sorted(s for s, (_, e) in resultats.items() if e)

    # 2. GDELT pour les aires faibles
    gd, n_req, err_gd = lire_gdelt(lire_yaml("gdelt.yaml"))
    erreurs += err_gd
    bruts += gd

    # 3. Dedoublonnage contre le mois en cours et le precedent
    stock = Stockage()
    mois = MAINTENANT.strftime("%Y-%m")
    mois_prec = (MAINTENANT.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    tables = {m: stock.lire(m) for m in (mois_prec, mois)}
    existant = pd.concat([tables[mois_prec].assign(_mois=mois_prec), tables[mois].assign(_mois=mois)],
                         ignore_index=True)
    avant_reprises = existant["reprises"].astype(float).sum() if len(existant) else 0
    nouveaux, compteurs = dedoublonner(bruts, existant, sc)

    # 4. Plafond par aire
    nouveaux, ecartes = appliquer_plafond(nouveaux, existant, sc.get("plafond_par_aire_jour", {"defaut": 150}))

    # 5. Mesure du texte disponible (texte jete aussitot)
    seuil_txt = sc.get("texte_min_flux", 500)
    a_lire = [a for a in nouveaux if len(a["_texte"]) < seuil_txt][: sc.get("pages_max_par_passage", 300)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        longueurs = dict(zip([a["url"] for a in a_lire], ex.map(mesurer_page, [a["url"] for a in a_lire])))
    for a in nouveaux:
        lf = len(a["_texte"])
        lp = longueurs.get(a["url"], 0)
        if lf >= seuil_txt or lf >= lp:
            a["longueur_texte"], a["texte_source"] = lf, ("FLUX" if lf else "TITRE")
        else:
            a["longueur_texte"], a["texte_source"] = lp, "PAGE"
        a["extrait"] = a["_texte"][: sc.get("extrait_max", 280)]
        del a["_texte"]

    # 6. Numerotation et ecriture
    jour = MAINTENANT.strftime("%Y%m%d")
    deja = existant["id"].astype(str).str.startswith(f"F-{jour}").sum() if len(existant) else 0
    for k, a in enumerate(nouveaux, start=deja + 1):
        a["id"] = f"F-{jour}-{k:04d}"
        a["date_collecte"] = MAINTENANT.isoformat(timespec="seconds")
        a["classe"] = False
    ajout = pd.DataFrame(nouveaux, columns=COLONNES)
    modifie_prec = len(existant) and existant["reprises"].astype(float).sum() != avant_reprises
    sorties = {}
    for m in (mois_prec, mois):
        part = existant[existant["_mois"] == m].drop(columns="_mois")
        if m == mois:
            part = pd.concat([part, ajout], ignore_index=True)
        if m == mois or modifie_prec:
            if len(part):
                part["reprises"] = part["reprises"].astype(int)
                sorties[m] = part[COLONNES]
    if len(ajout) or modifie_prec:
        stock.ecrire(sorties, f"Collecte du {MAINTENANT:%Y-%m-%d %H:%M} : {len(ajout)} fiches")

    # 7. Bilan du stock du mois (lisible sans acces a Hugging Face)
    stock_mois = sorties.get(mois, existant[existant["_mois"] == mois])
    if len(stock_mois):
        bilan = (stock_mois.assign(origine=stock_mois["type_source"].where(stock_mois["type_source"] == "GDELT", "RSS"))
                 .groupby(["origine", "aire_source"]).size().rename("fiches").reset_index())
        bilan.insert(0, "mois", mois)
        bilan.to_csv(JOURNAL / "stock_du_mois.csv", index=False)
    gd_ajout = ajout[ajout["type_source"] == "GDELT"] if len(ajout) else ajout
    journal["gdelt_enregistres"] = len(gd_ajout)

    # 8. Journal
    desactivees = maj_suivi_sources(resultats, sources, seuils.get("sources", {}))
    journal.update({
        "fin": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duree_s": round(time.time() - debut),
        "sources_lues": len(actives), "sources_ok": len(actives) - len(en_erreur),
        "sources_erreur": len(en_erreur), "liste_sources_erreur": ";".join(en_erreur),
        "gdelt_requetes": n_req, "gdelt_articles": len(gd),
        "articles_vus": len(bruts), **compteurs,
        "ecartes_plafond": sum(ecartes.values()),
        "detail_plafond": ";".join(f"{k}:{v}" for k, v in sorted(ecartes.items())),
        "nouveaux": len(ajout), "pages_lues": len(a_lire),
        "stockage": stock.depot or "local",
        "sources_desactivees": ";".join(desactivees),
        "erreurs": " | ".join(erreurs)[:500],
    })
    ecrire_journal(journal)
    print(json.dumps(journal, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001 : l'echec est inscrit au journal avant de remonter
        JOURNAL.mkdir(exist_ok=True)
        ecrire_journal({"tache": "collecte", "debut": MAINTENANT.isoformat(timespec="seconds"),
                        "fin": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "erreurs": f"ECHEC : {type(e).__name__} : {e}"[:500]})
        raise
