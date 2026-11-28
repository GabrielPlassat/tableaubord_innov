"""Agent A0 (Sprint 4) : etiquetage des sujets par Opus, en traitement differe (Batch).

Chaque lundi : pour les sujets de la semaine (sujets/groupes.parquet, calcules la nuit),
Opus lit jusqu'a 15 fiches par sujet et rend axe et pole par aire, precipitation, rebond,
levier, et comment chaque aire raconte le sujet. Consigne : config/consignes/a0_sujets_v1.txt.

Sorties : sujets/etiquettes.parquet (+ copie datee) sur Hugging Face ;
journal/etiquettes_bilan.csv et journal/couts.csv dans le depot.
Garde-fou : le cout du mois (journal/couts.csv) ne depasse jamais config/budget.yaml > arret_dollars.
Secrets : HF_TOKEN, ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import collecte as C  # noqa: E402
from classement import extraire_json  # noqa: E402

MAINTENANT = datetime.now(timezone.utc)
RACINE = C.RACINE
JOURNAL = C.JOURNAL
EN_ATTENTE = JOURNAL / "batch_en_attente.json"


def ecrire_bilan(ligne: dict):
    """journal/agents.csv : un fichier a part, pour ne pas croiser les ecritures de la collecte."""
    f = JOURNAL / "agents.csv"
    d = pd.DataFrame([ligne]).astype(str)
    if f.exists():
        d = pd.concat([pd.read_csv(f, dtype=str), d], ignore_index=True)
    d.to_csv(f, index=False)


# ---------------------------------------------------------------- couts

def tarifs():
    b = C.lire_yaml("budget.yaml")
    return b, b.get("tarifs", {}), b.get("reduction_batch", 0.5)


def cout_du_mois() -> float:
    f = JOURNAL / "couts.csv"
    if not f.exists():
        return 0.0
    d = pd.read_csv(f, dtype={"date": str})
    return float(d[d["date"].str.startswith(MAINTENANT.strftime("%Y-%m"))]["cout_dollars"].sum())


def noter_cout(tache: str, modele: str, usage: dict, batch: bool, ref: str = ""):
    _, t, red = tarifs()
    p = t.get(modele, {"entree": 4.0, "sortie": 20.0, "cache_lu": 0.2, "cache_ecrit": 5.0})
    k = red if batch else 1.0
    cout = k * (usage["entree"] * p["entree"] + usage["sortie"] * p["sortie"]
                + usage["cache_lu"] * p["cache_lu"] + usage["cache_ecrit"] * p["cache_ecrit"]) / 1e6
    f = JOURNAL / "couts.csv"
    if ref and f.exists() and ref in f.read_text():
        return cout                               # deja compte (traitement recupere une seconde fois)
    ligne = pd.DataFrame([{"date": MAINTENANT.isoformat(timespec="seconds"), "tache": tache, "modele": modele,
                           "batch": batch, **usage, "cout_dollars": round(cout, 4), "ref": ref}])
    ligne.to_csv(f, mode="a", header=not f.exists(), index=False)
    return cout


# ---------------------------------------------------------------- preparation

def lire_hf(stock, chemin):
    from huggingface_hub import hf_hub_download
    return pd.read_parquet(hf_hub_download(stock.depot, chemin, repo_type="dataset", token=stock.jeton))


def choisir_fiches(x: pd.DataFrame, n: int) -> pd.DataFrame:
    """Jusqu'a n fiches, les plus variees en aires de source, celles qui ont une fiche d'abord."""
    x = x.assign(_a_fiche=x["classe"].astype(str).str.lower().eq("true")).sort_values(
        ["_a_fiche", "date_collecte"], ascending=[False, False])
    x = x.assign(_rang=x.groupby("aire_source").cumcount()).sort_values(["_rang", "_a_fiche"], ascending=[True, False])
    return x.head(n)


def message_sujet(x: pd.DataFrame) -> str:
    lignes = []
    for _, r in x.iterrows():
        titre = r["titre_fr"] or r["titre_original"]
        corps = r["resume"] or r["extrait"] or ""
        lignes.append(f"[{r['id']}] source {r['source_nom']} · aire {r['aire_source']} · langue {r['langue']} · "
                      f"lien au pouvoir {r['lien_pouvoir'] or 'INCONNU'} · nature {r['nature'] or '?'}\n"
                      f"{titre}\n{corps}".strip())
    return "FICHES DU SUJET\n\n" + "\n\n".join(lignes)


# ---------------------------------------------------------------- programme

def main():
    import anthropic
    budget, _, _ = tarifs()
    conf = C.lire_yaml("seuils.yaml").get("agents", {})
    modele = C.lire_yaml("modeles.yaml")["claude"].get("etiquettes_agents", "claude-opus-5-5")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    stock = C.Stockage()
    JOURNAL.mkdir(exist_ok=True)
    bilan = {"tache": "etiquetage_sujets", "debut": MAINTENANT.isoformat(timespec="seconds")}

    if EN_ATTENTE.exists():                       # un traitement lance la semaine passee, pas encore recupere
        attente = json.loads(EN_ATTENTE.read_text())
        batch_id, entrees = attente["batch_id"], pd.DataFrame(attente["sujets"])
        bilan["reprise"] = batch_id
    else:
        deja = cout_du_mois()
        if deja >= budget.get("arret_dollars", 60):
            bilan["erreurs"] = f"arret : {deja:.2f} $ deja depenses ce mois-ci"
            ecrire_bilan(bilan)
            print(bilan)
            return
        groupes = lire_hf(stock, "sujets/groupes.parquet")
        groupes = groupes[(groupes["taille"] >= conf.get("sujet_taille_min", 5))
                          | (groupes["nb_aires_source"] >= conf.get("sujet_aires_min", 2))]
        groupes = groupes.sort_values(["nb_aires_source", "taille"], ascending=False)
        # combien de sujets le budget permet (environ 0,02 $ chacun en traitement differe)
        marge = budget.get("arret_dollars", 60) - deja
        n_max = min(conf.get("sujets_par_semaine", 120), int(marge / 0.03))
        groupes = groupes.head(n_max)
        mois = MAINTENANT.strftime("%Y-%m")
        mois_prec = (MAINTENANT.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        fiches = pd.concat([stock.lire(m) for m in (mois_prec, mois)], ignore_index=True)
        fiches = fiches.reindex(columns=C.COLONNES).fillna("")
        fiches = fiches.set_index("id", drop=False)
        consigne = (RACINE / "config" / "consignes" / "a0_sujets_v1.txt").read_text(encoding="utf-8")
        requetes, sujets = [], []
        for k, g in enumerate(groupes.itertuples()):
            ids = [i for i in g.ids.split(";") if i in fiches.index]
            if len(ids) < 3:
                continue
            x = choisir_fiches(fiches.loc[ids], conf.get("fiches_par_sujet", 15))
            cid = f"s{k:04d}"
            requetes.append({"custom_id": cid, "params": {
                "model": modele, "max_tokens": 2500,
                "system": [{"type": "text", "text": consigne, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": message_sujet(x)}]}})
            sujets.append({"custom_id": cid, "groupe": g.groupe, "taille": int(g.taille),
                           "nb_aires_source": int(g.nb_aires_source), "aires_source": g.aires_source,
                           "langues": g.langues, "ids": g.ids, "fiches_lues": ";".join(x["id"])})
        if not requetes:
            bilan["erreurs"] = "aucun sujet a etiqueter"
            ecrire_bilan(bilan)
            return
        batch = client.messages.batches.create(requests=requetes)
        batch_id, entrees = batch.id, pd.DataFrame(sujets)
        EN_ATTENTE.write_text(json.dumps({"batch_id": batch_id, "sujets": sujets}, ensure_ascii=False))
        bilan["envoyes"] = len(requetes)
        print(f"Traitement differe {batch_id} : {len(requetes)} sujets envoyes", flush=True)

    # attente du resultat
    fin = time.time() + 60 * conf.get("attente_batch_minutes", 150)
    while True:
        b = client.messages.batches.retrieve(batch_id)
        if b.processing_status == "ended":
            break
        if time.time() > fin:
            bilan["erreurs"] = f"traitement {batch_id} non termine : recupere au prochain passage"
            ecrire_bilan(bilan)
            print(bilan)
            return
        time.sleep(60)

    usage = {"entree": 0, "sortie": 0, "cache_lu": 0, "cache_ecrit": 0}
    resultats = {}
    for r in client.messages.batches.results(batch_id):
        if r.result.type != "succeeded":
            continue
        m = r.result.message
        u = m.usage
        usage["entree"] += u.input_tokens or 0
        usage["sortie"] += u.output_tokens or 0
        usage["cache_lu"] += getattr(u, "cache_read_input_tokens", 0) or 0
        usage["cache_ecrit"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        resultats[r.custom_id] = extraire_json("".join(c.text for c in m.content if c.type == "text"))
    cout = noter_cout("etiquetage_sujets", modele, usage, batch=True, ref=batch_id)

    lignes = []
    for s in entrees.to_dict("records"):
        e = resultats.get(s["custom_id"])
        if not e:
            continue
        ax = e.get("axes") or []
        pr = e.get("precipitation") or {}
        rb = e.get("rebond") or {}
        lv = e.get("levier") or {}
        lignes.append({**{k: v for k, v in s.items() if k != "custom_id"},
                       "date_etiquetage": MAINTENANT.date().isoformat(), "modele": modele, "consigne": "a0_sujets_v1",
                       "sujet_coherent": bool(e.get("sujet_coherent", True)), "titre": e.get("titre", ""),
                       "resume": e.get("resume", ""), "angle_mort": e.get("angle_mort") or "",
                       "lectures_par_aire": json.dumps(e.get("lectures_par_aire") or [], ensure_ascii=False),
                       "lentille_principale": e.get("lentille_principale") or "",
                       "lentille_secondaire": e.get("lentille_secondaire") or "",
                       "iceberg": e.get("iceberg") or "", "horizon": e.get("horizon") or "",
                       "axes": json.dumps(ax, ensure_ascii=False),
                       "axe1": ax[0].get("code", "") if ax else "", "pole1": ax[0].get("pole", "") if ax else "",
                       "tension_libre": e.get("tension_libre") or "",
                       "precipitation": pr.get("signal") or "AUCUN", "precipitation_detail": json.dumps(pr, ensure_ascii=False),
                       "rebond": rb.get("statut") or "NON_MENTIONNE", "rebond_detail": json.dumps(rb, ensure_ascii=False),
                       "levier_famille": lv.get("famille") or "AUCUN", "meadows": lv.get("meadows") or "",
                       "candidat_cas": bool(e.get("candidat_cas", False)),
                       "confiance": e.get("confiance") or "", "raison_confiance": e.get("raison_confiance") or "",
                       "ce_qu_on_ne_sait_pas": e.get("ce_qu_on_ne_sait_pas") or ""})
    et = pd.DataFrame(lignes)
    for col in et.columns:                         # le modele renvoie parfois un nombre la ou on attend du texte
        if et[col].dtype == object:
            et[col] = et[col].map(lambda v: "" if v is None else (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else str(v)))
    if len(et):
        from huggingface_hub import CommitOperationAdd
        tmp = Path("/tmp/etiquettes.parquet")
        et.to_parquet(tmp, index=False)
        ops = [CommitOperationAdd(path_in_repo="sujets/etiquettes.parquet", path_or_fileobj=str(tmp)),
               CommitOperationAdd(path_in_repo=f"sujets/etiquettes_{MAINTENANT:%Y-%m-%d}.parquet", path_or_fileobj=str(tmp))]
        stock.api.create_commit(stock.depot, repo_type="dataset", operations=ops,
                                commit_message=f"Etiquetage de {len(et)} sujets par {modele}")
        et.drop(columns=["ids", "fiches_lues"]).to_csv(JOURNAL / "etiquettes_bilan.csv", index=False)
    EN_ATTENTE.unlink(missing_ok=True)
    bilan.update({"etiquetes": len(et), "echecs": len(entrees) - len(et), "cout_dollars": round(cout, 3),
                  "cout_mois_dollars": round(cout_du_mois(), 2),
                  "fin": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    if len(et):
        bilan["axes"] = ";".join(f"{k}:{v}" for k, v in et["axe1"].replace("", "aucun").value_counts().items())
        bilan["precipitations"] = ";".join(f"{k}:{v}" for k, v in et["precipitation"].value_counts().items())
        bilan["candidats_cas"] = int(et["candidat_cas"].sum())
    ecrire_bilan(bilan)
    print(json.dumps(bilan, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
