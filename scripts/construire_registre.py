"""Construit config/sources.csv a partir des fichiers RSS de la v1 (data/*_rss.csv)
et de la liste des sources non occidentales ajoutees au Sprint 1.

Script a usage unique (Sprint 1), garde pour la tracabilite.
Usage : python scripts/construire_registre.py
"""
import csv
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DATA = RACINE / "data"
SORTIE = RACINE / "config" / "sources.csv"
DATE = "2026-11-14"

COLONNES = ["id", "nom", "url", "type", "langue", "pays", "aire_source", "ancrage",
            "lien_pouvoir", "proprietaire", "lentilles_attendues", "frequence",
            "fiabilite", "actif", "date_ajout", "remarque",
            "articles_30j", "taux_pertinence_30j", "dernier_succes"]

# Lentilles attendues par fichier v1
LENTILLES_FICHIER = {
    "energie_rss.csv": "TEC;MIL",
    "economie_rss.csv": "MON;PUI",
    "marches_rss.csv": "MON;TEC",
    "numerique_rss.csv": "TEC;INF",
    "reglementation_rss.csv": "INF;SOL",
    "thematiques_rss.csv": "TEC",
    "personnes_rss.csv": "TEC;SOC",
}

# Metadonnees des sources v1 : nom -> (pays, aire, ancrage, lien_pouvoir, proprietaire)
# Les institutions europeennes sont codees pays "EU" (pas un code ISO, mais sans ambiguite).
INST_EU = ("EU", "EU", "INTERNATIONAL", "INSTITUTION", "Union europeenne")
META = {
    "INSEE": ("FR", "EU", "LOCAL", "ETAT", "Etat francais"),
    "Banque de France": ("FR", "EU", "LOCAL", "INSTITUTION", "Banque de France"),
    "BCE": INST_EU,
    "OCDE": ("", "GLO", "INTERNATIONAL", "INSTITUTION", "OCDE"),
    "FMI": ("", "GLO", "INTERNATIONAL", "INSTITUTION", "FMI"),
    "Le Grand Continent": ("FR", "EU", "LOCAL", "INDEPENDANT", "Groupe d'etudes geopolitiques"),
    "Alternatives": ("FR", "EU", "LOCAL", "INDEPENDANT", "Cooperative Alternatives Economiques"),
    "La Tribune": ("FR", "EU", "LOCAL", "GROUPE_PRIVE", ""),
    "Project Syndicate": ("CZ", "EU", "INTERNATIONAL", "FONDATION_ONG", ""),
    "AIE": ("", "GLO", "INTERNATIONAL", "INSTITUTION", "Agence internationale de l'energie"),
    "RTE": ("FR", "EU", "LOCAL", "ETAT", "RTE"),
    "Connaissance des": ("FR", "EU", "LOCAL", "FONDATION_ONG", ""),
    "Actu-Environnement": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "Révolution": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "PV Magazine": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "European Energy Review": ("", "EU", "LOCAL", "INCONNU", ""),
    "Carbon Brief": ("GB", "EU", "LOCAL", "FONDATION_ONG", ""),
    "Oil Price": ("US", "US", "LOCAL", "GROUPE_PRIVE", ""),
    "Enerzine": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "Investing.com": ("IL", "MO", "INTERNATIONAL", "GROUPE_PRIVE", ""),
    "EnergyTrend": ("TW", "JK", "LOCAL", "ENTREPRISE", "TrendForce"),
    "BloombergNEF": ("US", "US", "LOCAL", "GROUPE_PRIVE", "Bloomberg"),
    "FXStreet": ("ES", "EU", "INTERNATIONAL", "GROUPE_PRIVE", ""),
    "CoinTelegraph": ("US", "US", "INTERNATIONAL", "GROUPE_PRIVE", ""),
    "Xinhua": ("CN", "CN", "LOCAL", "ETAT", "Agence Chine nouvelle"),
    "Epoch AI": ("US", "US", "LOCAL", "FONDATION_ONG", ""),
    "GitHub Trending": ("US", "US", "INTERNATIONAL", "ENTREPRISE", "Microsoft (GitHub)"),
    "Changelog": ("US", "US", "LOCAL", "INDEPENDANT", ""),
    "Hugging Face": ("US", "US", "INTERNATIONAL", "ENTREPRISE", "Hugging Face"),
    "HF Leaderboard": ("US", "US", "INTERNATIONAL", "FONDATION_ONG", "LMSYS"),
    "Parlement EU": INST_EU, "EUR-Lex": INST_EU, "Commission EU": INST_EU,
    "JRC": INST_EU, "Conseil UE": INST_EU, "EEA": INST_EU, "ENISA": INST_EU,
    "AI Act Observatory": ("", "EU", "LOCAL", "FONDATION_ONG", "Future of Life Institute"),
    "Federal Register": ("US", "US", "LOCAL", "ETAT", "Gouvernement federal americain"),
    "FTC": ("US", "US", "LOCAL", "ETAT", "Gouvernement federal americain"),
    "NIST": ("US", "US", "LOCAL", "ETAT", "Gouvernement federal americain"),
    "Tech Policy Press": ("US", "US", "LOCAL", "INDEPENDANT", ""),
    "Legifrance": ("FR", "EU", "LOCAL", "ETAT", "Etat francais"),
    "MIT Technology Review": ("US", "US", "LOCAL", "FONDATION_ONG", "MIT"),
    "TechCrunch": ("US", "US", "LOCAL", "GROUPE_PRIVE", "Yahoo"),
    "Wired": ("US", "US", "LOCAL", "GROUPE_PRIVE", "Conde Nast"),
    "The Verge": ("US", "US", "LOCAL", "GROUPE_PRIVE", "Vox Media"),
    "Next INpact": ("FR", "EU", "LOCAL", "INDEPENDANT", "Next"),
    "Usine Nouvelle": ("FR", "EU", "LOCAL", "GROUPE_PRIVE", "Infopro Digital"),
    "Techniques Ingénieur": ("FR", "EU", "LOCAL", "GROUPE_PRIVE", ""),
    "Décideurs": ("FR", "EU", "LOCAL", "GROUPE_PRIVE", ""),
    "The Batch": ("US", "US", "LOCAL", "ENTREPRISE", "DeepLearning.AI"),
    "VentureBeat": ("US", "US", "LOCAL", "GROUPE_PRIVE", ""),
    "Nature News": ("GB", "EU", "INTERNATIONAL", "GROUPE_PRIVE", "Springer Nature"),
    # Personnes
    "Benedict Evans": ("GB", "EU", "LOCAL", "INDEPENDANT", ""),
    "Stéphane Schultz": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "Azeem Azhar": ("GB", "EU", "LOCAL", "INDEPENDANT", ""),
    "Jack Clark": ("US", "US", "LOCAL", "INDEPENDANT", ""),
    "Kate Raworth": ("GB", "EU", "LOCAL", "INDEPENDANT", ""),
    "Tariq Krim": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "Philippe Méda": ("FR", "EU", "LOCAL", "INDEPENDANT", ""),
    "Bernard Marr": ("GB", "EU", "LOCAL", "INDEPENDANT", ""),
    "Roger Spitz": ("US", "US", "LOCAL", "INDEPENDANT", ""),
    "Tim O'Reilly": ("US", "US", "LOCAL", "ENTREPRISE", "O'Reilly Media"),
    "Kai-Fu Lee": ("CN", "CN", "LOCAL", "INDEPENDANT", ""),
    "Rui Ma": ("US", "US", "DIASPORA", "INDEPENDANT", ""),
    "Zeyi Yang": ("US", "US", "DIASPORA", "FONDATION_ONG", "MIT"),
    "Scott Galloway": ("US", "US", "LOCAL", "INDEPENDANT", ""),
    "Cory Doctorow": ("US", "US", "LOCAL", "INDEPENDANT", ""),
    "Tomi Adeyrun": ("NG", "AF", "LOCAL", "INDEPENDANT", "Techpoint Africa"),
    "Andile Masuku": ("GB", "EU", "DIASPORA", "GROUPE_PRIVE", "African Business (IC Publications)"),
    "Rebecca Enonchong": ("CM", "AF", "LOCAL", "INDEPENDANT", ""),
    "Mårten Mickos": ("FI", "EU", "LOCAL", "INDEPENDANT", ""),
    "Niklas Zennström": ("SE", "EU", "LOCAL", "ENTREPRISE", "Atomico"),
    "Cecilia Skingsley": ("CH", "GLO", "INTERNATIONAL", "INSTITUTION", "BRI"),
    "Marta Belcher": ("US", "US", "LOCAL", "ENTREPRISE", "Filecoin Foundation"),
    "Ronaldo Lemos": ("BR", "LA", "LOCAL", "INDEPENDANT", ""),
    "Cristina Junqueira": ("BR", "LA", "LOCAL", "ENTREPRISE", "Nubank"),
    "Ignacio Plaza": ("AR", "LA", "LOCAL", "INDEPENDANT", ""),
}

# Sources non occidentales ajoutees au Sprint 1.
# (nom, url, langue, pays, aire, ancrage, lien_pouvoir, proprietaire, lentilles)
NOUVELLES = [
    # Chine
    ("36Kr", "https://36kr.com/feed", "zh", "CN", "CN", "LOCAL", "GROUPE_PRIVE", "36Kr Holdings", "TEC;MON"),
    ("Huxiu (虎嗅)", "https://www.huxiu.com/rss/0.xml", "zh", "CN", "CN", "LOCAL", "GROUPE_PRIVE", "", "TEC;SOC"),
    ("South China Morning Post - Chine", "https://www.scmp.com/rss/91/feed", "en", "HK", "CN", "LOCAL", "GROUPE_PRIVE", "Alibaba", "PUI;SOC"),
    # Japon, Coree
    ("NHK - Actualites", "https://www3.nhk.or.jp/rss/news/cat0.xml", "ja", "JP", "JK", "LOCAL", "ETAT", "NHK (audiovisuel public)", "SOC;PUI"),
    ("NHK - Economie", "https://www3.nhk.or.jp/rss/news/cat5.xml", "ja", "JP", "JK", "LOCAL", "ETAT", "NHK (audiovisuel public)", "MON;TEC"),
    ("Yonhap (연합뉴스)", "https://www.yna.co.kr/rss/news.xml", "ko", "KR", "JK", "LOCAL", "ETAT", "Yonhap (agence publique)", "SOC;PUI"),
    ("Hankyoreh English", "https://english.hani.co.kr/rss/", "en", "KR", "JK", "LOCAL", "INDEPENDANT", "Hankyoreh (actionnariat populaire)", "SOC"),
    # Asie du Sud
    ("The Hindu", "https://www.thehindu.com/feeder/default.rss", "en", "IN", "IN", "LOCAL", "GROUPE_PRIVE", "THG Publishing", "SOC;PUI"),
    ("Scroll.in", "https://scroll.in/feed", "en", "IN", "IN", "LOCAL", "INDEPENDANT", "", "SOC"),
    ("The Wire", "https://thewire.in/feed", "en", "IN", "IN", "LOCAL", "FONDATION_ONG", "Foundation for Independent Journalism", "SOC;PUI"),
    ("Mongabay India", "https://india.mongabay.com/feed/", "en", "IN", "IN", "LOCAL", "FONDATION_ONG", "Mongabay", "MIL;SOL"),
    ("Amar Ujala", "https://www.amarujala.com/rss/breaking-news.xml", "hi", "IN", "IN", "LOCAL", "GROUPE_PRIVE", "", "SOC"),
    ("Dawn", "https://www.dawn.com/feeds/home", "en", "PK", "IN", "LOCAL", "GROUPE_PRIVE", "Dawn Media Group", "SOC;TEC"),
    ("The Daily Star (Bangladesh)", "https://www.thedailystar.net/frontpage/rss.xml", "en", "BD", "IN", "LOCAL", "GROUPE_PRIVE", "", "SOC"),
    # Asie du Sud-Est
    ("Mongabay Indonesia", "https://www.mongabay.co.id/feed/", "id", "ID", "ASE", "LOCAL", "FONDATION_ONG", "Mongabay", "MIL;SOL"),
    ("CNN Indonesia", "https://www.cnnindonesia.com/rss", "id", "ID", "ASE", "LOCAL", "GROUPE_PRIVE", "Trans Media (CT Corp)", "SOC;MON"),
    ("VnExpress", "https://vnexpress.net/rss/tin-moi-nhat.rss", "vi", "VN", "ASE", "LOCAL", "ETAT", "Ministere vietnamien des sciences", "SOC;TEC"),
    ("Rappler", "https://www.rappler.com/feed/", "en", "PH", "ASE", "LOCAL", "INDEPENDANT", "", "SOC"),
    ("CNA (Channel NewsAsia)", "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "en", "SG", "ASE", "LOCAL", "ETAT", "Mediacorp", "PUI;MON"),
    # Afrique subsaharienne
    ("allAfrica - Derniers titres", "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf", "en", "", "AF", "LOCAL", "GROUPE_PRIVE", "AllAfrica Global Media (agrege la presse africaine)", "SOC;PUI"),
    ("Premium Times", "https://www.premiumtimesng.com/feed", "en", "NG", "AF", "LOCAL", "INDEPENDANT", "", "SOC"),
    ("TechCabal", "https://techcabal.com/feed/", "en", "NG", "AF", "LOCAL", "GROUPE_PRIVE", "", "TEC;MON"),
    ("Daily Maverick", "https://www.dailymaverick.co.za/dmrss/", "en", "ZA", "AF", "LOCAL", "INDEPENDANT", "", "SOC;PUI"),
    ("The Conversation Africa", "https://theconversation.com/africa/articles.atom", "en", "ZA", "AF", "LOCAL", "FONDATION_ONG", "The Conversation Africa", "SOC;MIL"),
    ("Jeune Afrique", "https://www.jeuneafrique.com/feed/", "fr", "FR", "AF", "DIASPORA", "GROUPE_PRIVE", "Jeune Afrique Media Group", "PUI;MON"),
    ("Addis Standard", "https://addisstandard.com/feed/", "en", "ET", "AF", "LOCAL", "INDEPENDANT", "", "SOC;PUI"),
    # Amerique latine
    ("Mongabay Latam", "https://es.mongabay.com/feed/", "es", "", "LA", "LOCAL", "FONDATION_ONG", "Mongabay", "MIL;SOL"),
    ("Agencia Brasil", "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml", "pt", "BR", "LA", "LOCAL", "ETAT", "EBC (audiovisuel public)", "SOC;INF"),
    ("Folha de S.Paulo", "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml", "pt", "BR", "LA", "LOCAL", "GROUPE_PRIVE", "Grupo Folha", "SOC;MON"),
    ("CIPER Chile", "https://www.ciperchile.cl/feed/", "es", "CL", "LA", "LOCAL", "FONDATION_ONG", "", "SOC;PUI"),
    ("El Desconcierto", "https://www.eldesconcierto.cl/feed", "es", "CL", "LA", "LOCAL", "INDEPENDANT", "", "SOC;MIL"),
    ("Animal Politico", "https://www.animalpolitico.com/feed", "es", "MX", "LA", "LOCAL", "INDEPENDANT", "", "SOC"),
    # Golfe, Moyen-Orient, Afrique du Nord
    ("Attaqa (الطاقة)", "https://attaqa.net/feed/", "ar", "", "GO", "LOCAL", "INCONNU", "", "TEC;PUI"),
    ("Al Jazeera English", "https://www.aljazeera.com/xml/rss/all.xml", "en", "QA", "GO", "LOCAL", "ETAT", "Qatar", "PUI;SOC"),
    ("The National (EAU)", "https://www.thenationalnews.com/arc/outboundfeeds/rss/?outputType=xml", "en", "AE", "GO", "LOCAL", "ETAT", "International Media Investments (Abou Dhabi)", "MON;PUI"),
    ("Arab News", "https://www.arabnews.com/rss.xml", "en", "SA", "GO", "LOCAL", "GROUPE_PRIVE", "Saudi Research and Media Group", "PUI;MON"),
    ("Mada Masr", "https://www.madamasr.com/en/feed/", "en", "EG", "MO", "LOCAL", "INDEPENDANT", "", "SOC"),
    # Russie
    ("TASS", "https://tass.com/rss/v2.xml", "en", "RU", "RU", "LOCAL", "ETAT", "Etat russe", "PUI"),
    ("Kommersant (Коммерсантъ)", "https://www.kommersant.ru/RSS/news.xml", "ru", "RU", "RU", "LOCAL", "GROUPE_PRIVE", "", "MON;PUI"),
    ("Meduza (Медуза)", "https://meduza.io/rss/all", "ru", "LV", "RU", "DIASPORA", "INDEPENDANT", "Media en exil (Riga)", "SOC;PUI"),
    # Global, Sud-Sud
    ("Global Voices", "https://globalvoices.org/feed/", "en", "", "GLO", "INTERNATIONAL", "FONDATION_ONG", "Global Voices", "SOC"),
    ("Global Voices en francais", "https://fr.globalvoices.org/feed/", "fr", "", "GLO", "INTERNATIONAL", "FONDATION_ONG", "Global Voices", "SOC"),
    ("Dialogue Earth", "https://dialogue.earth/feed/", "en", "", "GLO", "INTERNATIONAL", "FONDATION_ONG", "Dialogue Earth", "MIL;PUI"),
    ("Dialogue Earth en espagnol", "https://dialogue.earth/es/feed/", "es", "", "LA", "LOCAL", "FONDATION_ONG", "Dialogue Earth", "MIL;PUI"),
]


def slug(texte):
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:40] or "source"


def meta_pour(nom):
    for cle, valeur in META.items():
        if nom.startswith(cle) or cle in nom:
            return valeur
    return ("", "", "", "INCONNU", "")


def main():
    lignes, urls_vues, ids_vus = [], {}, set()

    def nouvel_id(nom):
        base = slug(nom)
        ident, n = base, 2
        while ident in ids_vus:
            ident, n = f"{base}-{n}", n + 1
        ids_vus.add(ident)
        return ident

    for fichier in sorted(DATA.glob("*_rss.csv")):
        with fichier.open(encoding="utf-8") as f:
            for brut in csv.DictReader(f, skipinitialspace=True):
                nom = (brut.get("nom") or "").strip()
                url = (brut.get("url_flux") or "").strip()
                if not nom or not url:
                    continue
                cle = url.rstrip("/").lower()
                if cle in urls_vues:  # doublon entre fichiers v1
                    urls_vues[cle]["remarque"] += f" ; aussi dans {fichier.name}"
                    continue
                langue = (brut.get("langue") or "").strip().lower()
                pays, aire, ancrage, lien, proprio = meta_pour(nom)
                if not langue:
                    langue = "fr" if pays == "FR" else "en"
                ligne = {
                    "id": nouvel_id(nom), "nom": nom, "url": url,
                    "type": "PERSONNE" if fichier.name.startswith("personnes") else "RSS",
                    "langue": langue, "pays": pays, "aire_source": aire, "ancrage": ancrage,
                    "lien_pouvoir": lien, "proprietaire": proprio,
                    "lentilles_attendues": LENTILLES_FICHIER.get(fichier.name, ""),
                    "frequence": "6h", "fiabilite": 2, "actif": "oui", "date_ajout": "2024-03-01",
                    "remarque": f"v1 : {fichier.name}",
                    "articles_30j": "", "taux_pertinence_30j": "", "dernier_succes": "",
                }
                urls_vues[cle] = ligne
                lignes.append(ligne)

    for nom, url, langue, pays, aire, ancrage, lien, proprio, lent in NOUVELLES:
        cle = url.rstrip("/").lower()
        if cle in urls_vues:
            continue
        ligne = {
            "id": nouvel_id(nom), "nom": nom, "url": url, "type": "RSS", "langue": langue,
            "pays": pays, "aire_source": aire, "ancrage": ancrage, "lien_pouvoir": lien,
            "proprietaire": proprio, "lentilles_attendues": lent, "frequence": "6h",
            "fiabilite": 2, "actif": "oui", "date_ajout": DATE,
            "remarque": "Ajout Sprint 1 : adresse du flux a confirmer par l'audit automatique",
            "articles_30j": "", "taux_pertinence_30j": "", "dernier_succes": "",
        }
        urls_vues[cle] = ligne
        lignes.append(ligne)

    SORTIE.parent.mkdir(exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        w.writerows(lignes)
    sans_meta = [l["nom"] for l in lignes if not l["aire_source"]]
    print(f"{len(lignes)} sources ecrites dans {SORTIE}")
    if sans_meta:
        print("Sans aire :", sans_meta)


if __name__ == "__main__":
    main()
