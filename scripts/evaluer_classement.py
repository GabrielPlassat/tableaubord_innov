"""Evaluation du classement d'Albert sur le jeu de reference de 100 articles (Sprint 3).
# Relance : 16/11/2026, secret ALBERT_API_KEY ajouté.

Compare : tri article par article (consigne v1 et v2) et tri par lots de 20 (v2), avec le
modele de tri ; fiche (passe 2, consigne v3) avec le modele de fiche, sur tous les articles.
Texte : la page lue depuis GitHub, sinon le titre seul (comme dans la collecte).

Sorties : journal/evaluation_sprint3.csv (detail) et docs/evaluation-sprint3.md (bilan).
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from classement import Albert, ficher, modeles, trier_lot, trier_un  # noqa: E402

RACINE = Path(__file__).resolve().parents[1]


def lire_page(url: str) -> str:
    try:
        import trafilatura
        brut = trafilatura.fetch_url(url)
        return (trafilatura.extract(brut) or "") if brut else ""
    except Exception:  # noqa: BLE001
        return ""


def accepte(valeur, attendu: str) -> bool:
    """La valeur (ou l'une des valeurs) du modele est-elle parmi les reponses acceptables ?"""
    ok = set(str(attendu).split("|"))
    if isinstance(valeur, (list, tuple)):
        return any(v in ok for v in valeur)
    return str(valeur) in ok


def main():
    ref = pd.read_csv(RACINE / "tests" / "reference_100.csv", dtype=str).fillna("")
    albert = Albert()
    m = modeles()
    lignes = []
    print("Lecture des pages…", flush=True)
    textes = {r.num: lire_page(r.url) for r in ref.itertuples()}
    print(f"{sum(len(t) > 200 for t in textes.values())} pages lues sur {len(ref)}", flush=True)

    # Tri par lots (v2)
    t0 = time.time()
    lots = trier_lot(albert, [(r.titre_original, textes[r.num][:200]) for r in ref.itertuples()])
    duree_lot = time.time() - t0

    for k, r in enumerate(ref.itertuples()):
        texte = textes[r.num]
        l = {"num": r.num, "titre": r.titre[:80], "pertinent_ref": r.pertinent, "texte_lu": len(texte),
             "tri_lot_v2": lots[k]}
        t0 = time.time()
        for v in ("v1", "v2"):
            try:
                l[f"tri_{v}"] = trier_un(albert, r.titre_original, texte[:500], v)
            except Exception as e:  # noqa: BLE001
                l[f"tri_{v}"] = "ERREUR"
                l["erreur"] = str(e)[:120]
        l["duree_tri_s"] = round((time.time() - t0) / 2, 1)
        t0 = time.time()
        try:
            f, modele = ficher(albert, r.titre_original, r.langue, texte)
            l["modele_fiche"] = modele
            l["json_valide"] = f is not None
            if f:
                l.update({"lentille_principale": f.get("lentille_principale") or "",
                          "lentille_secondaire": f.get("lentille_secondaire") or "",
                          "iceberg": f.get("iceberg") or "", "aire_sujet": ";".join(f["aire_sujet"]),
                          "nature": f.get("nature") or "", "confiance": f.get("confiance"),
                          "titre_fr": f.get("titre_fr", ""), "resume": f.get("resume", "")})
        except Exception as e:  # noqa: BLE001
            l["json_valide"] = False
            l["erreur"] = str(e)[:120]
        l["duree_fiche_s"] = round(time.time() - t0, 1)
        lignes.append(l)
        print(k + 1, r.titre[:50], l.get("tri_v2"), l.get("lentille_principale"), flush=True)

    d = pd.DataFrame(lignes)
    (RACINE / "journal").mkdir(exist_ok=True)
    d.to_csv(RACINE / "journal" / "evaluation_sprint3.csv", index=False)
    c = ref.merge(d, on="num")

    # ---- tri : un OUI (ou DOUTE) sur un article attendu OUI, un NON sur un attendu NON
    def score_tri(col):
        def bon(row):
            v = "OUI" if row[col] in ("OUI", "DOUTE") else row[col]
            return v in row["pertinent"].split("|")
        oui = c[c["pertinent"] == "OUI"]
        non = c[c["pertinent"] == "NON"]
        return {"accord (cas ouverts comptés justes)": c.apply(bon, axis=1).mean(),
                "OUI retrouvés (rappel)": oui[col].isin(["OUI", "DOUTE"]).mean(),
                "NON écartés": (non[col] == "NON").mean(),
                "réponses illisibles": (c[col].isin(["ILLISIBLE", "ERREUR"])).mean()}
    tri = pd.DataFrame({"article par article, v1": score_tri("tri_v1"),
                        "article par article, v2": score_tri("tri_v2"),
                        "par lots de 20, v2": score_tri("tri_lot_v2")})

    # ---- fiche : sur les articles qui ont des etiquettes
    e = c[c["lentille_principale_x"].astype(bool)].copy()

    def champ(col_ref, col_mod, plusieurs=False):
        return e.apply(lambda r: accepte(r[col_mod].split(";") if plusieurs else r[col_mod], r[col_ref]), axis=1).mean()
    fiche = pd.Series({
        "JSON valide": c["json_valide"].mean(),
        "lentille principale": champ("lentille_principale_x", "lentille_principale_y"),
        "lentille principale ou secondaire": e.apply(
            lambda r: accepte([r["lentille_principale_y"], r["lentille_secondaire"]], r["lentille_principale_x"]), axis=1).mean(),
        "iceberg": champ("iceberg_x", "iceberg_y"),
        "aire du sujet": champ("aire_sujet_x", "aire_sujet_y", plusieurs=True),
        "nature": champ("nature_x", "nature_y"),
    })
    pages = (d["texte_lu"] > 200).mean()

    md = [f"# Évaluation du classement (Sprint 3)\n",
          f"*{datetime.now(timezone.utc):%d/%m/%Y %H:%M} UTC · jeu de référence de {len(ref)} articles · "
          f"pages lues : {pages:.0%} · appels à Albert : {albert.appels}*\n",
          f"Modèle de tri : `{m['tri']}` · modèle de fiche : `{m['fiche']}` · consignes : passe1 v1, v2, lot v2 ; passe2 v3.\n",
          "## Tri (passe 1)\n", (tri * 100).round(0).astype(int).astype(str).add(" %").to_markdown(), "\n",
          f"Durée moyenne : {d['duree_tri_s'].mean():.1f} s par article et par consigne ; "
          f"par lots : {duree_lot:.0f} s pour les {len(ref)} articles.\n",
          f"## Fiche (passe 2), sur les {len(e)} articles étiquetés\n",
          (fiche * 100).round(0).astype(int).astype(str).add(" %").to_frame("accord").to_markdown(), "\n",
          f"Durée moyenne : {d['duree_fiche_s'].mean():.1f} s par fiche. Seuils visés (L2) : lentille 80 %, "
          "iceberg 65 %, aire 90 %, nature 80 %, JSON 98 %.\n",
          "Détail article par article : `journal/evaluation_sprint3.csv`.\n"]
    (RACINE / "docs" / "evaluation-sprint3.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
