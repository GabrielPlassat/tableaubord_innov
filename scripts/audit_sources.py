"""Audit des sources : teste chaque flux de config/sources.csv.

Pour chaque source active : telecharge le flux, compte les articles, note la date du
plus recent. Ecrit journal/audit_sources.csv (un etat par source) et met a jour la
colonne dernier_succes de config/sources.csv.

Lance par GitHub Actions (.github/workflows/audit_sources.yml). Peut aussi tourner
dans Colab : !python scripts/audit_sources.py
"""
import csv
import datetime as dt
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import feedparser
import requests

RACINE = Path(__file__).resolve().parents[1]
REGISTRE = RACINE / "config" / "sources.csv"
JOURNAL = RACINE / "journal" / "audit_sources.csv"
ENTETES = {"User-Agent": "Mozilla/5.0 (compatible; InnovationRadar/2.0; +https://github.com/GabrielPlassat/tableaubord_innov)"}
AUJOURDHUI = dt.date.today().isoformat()


def tester(source):
    debut = time.time()
    res = {"id": source["id"], "nom": source["nom"], "url": source["url"],
           "aire_source": source["aire_source"], "langue": source["langue"],
           "date_audit": AUJOURDHUI, "statut": "", "code_http": "",
           "nb_articles": 0, "dernier_article": "", "message": "", "duree_s": 0}
    try:
        r = requests.get(source["url"], headers=ENTETES, timeout=25)
        res["code_http"] = r.status_code
        if r.status_code >= 400:
            res["statut"], res["message"] = "ERREUR", f"HTTP {r.status_code}"
        else:
            flux = feedparser.parse(r.content)
            n = len(flux.entries)
            res["nb_articles"] = n
            dates = []
            for e in flux.entries:
                t = e.get("published_parsed") or e.get("updated_parsed")
                if t:
                    dates.append(dt.date(t.tm_year, t.tm_mon, t.tm_mday))
            if dates:
                res["dernier_article"] = max(dates).isoformat()
            if n == 0:
                res["statut"] = "VIDE"
                res["message"] = "Aucun article lisible (page qui n'est pas un flux ?)"
            elif dates and (dt.date.today() - max(dates)).days > 90:
                res["statut"] = "ENDORMI"
                res["message"] = "Dernier article de plus de 90 jours"
            else:
                res["statut"] = "OK"
    except Exception as exc:  # reseau, delai, certificat
        res["statut"], res["message"] = "ERREUR", type(exc).__name__ + ": " + str(exc)[:150]
    res["duree_s"] = round(time.time() - debut, 1)
    return res


def main():
    with REGISTRE.open(encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        colonnes = lecteur.fieldnames
        sources = list(lecteur)
    actives = [s for s in sources if s.get("actif", "oui").strip().lower() == "oui"
               and s.get("type") in ("RSS", "PERSONNE")]
    with ThreadPoolExecutor(max_workers=8) as pool:
        resultats = list(pool.map(tester, actives))

    JOURNAL.parent.mkdir(exist_ok=True)
    with JOURNAL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(resultats[0].keys()))
        w.writeheader()
        w.writerows(resultats)

    ok = {r["id"] for r in resultats if r["statut"] == "OK"}
    for s in sources:
        if s["id"] in ok:
            s["dernier_succes"] = AUJOURDHUI
    with REGISTRE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colonnes)
        w.writeheader()
        w.writerows(sources)

    bilan = {}
    for r in resultats:
        bilan[r["statut"]] = bilan.get(r["statut"], 0) + 1
    print(f"{len(resultats)} sources testees :", bilan)


if __name__ == "__main__":
    main()
