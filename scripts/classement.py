"""Classement des articles par Albert (Sprint 3) : tri (passe 1) et fiche (passe 2).

Utilise par la collecte et par l'evaluation sur le jeu de reference.
Modeles et consignes : config/modeles.yaml et config/consignes/.
Secret : ALBERT_API_KEY.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
CONSIGNES = RACINE / "config" / "consignes"
AIRES = {"EU", "US", "CN", "JK", "IN", "ASE", "RU", "GO", "MO", "AF", "LA", "OC", "GLO"}
LENTILLES = {"TEC", "INF", "MON", "PUI", "SOC", "SOL", "MIL"}


def modeles() -> dict:
    return yaml.safe_load(open(RACINE / "config" / "modeles.yaml", encoding="utf-8"))["albert"]


def consigne(nom: str) -> str:
    return (CONSIGNES / nom).read_text(encoding="utf-8")


def liste_technologies() -> str:
    import pandas as pd
    t = pd.read_csv(RACINE / "config" / "technologies.csv", dtype=str).fillna("")
    col = "nom" if "nom" in t else t.columns[0]
    return ", ".join(t[col].tolist())


class Albert:
    """Client minimal, avec nouvel essai et bascule sur les modeles de secours."""

    def __init__(self):
        from openai import OpenAI
        cle = os.environ.get("ALBERT_API_KEY", "").strip()
        if not cle:
            raise RuntimeError("secret ALBERT_API_KEY absent")
        conf = modeles()
        self.client = OpenAI(base_url=conf["adresse"], api_key=cle, timeout=120)
        self.secours = conf.get("secours", [])
        self.appels = 0

    def demander(self, modele: str, texte: str, max_tokens: int, json_force: bool = False) -> tuple[str, str]:
        """Renvoie (reponse, modele effectivement utilise)."""
        derniere = None
        for m in [modele] + self.secours:
            for essai in range(3):
                try:
                    params = dict(model=m, temperature=0, max_tokens=max_tokens,
                                  messages=[{"role": "user", "content": texte}])
                    if json_force:
                        params["response_format"] = {"type": "json_object"}
                    self.appels += 1
                    rep = self.client.chat.completions.create(**params)
                    return nettoyer(rep.choices[0].message.content), m
                except Exception as e:  # noqa: BLE001
                    derniere = e
                    message = str(e)
                    if "response_format" in message and json_force:
                        json_force = False          # modele qui refuse le JSON impose
                        continue
                    if any(c in message for c in ("404", "model_not_found", "does not exist")):
                        break                       # modele retire : on passe au suivant
                    time.sleep(5 * (essai + 1))
        raise RuntimeError(f"Albert indisponible : {derniere}")


def nettoyer(t: str) -> str:
    return re.sub(r"<think>.*?</think>", "", t or "", flags=re.S).strip()


def extraire_json(t: str):
    d, f = t.find("{"), t.rfind("}")
    try:
        return json.loads(t[d:f + 1]) if d >= 0 and f > d else None
    except json.JSONDecodeError:
        return None


def lire_tri(t: str) -> str:
    m = re.search(r"\b(OUI|NON|DOUTE)\b", (t or "").upper())
    return m.group(1) if m else "ILLISIBLE"


# ---------------------------------------------------------------- passe 1

def trier_un(albert: Albert, titre: str, extrait: str, version: str = "v2") -> str:
    texte = consigne(f"passe1_{version}.txt").replace("<<TITRE>>", titre).replace("<<EXTRAIT>>", extrait[:500])
    rep, _ = albert.demander(modeles()["tri"], texte, 300)
    return lire_tri(rep)


def trier_lot(albert: Albert, articles: list[tuple[str, str]], taille: int = 20) -> list[str]:
    """Tri de plusieurs articles par requete. articles = [(titre, extrait)]."""
    gabarit = consigne("passe1_lot_v2.txt")
    sortie = []
    for i in range(0, len(articles), taille):
        lot = articles[i:i + taille]
        bloc = "\n".join(f"{k + 1}. {t[:200]} | {e[:200]}".replace("\n", " ") for k, (t, e) in enumerate(lot))
        rep, _ = albert.demander(modeles()["tri"], gabarit.replace("<<ARTICLES>>", bloc), 60 + 12 * len(lot), json_force=True)
        d = extraire_json(rep) or {}
        sortie += [lire_tri(str(d.get(str(k + 1), ""))) for k in range(len(lot))]
    return sortie


# ---------------------------------------------------------------- passe 2

_TECHNO = None


def ficher(albert: Albert, titre: str, langue: str, texte: str, version: str = "v3") -> tuple[dict | None, str]:
    """Fiche d'analyse (dict) ou None si le JSON est illisible, et le modele utilise."""
    global _TECHNO
    if _TECHNO is None:
        _TECHNO = liste_technologies()
    c = (consigne(f"passe2_{version}.txt").replace("<<TECHNOLOGIES>>", _TECHNO).replace("<<TITRE>>", titre)
         .replace("<<LANGUE>>", langue or "?")
         .replace("<<TEXTE>>", texte[:6000] or "(texte non disponible : classer sur le titre)"))
    rep, m = albert.demander(modeles()["fiche"], c, 2500, json_force=True)
    f = extraire_json(rep)
    if f is None:
        return None, m
    f["aire_sujet"] = [a for a in (f.get("aire_sujet") or []) if a in AIRES]
    for k in ("lentille_principale", "lentille_secondaire"):
        if f.get(k) not in LENTILLES:
            f[k] = None
    return f, m
