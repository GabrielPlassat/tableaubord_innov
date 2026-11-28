"""Travail de nuit (Sprint 3) : rattrapage du classement, vecteurs, sujets.

1. Tri (par lots) des articles du mois qui n'ont pas encore ete tries (stock d'avant le classement).
2. Fiches pour les articles pertinents restes sans fiche (3 derniers jours), dans la limite du
   quota du jour ; la page est relue pour l'occasion, puis le texte est jete.
3. Vecteurs (bge-m3 sur Albert) pour les articles pertinents : vecteurs/AAAA-MM.parquet.
4. Sujets : regroupement des articles des 14 derniers jours dont les vecteurs sont tres proches,
   quelle que soit leur langue. sujets/groupes.parquet et journal/sujets_bilan.csv.

Reglages : config/seuils.yaml, sections "classement" et "sujets".
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import collecte as C  # noqa: E402  (stockage, lecture des pages, colonnes)
from classement import Albert, ficher, modeles, trier_lot  # noqa: E402

MAINTENANT = datetime.now(timezone.utc)
JOURNAL = C.JOURNAL


def lire_vecteurs(stock, mois: str) -> pd.DataFrame:
    chemin = f"vecteurs/{mois}.parquet"
    try:
        if stock.depot:
            from huggingface_hub import hf_hub_download
            return pd.read_parquet(hf_hub_download(stock.depot, chemin, repo_type="dataset", token=stock.jeton))
        f = C.LOCAL / chemin
        return pd.read_parquet(f) if f.exists() else pd.DataFrame(columns=["id", "vecteur"])
    except Exception as e:  # noqa: BLE001
        if "404" in str(e) or "EntryNotFound" in type(e).__name__:
            return pd.DataFrame(columns=["id", "vecteur"])
        raise


def ecrire_fichiers(stock, fichiers: dict[str, pd.DataFrame], message: str):
    """fichiers = {chemin dans le depot : tableau}."""
    if stock.depot:
        from huggingface_hub import CommitOperationAdd
        ops = []
        for chemin, df in fichiers.items():
            tmp = Path("/tmp") / chemin.replace("/", "_")
            df.to_parquet(tmp, index=False)
            ops.append(CommitOperationAdd(path_in_repo=chemin, path_or_fileobj=str(tmp)))
        stock.api.create_commit(stock.depot, repo_type="dataset", operations=ops, commit_message=message)
    else:
        for chemin, df in fichiers.items():
            (C.LOCAL / chemin).parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(C.LOCAL / chemin, index=False)


def texte_pour_vecteur(r) -> str:
    titre = r["titre_fr"] or r["titre_original"]
    corps = r["resume"] or r["extrait"]
    return f"{titre}. {corps}"[:2000]


def sujets(df: pd.DataFrame, vec: pd.DataFrame, conf: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Regroupe les articles dont les vecteurs sont proches (similarite cosinus >= seuil),
    par composantes connexes. Renvoie (groupes, appartenance)."""
    seuil = conf.get("similarite_min", 0.85)
    limite = (MAINTENANT - timedelta(days=conf.get("fenetre_jours", 14))).isoformat()
    d = df[(df["date_collecte"] >= limite) & (df["tri"] != "NON")].merge(vec, on="id")
    if len(d) < 2:
        return pd.DataFrame(), pd.DataFrame()
    m = np.vstack(d["vecteur"].to_numpy()).astype(np.float32)
    m /= np.linalg.norm(m, axis=1, keepdims=True) + 1e-9
    n = len(m)
    parent = list(range(n))

    def racine(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for debut in range(0, n, 1000):
        sim = m[debut:debut + 1000] @ m.T
        lignes, cols = np.nonzero(sim >= seuil)
        for a, b in zip(lignes + debut, cols):
            if a < b:
                ra, rb = racine(a), racine(b)
                if ra != rb:
                    parent[rb] = ra
    comp = np.array([racine(i) for i in range(n)])
    # Les composantes connexes enchainent les ressemblances de proche en proche (A ressemble a B,
    # B a C...) : un gros groupe peut reunir plusieurs histoires. On redecoupe les gros groupes par
    # un regroupement "moyen", ou chaque article doit ressembler a l'ensemble du groupe.
    from sklearn.cluster import AgglomerativeClustering
    groupe = comp.copy()
    prochain = n
    for c in np.unique(comp):
        membres = np.nonzero(comp == c)[0]
        if len(membres) <= conf.get("taille_sans_controle", 12):
            continue
        ac = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average",
                                     distance_threshold=1 - conf.get("similarite_moyenne_min", 0.80))
        etiquettes = ac.fit_predict(m[membres])
        for e in np.unique(etiquettes):
            groupe[membres[etiquettes == e]] = prochain
            prochain += 1
    d["groupe"] = groupe
    taille = d.groupby("groupe")["id"].transform("count")
    d = d[taille >= conf.get("taille_min", 3)]
    if d.empty:
        return pd.DataFrame(), pd.DataFrame()
    groupes = []
    for g, x in d.groupby("groupe"):
        x = x.sort_values("date_collecte")
        groupes.append({
            "groupe": f"S-{MAINTENANT:%Y%m%d}-{int(g):05d}", "taille": len(x),
            "nb_aires_source": x["aire_source"].nunique(), "aires_source": ";".join(sorted(x["aire_source"].unique())),
            "aires_sujet": ";".join(sorted({a for s in x["aire_sujet"] for a in str(s).split(";") if a})),
            "langues": ";".join(sorted(x["langue"].unique())), "nb_sources": x["source_id"].nunique(),
            "lentilles": ";".join(x["lentille_principale"].replace("", np.nan).dropna().value_counts().index[:3]),
            "titre": (x["titre_fr"].replace("", np.nan).dropna().tolist() or x["titre_original"].tolist())[0],
            "titres": " | ".join((x["titre_fr"].where(x["titre_fr"] != "", x["titre_original"])).head(6)),
            "premier": x["date_collecte"].iloc[0], "dernier": x["date_collecte"].iloc[-1],
            "ids": ";".join(x["id"]),
        })
    gr = pd.DataFrame(groupes).sort_values(["nb_aires_source", "taille"], ascending=False)
    correspondance = {g: f"S-{MAINTENANT:%Y%m%d}-{int(g):05d}" for g in d["groupe"].unique()}
    app = d[["id"]].assign(groupe=d["groupe"].map(correspondance))
    return gr, app


def main():
    debut = time.time()
    seuils = C.lire_yaml("seuils.yaml")
    cc, cs = seuils.get("classement", {}), seuils.get("sujets", {})
    bilan = {"tache": "rattrapage", "debut": MAINTENANT.isoformat(timespec="seconds")}
    stock = C.Stockage()
    albert = Albert()
    mois = MAINTENANT.strftime("%Y-%m")
    mois_prec = (MAINTENANT.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    tables = {m: stock.lire(m).reindex(columns=C.COLONNES) for m in (mois_prec, mois)}
    for t in tables.values():
        t["classe"] = t["classe"].astype(str).str.lower().eq("true")
        for col in C.COLONNES[C.COLONNES.index("tri"):]:
            t[col] = t[col].map(lambda v: "" if v is None or (isinstance(v, float) and v != v) else str(v))

    # 1. Tri du stock non trie (mois en cours)
    df = tables[mois]
    a_trier = df.index[df["tri"] == ""][: cc.get("tri_rattrapage_max", 6000)]
    if len(a_trier):
        res = trier_lot(albert, list(zip(df.loc[a_trier, "titre_original"], df.loc[a_trier, "extrait"])))
        df.loc[a_trier, "tri"] = res
    bilan["tries"] = len(a_trier)

    # 2. Fiches restees en attente, dans la limite du quota du jour
    jour = MAINTENANT.date().isoformat()
    deja = sum(t["date_classement"].str.startswith(jour).sum() for t in tables.values())
    reste = max(0, cc.get("fiches_par_jour", 700) - deja)
    limite = (MAINTENANT - timedelta(days=3)).isoformat()
    attente = df[(df["tri"].isin(["OUI", "DOUTE"])) & (df["classe"].astype(str).str.lower() != "true") & (df["date_collecte"] >= limite)]
    # a part egale entre les aires, les plus recents d'abord
    attente = attente.sort_values("date_collecte", ascending=False)
    attente = attente.assign(rang=attente.groupby("aire_source").cumcount()).sort_values("rang").head(reste)
    version = modeles().get("consigne_fiche", "v3")

    def une(i):
        r = df.loc[i]
        texte = C.lire_page(r["url"]) or r["extrait"]
        try:
            return i, ficher(albert, r["titre_original"], r["langue"], texte)
        except Exception as e:  # noqa: BLE001
            return i, (None, str(e)[:80])
    faites = 0
    with ThreadPoolExecutor(max_workers=cc.get("fils", 3)) as ex:
        for i, (f, modele) in ex.map(une, attente.index):
            if not f:
                continue
            txt = lambda v: " ".join(map(str, v)) if isinstance(v, (list, tuple)) else ("" if v is None else str(v))  # noqa: E731
            df.loc[i, ["titre_fr", "resume", "nature", "aire_sujet", "pays", "lentille_principale", "lentille_secondaire",
                       "iceberg", "horizon", "technologies", "indice_maturite", "levier_famille", "entites", "chiffres_cles",
                       "confiance", "modele", "version_consigne", "date_classement", "classe"]] = [
                txt(f.get("titre_fr")), txt(f.get("resume"))[:900], txt(f.get("nature")), ";".join(f.get("aire_sujet") or []),
                ";".join(map(str, f.get("pays") or [])), txt(f.get("lentille_principale")), txt(f.get("lentille_secondaire")),
                txt(f.get("iceberg")), txt(f.get("horizon")), ";".join(map(str, f.get("technologies") or [])),
                txt(f.get("indice_maturite")), txt(f.get("levier_famille")),
                json.dumps(f.get("entites") or [], ensure_ascii=False), json.dumps(f.get("chiffres_cles") or [], ensure_ascii=False),
                txt(f.get("confiance")), modele, f"passe1_lot_v2+passe2_{version}", MAINTENANT.isoformat(timespec="seconds"), True]
            faites += 1
    bilan["fiches_rattrapees"] = faites
    tables[mois] = df

    # 3. Vecteurs des articles pertinents
    vec = {m: lire_vecteurs(stock, m) for m in (mois_prec, mois)}
    sans = df[(df["tri"] != "NON") & (df["tri"] != "") & ~df["id"].isin(vec[mois]["id"])]
    sans = sans.head(cs.get("vecteurs_max", 20000))
    nouveaux = []
    modele_vec = modeles().get("vecteurs", "bge-m3")
    lot = cs.get("lot_vecteurs", 32)
    textes = [texte_pour_vecteur(r) for _, r in sans.iterrows()]
    for k in range(0, len(textes), lot):
        for essai in range(3):
            try:
                rep = albert.client.embeddings.create(model=modele_vec, input=textes[k:k + lot])
                nouveaux += [np.asarray(e.embedding, dtype=np.float32) for e in rep.data]
                break
            except Exception as e:  # noqa: BLE001
                if essai == 2:
                    bilan["erreur_vecteurs"] = str(e)[:150]
                time.sleep(5 * (essai + 1))
        if "erreur_vecteurs" in bilan:
            break
    if nouveaux:
        vec[mois] = pd.concat([vec[mois], pd.DataFrame({"id": sans["id"].iloc[:len(nouveaux)].tolist(),
                                                        "vecteur": [v.tolist() for v in nouveaux]})], ignore_index=True)
    bilan["vecteurs"] = len(nouveaux)

    # 4. Sujets
    tout = pd.concat([tables[mois_prec], tables[mois]], ignore_index=True)
    vtout = pd.concat([vec[mois_prec], vec[mois]], ignore_index=True)
    groupes, appartenance = sujets(tout, vtout, cs)
    bilan["sujets"] = len(groupes)
    bilan["sujets_multi_aires"] = int((groupes["nb_aires_source"] >= 3).sum()) if len(groupes) else 0

    # Ecriture : on relit le mois juste avant, pour ne pas ecraser une collecte passee entre-temps
    frais = stock.lire(mois).reindex(columns=C.COLONNES)
    frais["classe"] = frais["classe"].astype(str).str.lower().eq("true")
    maj = tables[mois].set_index("id")
    frais = frais.set_index("id")
    communs = frais.index.intersection(maj.index)
    cols = C.COLONNES[C.COLONNES.index("tri"):] + ["classe"]
    frais.loc[communs, cols] = maj.loc[communs, cols]
    frais = frais.reset_index()
    for col in C.COLONNES[C.COLONNES.index("tri"):]:
        frais[col] = frais[col].map(lambda v: "" if v is None or (isinstance(v, float) and v != v) else str(v))
    fichiers = {f"fiches/{mois}.parquet": frais[C.COLONNES], f"vecteurs/{mois}.parquet": vec[mois]}
    if len(groupes):
        fichiers["sujets/groupes.parquet"] = groupes
        fichiers["sujets/appartenance.parquet"] = appartenance
    ecrire_fichiers(stock, fichiers, f"Rattrapage du {MAINTENANT:%Y-%m-%d} : {bilan['tries']} tris, "
                                     f"{faites} fiches, {len(nouveaux)} vecteurs, {len(groupes)} sujets")

    # Journal lisible sans Hugging Face
    JOURNAL.mkdir(exist_ok=True)
    if len(groupes):
        groupes.drop(columns=["ids"]).head(40).to_csv(JOURNAL / "sujets_bilan.csv", index=False)
    bilan.update({"fin": datetime.now(timezone.utc).isoformat(timespec="seconds"), "duree_s": round(time.time() - debut),
                  "appels_albert": albert.appels})
    C.ecrire_journal(bilan)
    print(json.dumps(bilan, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
