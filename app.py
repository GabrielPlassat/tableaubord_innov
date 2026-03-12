import os
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import feedparser

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Innovation Radar",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { background-color: #080c14; color: #c8d8e8; font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #080c14; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }

.radar-header { display: flex; align-items: baseline; gap: 1rem; border-bottom: 1px solid #1a2a3a; padding-bottom: 0.8rem; margin-bottom: 1.5rem; }
.radar-title { font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #00e5ff; letter-spacing: 0.08em; text-transform: uppercase; }
.radar-subtitle { font-size: 0.75rem; color: #4a6a8a; font-family: 'Space Mono', monospace; letter-spacing: 0.12em; }

.section-header        { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #00e5ff;  text-transform: uppercase; letter-spacing: 0.2em; border-left: 2px solid #00e5ff;  padding-left: 0.6rem; margin: 1.5rem 0 1rem 0; }
.section-header-orange { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #ffaa00;  text-transform: uppercase; letter-spacing: 0.2em; border-left: 2px solid #ffaa00;  padding-left: 0.6rem; margin: 1.5rem 0 1rem 0; }
.section-header-green  { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #00e5a0;  text-transform: uppercase; letter-spacing: 0.2em; border-left: 2px solid #00e5a0;  padding-left: 0.6rem; margin: 1.5rem 0 1rem 0; }

.tag { display: inline-block; background: #0d2030; border: 1px solid #1a3a5a; border-radius: 2px; padding: 1px 7px; font-size: 0.65rem; color: #6aadcc; font-family: 'Space Mono', monospace; margin: 1px 2px; }
.person-card { background: #0d1520; border: 1px solid #1a2a3a; border-radius: 4px; padding: 1rem; margin-bottom: 0.8rem; }
.person-name    { font-family: 'Space Mono', monospace; font-size: 0.9rem; font-weight: 700; color: #e8f4ff; }
.person-courant { font-size: 0.72rem; color: #00e5ff; margin: 0.15rem 0 0.5rem 0; }
.person-focus   { font-size: 0.78rem; color: #8aaabb; line-height: 1.4; }
.person-note    { font-size: 0.72rem; color: #4a7a8a; margin-top: 0.4rem; font-style: italic; }
.person-link    { display: inline-block; margin-top: 0.5rem; font-family: 'Space Mono', monospace; font-size: 0.62rem; color: #00e5ff; text-decoration: none; border-bottom: 1px solid #00e5ff44; }
.signal-card  { background: #0d1520; border-left: 3px solid; padding: 0.8rem 1rem; margin-bottom: 0.7rem; border-radius: 0 4px 4px 0; }
.signal-title { font-size: 0.88rem; color: #e8f4ff; font-weight: 500; }
.signal-meta  { font-family: 'Space Mono', monospace; font-size: 0.62rem; color: #4a6a8a; margin-top: 0.3rem; }
.signal-note  { font-size: 0.75rem; color: #7a9aaa; margin-top: 0.35rem; }

.stTabs [data-baseweb="tab-list"] { gap: 2px; background: #0d1520; padding: 4px; border-radius: 4px; border: 1px solid #1a2a3a; }
.stTabs [data-baseweb="tab"] { font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #4a6a8a; text-transform: uppercase; letter-spacing: 0.08em; background: transparent; border-radius: 2px; padding: 6px 16px; }
.stTabs [aria-selected="true"] { background: #1a2a3a !important; color: #00e5ff !important; }

.synthese-card  { background: #0d1520; border-radius: 4px; padding: 1.4rem; margin-bottom: 1.2rem; line-height: 1.75; font-size: 0.88rem; color: #c8d8e8; }
.synthese-theme { font-family: 'Space Mono', monospace; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────────────
DOMAINE_COLORS = {
    "énergie": "#ffaa00", "energy": "#ffaa00", "prix": "#ffaa00", "renouvelable": "#ffaa00", "transition": "#ffcc44",
    "tech": "#00e5ff", "ia": "#00e5ff", "ai": "#00e5ff",
    "transport": "#aa88ff", "mobilité": "#aa88ff",
    "agri": "#00e5a0", "climat": "#44aaff",
    "économie": "#ff8844", "macro": "#ff8844", "bce": "#ff8844", "géopolitique": "#ff8844", "conjoncture": "#ff8844",
    "industrie": "#aabb66",
}
def color_for(domaine):
    d = str(domaine).lower()
    for k, v in DOMAINE_COLORS.items():
        if k in d:
            return v
    return "#6688aa"

# ── CHARGEMENT RSS ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_rss(path, max_per_source=5):
    try:
        sources = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()
    items = []
    for _, src in sources.iterrows():
        try:
            feed = feedparser.parse(src["url_flux"], agent="Mozilla/5.0 (compatible; RSSReader/1.0)")
            for entry in feed.entries[:max_per_source]:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                date_str = datetime.datetime(*pub[:6]).strftime("%Y-%m-%d") if pub else "—"
                items.append({
                    "date":      date_str,
                    "titre":     entry.get("title", "Sans titre"),
                    "url":       entry.get("link", ""),
                    "resume":    entry.get("summary", "")[:280].replace("<p>","").replace("</p>","").replace("<br>","").strip() + "…",
                    "source":    src["nom"],
                    "domaine":   src.get("domaine", src.get("categorie", "")),
                    "categorie": src.get("categorie", ""),
                    "langue":    src.get("langue", ""),
                    "courant":   src.get("courant", ""),
                })
        except Exception:
            pass
    df = pd.DataFrame(items)
    return df.sort_values("date", ascending=False) if not df.empty else df

def render_articles(df, color, max_items=30):
    for _, row in df.head(max_items).iterrows():
        url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
        cat  = row.get("categorie", "")
        lang = row.get("langue", "")
        badges = ""
        if cat:  badges += f'<span class="tag" style="border-color:{color}44; color:{color}">{cat}</span>'
        if lang: badges += f'<span class="tag">{lang}</span>'
        st.markdown(f"""
        <div class="signal-card" style="border-color:{color}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                <div class="signal-title">{row["titre"]}</div>
                <div style="white-space:nowrap; flex-shrink:0">{badges}</div>
            </div>
            <div class="signal-meta">{row["date"]} · {row["source"]}</div>
            <div class="signal-note">{row["resume"]}</div>
            <div style="margin-top:0.4rem">{url_html}</div>
        </div>""", unsafe_allow_html=True)



# ── INDICATEURS MARCHÉS ────────────────────────────────────────────────────────
@st.cache_data(ttl=900)
def fetch_prices():
    """Récupère les prix via yfinance. Retourne un dict {ticker: {price, delta_pct, hist}}"""
    try:
        import yfinance as yf
        tickers = {
            "Brent": "BZ=F", "WTI": "CL=F",
            "Gaz naturel": "NG=F",
            "EUR/USD": "EURUSD=X", "USD/CNY": "USDCNY=X",
            "Bitcoin": "BTC-USD",
            "Lithium ETF": "LIT",
        }
        result = {}
        for name, sym in tickers.items():
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="30d", interval="1d")
                if hist.empty:
                    continue
                closes = hist["Close"].dropna()
                if len(closes) < 2:
                    continue
                price  = float(closes.iloc[-1])
                price0 = float(closes.iloc[-2])
                delta  = (price - price0) / price0 * 100
                result[name] = {"price": price, "delta_pct": delta, "hist": closes.tolist()[-14:]}
            except Exception:
                pass
        return result
    except ImportError:
        return {}

def render_price_cards(prices, specs):
    """specs = [(name, unit, decimals, color), ...]"""
    cols = st.columns(len(specs))
    for col, (name, unit, dec, color) in zip(cols, specs):
        if name not in prices:
            col.markdown(f"""<div class="metric-card" style="border-top:2px solid {color}; opacity:0.4">
                <div class="metric-label">{name}</div>
                <div class="metric-value" style="font-size:1rem; color:#4a6a8a">—</div>
                <div class="metric-note">Données indisponibles</div></div>""", unsafe_allow_html=True)
            continue
        d = prices[name]
        p, delta = d["price"], d["delta_pct"]
        arrow  = "▲" if delta >= 0 else "▼"
        dclass = "#00e5a0" if delta >= 0 else "#ff4d6d"
        hist   = d["hist"]
        # mini sparkline SVG
        if len(hist) >= 2:
            mn, mx = min(hist), max(hist)
            rng = mx - mn if mx != mn else 1
            pts = " ".join(f"{int(i*(56/(len(hist)-1)))},{int(24 - (v-mn)/rng*22)}" for i, v in enumerate(hist))
            spark = f'<svg width="60" height="26" style="overflow:visible"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.8"/></svg>'
        else:
            spark = ""
        col.markdown(f"""<div class="metric-card" style="border-top:2px solid {color}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start">
                <div class="metric-label">{name}</div>
                <div>{spark}</div>
            </div>
            <div class="metric-value" style="font-size:1.3rem">{p:,.{dec}f} {unit}</div>
            <div style="color:{dclass}; font-family:Space Mono; font-size:0.78rem">{arrow} {abs(delta):.2f}% / 24h</div>
            </div>""", unsafe_allow_html=True)


# ── COMPARIA SCRAPER ───────────────────────────────────────────────────────────
@st.cache_data(ttl=21600)  # refresh toutes les 6h
def fetch_comparia():
    """Scrape le classement compar:IA (beta.gouv.fr) et retourne un DataFrame."""
    try:
        import requests
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (compatible; InnovationRadar/1.0)"}
        r = requests.get("https://comparia.beta.gouv.fr/ranking", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Chercher le premier tableau principal (classement général)
        tables = soup.find_all("table")
        if not tables:
            return pd.DataFrame()
        # Premier tableau = classement général
        table = tables[0]
        rows = []
        for tr in table.find_all("tr")[1:]:  # skip header
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cols) >= 9:
                rows.append({
                    "rang":   cols[0],
                    "modele": cols[1],
                    "score":  cols[2],
                    "confiance": cols[3],
                    "votes":  cols[4],
                    "conso_wh": cols[5].replace("N/A","").replace("Wh","").strip(),
                    "taille": cols[6],
                    "archi":  cols[7],
                    "date_sortie": cols[8] if len(cols) > 8 else "",
                    "org":    cols[9] if len(cols) > 9 else "",
                    "licence": cols[10] if len(cols) > 10 else "",
                })
        df = pd.DataFrame(rows)
        # Nettoyage
        df["rang_int"]  = pd.to_numeric(df["rang"], errors="coerce")
        df["score_int"] = pd.to_numeric(df["score"], errors="coerce")
        df["conso_num"] = pd.to_numeric(df["conso_wh"], errors="coerce")
        df["votes_int"] = pd.to_numeric(df["votes"].str.replace(" ","").str.replace(",",""), errors="coerce")
        return df.dropna(subset=["rang_int"]).sort_values("rang_int")
    except Exception as e:
        return pd.DataFrame()

def render_comparia(df):
    """Affiche le classement compar:IA avec indicateurs visuels."""
    if df.empty:
        st.info("⏳ Classement compar:IA indisponible (beautifulsoup4 requis ou site inaccessible)")
        return

    top10 = df.head(10)
    score_max = df["score_int"].max()
    score_min = df["score_int"].min()
    score_range = max(score_max - score_min, 1)

    ORG_COLORS = {
        "Google": "#4285f4", "OpenAI": "#10a37f", "Anthropic": "#d97706",
        "Mistral AI": "#ff6b35", "DeepSeek": "#6366f1", "Meta": "#1877f2",
        "Alibaba": "#ff6900", "xAI": "#1da1f2", "Cohere": "#3b82f6",
        "Microsoft": "#0078d4",
    }
    LICENCE_COLORS = {
        "Open source": "#00e5a0", "Semi-ouvert": "#44aaff", "Propriétaire": "#ff8844"
    }

    # ── Podium Top 3
    st.markdown('''<div class="section-header" style="color:#00e5ff; border-color:#00e5ff">🏆 Classement compar:IA — Modèles LLM (préférences utilisateurs FR)</div>''', unsafe_allow_html=True)

    # Métriques clés
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card" style="border-top:2px solid #00e5ff">
            <div class="metric-label">🥇 Modèle #1</div>
            <div class="metric-value" style="font-size:0.9rem; color:#e8f4ff">{top10.iloc[0]["modele"][:22]}</div>
            <div style="font-family:Space Mono; font-size:0.7rem; color:#00e5ff">Score BT {top10.iloc[0]["score"]}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        best_eco = df[df["conso_num"].notna()].nsmallest(1, "conso_num").iloc[0] if df["conso_num"].notna().any() else None
        if best_eco is not None:
            st.markdown(f"""<div class="metric-card" style="border-top:2px solid #00e5a0">
                <div class="metric-label">🌱 + sobre en énergie</div>
                <div class="metric-value" style="font-size:0.9rem; color:#e8f4ff">{best_eco["modele"][:22]}</div>
                <div style="font-family:Space Mono; font-size:0.7rem; color:#00e5a0">{best_eco["conso_wh"]} Wh / 1k tokens</div>
            </div>""", unsafe_allow_html=True)
    with m3:
        # Meilleur score parmi les < 10Wh (ratio perf/éco)
        eco_perf = df[(df["conso_num"].notna()) & (df["conso_num"] < 10)].nlargest(1, "score_int")
        if not eco_perf.empty:
            r = eco_perf.iloc[0]
            st.markdown(f"""<div class="metric-card" style="border-top:2px solid #ffaa00">
                <div class="metric-label">⚖️ Meilleur ratio perf/éco</div>
                <div class="metric-value" style="font-size:0.9rem; color:#e8f4ff">{r["modele"][:22]}</div>
                <div style="font-family:Space Mono; font-size:0.7rem; color:#ffaa00">BT {r["score"]} · {r["conso_wh"]} Wh</div>
            </div>""", unsafe_allow_html=True)
    with m4:
        total_votes = df["votes_int"].sum()
        n_models = len(df)
        st.markdown(f"""<div class="metric-card" style="border-top:2px solid #aa88ff">
            <div class="metric-label">📊 Total votes</div>
            <div class="metric-value" style="font-size:1.1rem">{total_votes:,.0f}</div>
            <div style="font-family:Space Mono; font-size:0.7rem; color:#aa88ff">{n_models} modèles classés</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top 10 barre de classement
    col_rank, col_chart = st.columns([1, 2])

    with col_rank:
        st.markdown('''<div style="font-family:Space Mono; font-size:0.62rem; color:#4a6a8a; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.6rem">Top 10 — Score Bradley-Terry</div>''', unsafe_allow_html=True)
        for _, row in top10.iterrows():
            rang = int(row["rang_int"])
            score = row["score_int"]
            pct = int((score - score_min) / score_range * 100) if score_range else 80
            org = str(row.get("org",""))
            lic = str(row.get("licence",""))
            org_color = ORG_COLORS.get(org, "#6688aa")
            lic_color = LICENCE_COLORS.get(lic, "#4a6a8a")
            medals = {1:"🥇", 2:"🥈", 3:"🥉"}
            medal = medals.get(rang, f"<span style='font-family:Space Mono; color:#4a6a8a; font-size:0.7rem'>#{rang}</span>")
            conso = row.get("conso_wh","")
            conso_tag = f'<span style="background:#0a1a10; border:1px solid #00e5a044; border-radius:2px; padding:0 5px; font-size:0.58rem; color:#00e5a0; font-family:Space Mono">{conso}Wh</span>' if conso else ""
            st.markdown(f"""
            <div style="margin-bottom:0.45rem">
              <div style="display:flex; align-items:center; gap:6px; margin-bottom:2px">
                <span style="font-size:0.85rem; min-width:22px">{medal}</span>
                <span style="font-size:0.76rem; color:#e8f4ff; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">{row["modele"]}</span>
                <span style="white-space:nowrap">{conso_tag}</span>
              </div>
              <div style="display:flex; align-items:center; gap:6px">
                <div style="flex:1; background:#0d1520; border-radius:2px; height:5px">
                  <div style="background:linear-gradient(90deg, {org_color}88, {org_color}); width:{pct}%; height:5px; border-radius:2px"></div>
                </div>
                <span style="font-family:Space Mono; font-size:0.65rem; color:{org_color}; min-width:32px">{int(score) if not pd.isna(score) else ""}</span>
                <span style="font-size:0.62rem; color:{lic_color}; white-space:nowrap">{lic[:4]}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_chart:
        # Organisations dominantes parmi le Top 20
        top20 = df.head(20)
        org_counts = top20["org"].value_counts().head(6)
        st.markdown('''<div style="font-family:Space Mono; font-size:0.62rem; color:#4a6a8a; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.6rem">Organisations — Top 20</div>''', unsafe_allow_html=True)
        for org, cnt in org_counts.items():
            c = ORG_COLORS.get(org, "#6688aa")
            pct = int(cnt / org_counts.max() * 100)
            st.markdown(f"""<div style="margin-bottom:0.4rem">
                <div style="display:flex; justify-content:space-between; margin-bottom:2px">
                    <span style="font-size:0.74rem; color:#c8d8e8">{org}</span>
                    <span style="font-family:Space Mono; font-size:0.65rem; color:{c}">{cnt} modèles</span>
                </div>
                <div style="background:#0d1520; border-radius:2px; height:5px">
                    <div style="background:{c}; width:{pct}%; height:5px; border-radius:2px"></div>
                </div></div>""", unsafe_allow_html=True)

        # Répartition licences Top 20
        lic_counts = top20["licence"].value_counts()
        st.markdown('''<div style="font-family:Space Mono; font-size:0.62rem; color:#4a6a8a; text-transform:uppercase; letter-spacing:0.1em; margin:1rem 0 0.6rem 0">Licences — Top 20</div>''', unsafe_allow_html=True)
        total_lic = lic_counts.sum()
        lic_html = ""
        for lic, cnt in lic_counts.items():
            c = LICENCE_COLORS.get(lic, "#4a6a8a")
            pct_w = int(cnt / total_lic * 100)
            lic_html += f'<span style="background:{c}22; border:1px solid {c}66; border-radius:3px; padding:2px 8px; font-size:0.68rem; color:{c}; margin-right:6px; white-space:nowrap">{lic} {pct_w}%</span>'
        st.markdown(f'<div style="line-height:2">{lic_html}</div>', unsafe_allow_html=True)

        # Lien source
        st.markdown('''<div style="margin-top:1rem; font-size:0.68rem; color:#4a6a8a; font-family:Space Mono">
            Source : <a href="https://comparia.beta.gouv.fr/ranking" target="_blank" style="color:#00e5ff; text-decoration:none">compar:IA — beta.gouv.fr</a>
            · Score Bradley-Terry · Préférences utilisateurs FR
        </div>''', unsafe_allow_html=True)

# ── INDICATEURS SIGNAUX FAIBLES ────────────────────────────────────────────────
def build_word_freq(df, n=80):
    """Extrait les mots les plus fréquents des titres RSS."""
    import re, collections
    STOP = {
        "le","la","les","de","du","des","un","une","en","et","à","au","aux",
        "pour","sur","par","avec","dans","est","que","qui","se","ne","pas",
        "plus","this","that","the","and","for","with","from","has","are","its",
        "have","will","new","can","how","was","but","not","you","all","also",
        "been","more","said","says","after","over","their","they","what",
        "into","than","other","about","l","d","s","c","j","n","m","y",
    }
    words = []
    for title in df["titre"].dropna():
        for w in re.split(r"[^a-zA-ZÀ-ÿ]+", title.lower()):
            if len(w) > 3 and w not in STOP:
                words.append(w)
    return collections.Counter(words).most_common(n)

def render_wordcloud_html(freq_list, max_words=50):
    """Génère un nuage de mots en HTML pur — aucune dépendance."""
    import random
    if not freq_list:
        return "<div style='color:#4a6a8a'>Pas assez de données.</div>"
    top = freq_list[:max_words]
    max_count = top[0][1] if top else 1
    COLORS = ["#00e5ff","#ffaa00","#00e5a0","#aa88ff","#ff8844","#44aaff","#ff4d6d","#aabb66"]
    random.shuffle(COLORS)
    words_html = ""
    for i, (word, count) in enumerate(top):
        size  = 0.7 + (count / max_count) * 1.8   # em, entre 0.7 et 2.5
        color = COLORS[i % len(COLORS)]
        opacity = 0.6 + (count / max_count) * 0.4
        words_html += f'<span style="font-size:{size:.2f}em; color:{color}; opacity:{opacity}; margin:4px 6px; display:inline-block; font-family:DM Sans; line-height:1.2">{word}</span>'
    return f'<div style="background:#0d1520; border:1px solid #1a2a3a; border-radius:4px; padding:1.2rem; line-height:2; text-align:center">{words_html}</div>'

# ── INDICATEURS NUMÉRIQUE ──────────────────────────────────────────────────────
def parse_github_trending(df):
    """Extrait les infos structurées des entrées GitHub Trending RSS."""
    import re
    projects = []
    gh = df[df["source"].str.contains("GitHub", case=False, na=False)]
    for _, row in gh.iterrows():
        title = row["titre"]
        resume = row.get("resume", "")
        # Titre typique: "owner/repo" ou "owner / repo"
        match = re.match(r"^([^/\s]+)\s*/\s*(.+)$", title.strip())
        if match:
            owner, repo = match.group(1).strip(), match.group(2).strip()
        else:
            owner, repo = "", title.strip()
        # Cherche les étoiles dans le résumé
        stars = re.search(r"([\d,]+)\s*stars?", resume, re.I)
        stars_txt = stars.group(0) if stars else ""
        # Cherche le langage
        lang = re.search(r"language[\s:]+([A-Za-z+#]+)", resume, re.I)
        lang_txt = lang.group(1) if lang else ""
        projects.append({
            "owner": owner, "repo": repo,
            "stars": stars_txt, "lang": lang_txt,
            "url": row.get("url",""), "resume": resume[:120],
            "source": row["source"]
        })
    return projects[:5]

def parse_hf_papers(df):
    """Extrait les papiers Hugging Face."""
    papers = []
    hf = df[df["source"].str.contains("Hugging Face|takara|papers", case=False, na=False)]
    for _, row in hf.head(3).iterrows():
        papers.append({
            "titre": row["titre"][:80],
            "url":   row.get("url",""),
            "date":  row.get("date",""),
        })
    return papers
# ── CHEMINS ────────────────────────────────────────────────────────────────────
base              = os.path.dirname(os.path.abspath(__file__))
pers_rss_path     = os.path.join(base, "data", "personnes_rss.csv")
thema_rss_path    = os.path.join(base, "data", "thematiques_rss.csv")
energie_rss_path  = os.path.join(base, "data", "energie_rss.csv")
economie_rss_path = os.path.join(base, "data", "economie_rss.csv")
regl_rss_path     = os.path.join(base, "data", "reglementation_rss.csv")
marches_rss_path  = os.path.join(base, "data", "marches_rss.csv")
numerique_rss_path= os.path.join(base, "data", "numerique_rss.csv")
personnes_path    = os.path.join(base, "data", "personnes.csv")

@st.cache_data
def load_personnes():
    return pd.read_csv(personnes_path)

personnes = load_personnes()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="radar-header">
    <span class="radar-title">◈ Innovation Radar</span>
    <span class="radar-subtitle">Tableau de bord prospectif</span>
</div>""", unsafe_allow_html=True)

tabs = st.tabs(["⚡📈 Énergie & Économie", "👤 Personnes", "📡 Signaux Faibles", "⚖️ Réglementation", "📊 Marchés & Indices", "💻 Numérique & Open Source", "🧠 Synthèse IA"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ÉNERGIE & ÉCONOMIE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    _, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄 Rafraîchir", key="ref_ee", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    sub_e, sub_eco = st.tabs(["⚡ Énergie", "📈 Économie"])

    with sub_e:
        try:
            enr_src = pd.read_csv(energie_rss_path)
            cats  = ["Toutes"] + sorted(enr_src["categorie"].dropna().unique().tolist())
            langs = ["Toutes"] + sorted(enr_src["langue"].dropna().unique().tolist())
        except Exception:
            enr_src = pd.DataFrame(); cats = ["Toutes"]; langs = ["Toutes"]

        cf1, cf2 = st.columns(2)
        with cf1: filtre_ec = st.selectbox("Catégorie", cats, key="e_cat")
        with cf2: filtre_el = st.selectbox("Langue", langs, key="e_lang")

        st.markdown('<div class="section-header-orange">📡 Actualités énergie — IEA · RTE · médias spécialisés</div>', unsafe_allow_html=True)
        with st.spinner("Chargement…"):
            e_art = fetch_rss(energie_rss_path, max_per_source=4)

        if e_art.empty:
            st.warning("Aucun article. Vérifiez data/energie_rss.csv")
        else:
            df_e = e_art.copy()
            if filtre_ec != "Toutes": df_e = df_e[df_e["categorie"] == filtre_ec]
            if filtre_el != "Toutes" and not enr_src.empty:
                df_e = df_e[df_e["source"].isin(enr_src[enr_src["langue"] == filtre_el]["nom"].tolist())]
            render_articles(df_e, "#ffaa00")

        with st.expander("Ajouter une source énergie"):
            st.info("Éditez `data/energie_rss.csv` dans GitHub.")
            st.code("NOM,URL_FLUX,CATEGORIE,LANGUE", language="text")

    with sub_eco:
        try:
            eco_src = pd.read_csv(economie_rss_path)
            cats_e  = ["Toutes"] + sorted(eco_src["categorie"].dropna().unique().tolist())
            langs_e = ["Toutes"] + sorted(eco_src["langue"].dropna().unique().tolist())
        except Exception:
            eco_src = pd.DataFrame(); cats_e = ["Toutes"]; langs_e = ["Toutes"]

        cf1, cf2 = st.columns(2)
        with cf1: filtre_ecc = st.selectbox("Catégorie", cats_e, key="eco_cat")
        with cf2: filtre_ecl = st.selectbox("Langue",    langs_e, key="eco_lang")

        st.markdown('<div class="section-header-green">📡 Actualités économie — INSEE · BCE · OCDE · médias</div>', unsafe_allow_html=True)
        with st.spinner("Chargement…"):
            eco_art = fetch_rss(economie_rss_path, max_per_source=4)

        if eco_art.empty:
            st.warning("Aucun article. Vérifiez data/economie_rss.csv")
        else:
            df_eco = eco_art.copy()
            if filtre_ecc != "Toutes": df_eco = df_eco[df_eco["categorie"] == filtre_ecc]
            if filtre_ecl != "Toutes" and not eco_src.empty:
                df_eco = df_eco[df_eco["source"].isin(eco_src[eco_src["langue"] == filtre_ecl]["nom"].tolist())]
            render_articles(df_eco, "#00e5a0")

        with st.expander("Ajouter une source économie"):
            st.info("Éditez `data/economie_rss.csv` dans GitHub.")
            st.code("NOM,URL_FLUX,CATEGORIE,LANGUE", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PERSONNES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        courants = ["Tous"] + sorted(personnes["courant"].dropna().unique().tolist())
        filtre_courant = st.selectbox("Filtrer par courant", courants)
    with col_f2:
        if st.button("🔄 Rafraîchir", key="ref_pers", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    st.markdown('<div class="section-header">📡 Derniers articles publiés</div>', unsafe_allow_html=True)
    with st.spinner("Chargement…"):
        pers_art = fetch_rss(pers_rss_path, max_per_source=4)

    if pers_art.empty:
        st.warning("Aucun article. Vérifiez data/personnes_rss.csv")
    else:
        df_pa = pers_art.copy()
        if filtre_courant != "Tous":
            df_pa = df_pa[df_pa["courant"] == filtre_courant]
        for _, row in df_pa.head(20).iterrows():
            c = color_for(row["domaine"])
            url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
            st.markdown(f"""
            <div class="signal-card" style="border-color:{c}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                    <div class="signal-title">{row["titre"]}</div>
                    <span class="tag" style="border-color:{c}44; color:{c}; white-space:nowrap">{row["source"].split("(")[0].strip()}</span>
                </div>
                <div class="signal-meta">{row["date"]} · {row["courant"]}</div>
                <div class="signal-note">{row["resume"]}</div>
                <div style="margin-top:0.4rem">{url_html}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Profils suivis</div>', unsafe_allow_html=True)
    df_p = personnes if filtre_courant == "Tous" else personnes[personnes["courant"] == filtre_courant]
    cols = st.columns(2)
    for i, (_, row) in enumerate(df_p.iterrows()):
        with cols[i % 2]:
            url_html = f'<a class="person-link" href="{row["url_profil"]}" target="_blank">→ Profil</a>' if pd.notna(row.get("url_profil","")) and row.get("url_profil","") else ""
            rss_html = f'&nbsp;&nbsp;<a class="person-link" href="{row["url_flux"]}" target="_blank">RSS</a>' if pd.notna(row.get("url_flux","")) and row.get("url_flux","") else ""
            st.markdown(f"""
            <div class="person-card">
                <div class="person-name">{row["nom"]}</div>
                <div class="person-courant">{row["courant"]}</div>
                <div class="person-focus">{row["focus"]}</div>
                <div class="person-note">{row["note"]}</div>
                <div style="margin-top:0.5rem">{url_html}{rss_html}</div>
            </div>""", unsafe_allow_html=True)

    st.info("💡 Éditez `data/personnes.csv` et `data/personnes_rss.csv` dans GitHub pour ajouter des personnes.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SIGNAUX FAIBLES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    try:
        thema_src = pd.read_csv(thema_rss_path)
        dom_opts  = ["Tous"]   + sorted(thema_src["domaine"].dropna().unique().tolist())
        lang_opts = ["Toutes"] + sorted(thema_src["langue"].dropna().unique().tolist())
    except Exception:
        thema_src = pd.DataFrame(); dom_opts = ["Tous"]; lang_opts = ["Toutes"]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: filtre_t_dom = st.selectbox("Domaine", dom_opts, key="sf_dom")
    with col2: filtre_lang  = st.selectbox("Langue",  lang_opts, key="sf_lang")
    with col3:
        if st.button("🔄 Rafraîchir", key="ref_sf", use_container_width=True):
            st.cache_data.clear(); st.rerun()


    # ── Indicateurs Signaux Faibles ───────────────────────────────────────────
    with st.spinner("Analyse des tendances…"):
        all_sf = fetch_rss(thema_rss_path, max_per_source=8)

    if not all_sf.empty:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown('''<div class="section-header">☁️ Nuage de mots — titres des 100 derniers articles</div>''', unsafe_allow_html=True)
            freq = build_word_freq(all_sf)
            st.markdown(render_wordcloud_html(freq, max_words=50), unsafe_allow_html=True)
        with c2:
            st.markdown('''<div class="section-header">📊 Domaines les plus actifs</div>''', unsafe_allow_html=True)
            dom_counts = all_sf.groupby("domaine").size().sort_values(ascending=False).head(8)
            if not dom_counts.empty:
                dom_max = dom_counts.max()
                for dom, cnt in dom_counts.items():
                    pct = int(cnt / dom_max * 100)
                    c = color_for(str(dom))
                    st.markdown(f"""<div style="margin-bottom:0.5rem">
                        <div style="display:flex; justify-content:space-between; margin-bottom:2px">
                            <span style="font-size:0.75rem; color:#c8d8e8">{dom}</span>
                            <span style="font-family:Space Mono; font-size:0.65rem; color:{c}">{cnt}</span>
                        </div>
                        <div style="background:#0d1520; border-radius:2px; height:4px">
                            <div style="background:{c}; width:{pct}%; height:4px; border-radius:2px"></div>
                        </div></div>""", unsafe_allow_html=True)
            # Top 3 mots du moment
            if freq:
                top3 = " · ".join(f'<span style="color:#00e5ff">{w}</span>' for w, _ in freq[:3])
                st.markdown(f'''<div style="margin-top:1rem; font-size:0.72rem; color:#4a6a8a; font-family:Space Mono">
                    🔥 Mots dominants : {top3}</div>''', unsafe_allow_html=True)
    st.markdown("")
    st.markdown('<div class="section-header">📡 Veille thématique — flux automatiques</div>', unsafe_allow_html=True)
    with st.spinner("Chargement…"):
        thema_art = fetch_rss(thema_rss_path, max_per_source=3)

    if thema_art.empty:
        st.warning("Aucun article.")
    else:
        df_t = thema_art.copy()
        if filtre_t_dom != "Tous": df_t = df_t[df_t["domaine"] == filtre_t_dom]
        if filtre_lang != "Toutes" and not thema_src.empty:
            df_t = df_t[df_t["source"].isin(thema_src[thema_src["langue"] == filtre_lang]["nom"].tolist())]
        render_articles(df_t, "#6688aa", max_items=40)

    with st.expander("Ajouter une source thématique"):
        st.info("Éditez `data/thematiques_rss.csv` dans GitHub.")
        st.code("NOM,URL_FLUX,DOMAINE,LANGUE", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — RÉGLEMENTATION
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    try:
        regl_src = pd.read_csv(regl_rss_path)
        domaines_regl = ["Tous"] + sorted(regl_src["domaine"].dropna().unique().tolist())
        langs_regl    = ["Toutes"] + sorted(regl_src["langue"].dropna().unique().tolist())
    except Exception:
        regl_src = pd.DataFrame(); domaines_regl = ["Tous"]; langs_regl = ["Toutes"]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: filtre_rd = st.selectbox("Domaine", domaines_regl, key="regl_dom")
    with col2: filtre_rl = st.selectbox("Langue",  langs_regl,    key="regl_lang")
    with col3:
        if st.button("🔄", key="ref_regl", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    sub_eu, sub_us, sub_fr = st.tabs(["🇪🇺 Europe", "🇺🇸 USA", "🇫🇷 France"])

    with st.spinner("Chargement des flux réglementaires…"):
        regl_art = fetch_rss(regl_rss_path, max_per_source=5)

    for sub, zone_name, zone_color in [
        (sub_eu, "Europe", "#4488ff"),
        (sub_us, "USA",    "#ff6644"),
        (sub_fr, "France", "#6644ff"),
    ]:
        with sub:
            st.markdown(f'<div class="section-header" style="color:{zone_color}; border-color:{zone_color}">📡 Textes & actualités — {zone_name}</div>', unsafe_allow_html=True)

            if regl_art.empty:
                st.warning("Aucun article. Vérifiez data/reglementation_rss.csv")
            else:
                df_r = regl_art.copy()
                # Filtrer par zone
                if zone_name == "USA":
                    sources_zone = regl_src[regl_src["zone"].isin(["USA", "USA/Global"])]["nom"].tolist() if not regl_src.empty else []
                else:
                    sources_zone = regl_src[regl_src["zone"] == zone_name]["nom"].tolist() if not regl_src.empty else []
                if sources_zone:
                    df_r = df_r[df_r["source"].isin(sources_zone)]
                # Filtres globaux
                if filtre_rd != "Tous":
                    df_r = df_r[df_r["domaine"] == filtre_rd]
                if filtre_rl != "Toutes" and not regl_src.empty:
                    df_r = df_r[df_r["source"].isin(regl_src[regl_src["langue"] == filtre_rl]["nom"].tolist())]

                if df_r.empty:
                    st.markdown("""<div style="background:#0d1520; border:1px solid #1a2a3a;
                        border-radius:4px; padding:1rem; color:#4a6a8a; font-size:0.8rem; text-align:center">
                        Aucun texte détecté pour cette zone / ce filtre.</div>""", unsafe_allow_html=True)
                else:
                    for _, row in df_r.head(25).iterrows():
                        dom = str(row.get("domaine","")).lower()
                        if "énergie" in dom or "energy" in dom: c = "#ffaa00"
                        elif "transport" in dom: c = "#aa88ff"
                        elif "ia" in dom: c = "#00e5ff"
                        else: c = zone_color
                        url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Texte officiel</a>' if row["url"] else ""
                        dom_tag  = f'<span class="tag" style="border-color:{c}44; color:{c}">{row.get("domaine","")}</span>'
                        lang_tag = f'<span class="tag">{row.get("langue","")}</span>'
                        st.markdown(f"""
                        <div class="signal-card" style="border-color:{c}">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                                <div class="signal-title">{row["titre"]}</div>
                                <div style="white-space:nowrap; flex-shrink:0">{dom_tag} {lang_tag}</div>
                            </div>
                            <div class="signal-meta">{row["date"]} · {row["source"]}</div>
                            <div class="signal-note">{row["resume"]}</div>
                            <div style="margin-top:0.4rem">{url_html}</div>
                        </div>""", unsafe_allow_html=True)

    with st.expander("Ajouter une source réglementaire"):
        st.info("Éditez `data/reglementation_rss.csv` dans GitHub.")
        st.code("NOM,URL_FLUX,DOMAINE,ZONE,LANGUE\n# ZONE = Europe | USA | France | Chine | Global", language="text")
        st.markdown("""<div style="font-size:0.75rem; color:#4a6a8a; margin-top:0.5rem">
        <b style="color:#c8d8e8">Sources à ajouter :</b>
        ENISA (cybersécurité EU) · NHTSA (véhicules autonomes USA) · SEC · EPA · MIIT Chine
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MARCHÉS & INDICES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    _, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄", key="ref_marches", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    try:
        marches_src = pd.read_csv(marches_rss_path)
        cats_m = ["Toutes"] + sorted(marches_src["categorie"].dropna().unique().tolist())
    except Exception:
        marches_src = pd.DataFrame(); cats_m = ["Toutes"]

    filtre_mc = st.selectbox("Catégorie", cats_m, key="m_cat")


    # ── Indicateurs prix ──────────────────────────────────────────────────────
    st.markdown('''<div class="section-header-orange">📈 Prix en temps réel — 14 derniers jours</div>''', unsafe_allow_html=True)

    with st.spinner("Chargement des prix…"):
        prices = fetch_prices()

    if not prices:
        st.info("📦 Installation de yfinance en cours sur Streamlit Cloud… Les prix apparaîtront au prochain démarrage.")
    else:
        st.markdown("**🛢️ Énergie**")
        render_price_cards(prices, [
            ("Brent",       "$/bbl", 2, "#ffaa00"),
            ("WTI",         "$/bbl", 2, "#ff8844"),
            ("Gaz naturel", "$/MMBtu", 2, "#ffcc44"),
        ])
        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**💱 Devises & Crypto**")
            render_price_cards(prices, [
                ("EUR/USD",  "", 4, "#00e5a0"),
                ("USD/CNY",  "", 3, "#44aaff"),
                ("Bitcoin",  "$", 0, "#ff9900"),
            ])
        with c2:
            st.markdown("**🔋 Proxy Matières premières**")
            render_price_cards(prices, [
                ("Lithium ETF", "$", 2, "#aa88ff"),
            ])

    st.markdown("")
    CAT_COLORS = {
        "Énergie & Matières premières": "#ffaa00",
        "Devises & Crypto": "#00e5a0",
        "IA Benchmarks": "#00e5ff",
    }

    with st.spinner("Chargement des flux marchés…"):
        marches_art = fetch_rss(marches_rss_path, max_per_source=6)


    # ── Classement compar:IA ──────────────────────────────────────────────────
    st.markdown('<div class="section-header" style="color:#00e5ff; border-color:#00e5ff">🤖 Classement LLM — compar:IA (beta.gouv.fr)</div>', unsafe_allow_html=True)
    with st.spinner("Chargement du classement compar:IA…"):
        comparia_df = fetch_comparia()
    render_comparia(comparia_df)
    st.markdown("---")

    if marches_art.empty:
        st.warning("Aucun article. Vérifiez data/marches_rss.csv")
    else:
        # Grouper par catégorie
        cats_dispo = marches_src["categorie"].dropna().unique().tolist() if not marches_src.empty else []
        cats_show  = [filtre_mc] if filtre_mc != "Toutes" else cats_dispo

        for cat in cats_show:
            c = CAT_COLORS.get(cat, "#6688aa")
            emoji = {"Énergie & Matières premières": "🛢️", "Devises & Crypto": "💱", "IA Benchmarks": "🤖"}.get(cat, "📊")
            st.markdown(f'''<div class="section-header" style="color:{c}; border-color:{c}">{emoji} {cat}</div>''', unsafe_allow_html=True)

            sources_cat = marches_src[marches_src["categorie"] == cat]["nom"].tolist() if not marches_src.empty else []
            df_m = marches_art[marches_art["source"].isin(sources_cat)] if sources_cat else marches_art

            if df_m.empty:
                st.markdown('<div style="color:#4a6a8a; font-size:0.8rem; margin-bottom:1rem">Aucun article pour cette catégorie.</div>', unsafe_allow_html=True)
                continue

            # Grouper par source dans chaque catégorie
            for src_name in sources_cat:
                df_src = df_m[df_m["source"] == src_name].head(4)
                if df_src.empty:
                    continue
                emoji_src = marches_src[marches_src["nom"] == src_name]["emoji"].values
                e = emoji_src[0] if len(emoji_src) > 0 else "📌"
                st.markdown(f'''<div style="font-family:Space Mono,monospace; font-size:0.65rem; color:{c}; text-transform:uppercase;
                    letter-spacing:0.1em; margin: 0.8rem 0 0.4rem 0; opacity:0.8">{e} {src_name}</div>''', unsafe_allow_html=True)
                for _, row in df_src.iterrows():
                    url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
                    st.markdown(f"""
                    <div class="signal-card" style="border-color:{c}; margin-bottom:0.4rem">
                        <div class="signal-title" style="font-size:0.84rem">{row["titre"]}</div>
                        <div class="signal-meta">{row["date"]} · {row["source"]}</div>
                        <div class="signal-note">{row["resume"]}</div>
                        <div style="margin-top:0.3rem">{url_html}</div>
                    </div>""", unsafe_allow_html=True)

    with st.expander("Ajouter une source"):
        st.info("Éditez `data/marches_rss.csv` dans GitHub.")
        st.code("NOM,URL_FLUX,CATEGORIE,EMOJI", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — NUMÉRIQUE & OPEN SOURCE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    _, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄", key="ref_num", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    try:
        num_src = pd.read_csv(numerique_rss_path)
        cats_n = ["Toutes"] + sorted(num_src["categorie"].dropna().unique().tolist())
    except Exception:
        num_src = pd.DataFrame(); cats_n = ["Toutes"]

    filtre_nc = st.selectbox("Catégorie", cats_n, key="n_cat")


    # ── Indicateurs Numérique ─────────────────────────────────────────────────
    with st.spinner("Analyse des tendances open source…"):
        all_num = fetch_rss(numerique_rss_path, max_per_source=10)

    if not all_num.empty:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown('''<div class="section-header" style="color:#6e40c9; border-color:#6e40c9">⭐ Top 5 projets GitHub du jour</div>''', unsafe_allow_html=True)
            projects = parse_github_trending(all_num)
            if projects:
                for i, p in enumerate(projects, 1):
                    lang_tag = f'<span class="tag" style="color:#6e40c9; border-color:#6e40c944">{p["lang"]}</span>' if p["lang"] else ""
                    stars_tag = f'<span class="tag" style="color:#ffaa00; border-color:#ffaa0044">⭐ {p["stars"]}</span>' if p["stars"] else ""
                    url_html = f'<a class="person-link" href="{p["url"]}" target="_blank">→ GitHub</a>' if p["url"] else ""
                    st.markdown(f"""<div class="signal-card" style="border-color:#6e40c9; margin-bottom:0.4rem">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                            <div>
                                <span style="font-family:Space Mono; font-size:0.7rem; color:#4a6a8a">#{i} </span>
                                <span class="signal-title" style="font-family:Space Mono">{p["owner"]}<span style="color:#4a6a8a">/</span>{p["repo"]}</span>
                            </div>
                            <div style="white-space:nowrap">{lang_tag} {stars_tag}</div>
                        </div>
                        <div class="signal-note" style="margin-top:0.3rem">{p["resume"]}</div>
                        <div style="margin-top:0.3rem">{url_html}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#4a6a8a; font-size:0.8rem">Flux GitHub en cours de chargement…</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('''<div class="section-header" style="color:#ff9d00; border-color:#ff9d00">🤗 Papers du jour — Hugging Face</div>''', unsafe_allow_html=True)
            papers = parse_hf_papers(all_num)
            if papers:
                for p in papers:
                    url_html = f'<a class="person-link" href="{p["url"]}" target="_blank" style="color:#ff9d00; border-color:#ff9d0044">→ Paper</a>' if p["url"] else ""
                    st.markdown(f"""<div class="signal-card" style="border-color:#ff9d00; margin-bottom:0.5rem; padding:0.6rem 0.8rem">
                        <div class="signal-title" style="font-size:0.8rem">{p["titre"]}</div>
                        <div class="signal-meta">{p["date"]}</div>
                        {url_html}
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#4a6a8a; font-size:0.8rem">Chargement des papers…</div>', unsafe_allow_html=True)

            # Langages dominants dans le trending
            st.markdown('''<div class="section-header" style="color:#6e40c9; border-color:#6e40c9; margin-top:1rem">🐍 Langages trending</div>''', unsafe_allow_html=True)
            import re as _re
            lang_counts = {}
            gh_art = all_num[all_num["source"].str.contains("GitHub|python|javascript", case=False, na=False)]
            for _, row in gh_art.iterrows():
                m = _re.search(r"language[\s:]+([A-Za-z+#]+)", str(row.get("resume","")), _re.I)
                if m:
                    l = m.group(1)
                    lang_counts[l] = lang_counts.get(l, 0) + 1
            # Source heuristic : python feed → Python
            py_count = len(all_num[all_num["source"].str.contains("Python", case=False, na=False)])
            js_count = len(all_num[all_num["source"].str.contains("JavaScript", case=False, na=False)])
            if py_count: lang_counts["Python"] = lang_counts.get("Python", 0) + py_count
            if js_count: lang_counts["JavaScript"] = lang_counts.get("JavaScript", 0) + js_count
            if lang_counts:
                lmax = max(lang_counts.values())
                LANG_COLORS = {"Python":"#3776ab","JavaScript":"#f7df1e","Rust":"#ff4a00","TypeScript":"#3178c6","Go":"#00add8"}
                for lang, cnt in sorted(lang_counts.items(), key=lambda x: -x[1])[:5]:
                    pct = int(cnt / lmax * 100)
                    c = LANG_COLORS.get(lang, "#6e40c9")
                    st.markdown(f"""<div style="margin-bottom:0.4rem">
                        <div style="display:flex; justify-content:space-between; margin-bottom:2px">
                            <span style="font-size:0.72rem; color:#c8d8e8">{lang}</span>
                            <span style="font-family:Space Mono; font-size:0.62rem; color:{c}">{cnt}</span>
                        </div>
                        <div style="background:#0d1520; border-radius:2px; height:4px">
                            <div style="background:{c}; width:{pct}%; height:4px; border-radius:2px"></div>
                        </div></div>""", unsafe_allow_html=True)
    st.markdown("")
    CAT_COLORS_N = {
        "GitHub Trending": "#6e40c9",
        "Hugging Face": "#ff9d00",
    }

    with st.spinner("Chargement des flux numériques…"):
        num_art = fetch_rss(numerique_rss_path, max_per_source=8)

    if num_art.empty:
        st.warning("Aucun article. Vérifiez data/numerique_rss.csv")
    else:
        cats_n_dispo = num_src["categorie"].dropna().unique().tolist() if not num_src.empty else []
        cats_n_show  = [filtre_nc] if filtre_nc != "Toutes" else cats_n_dispo

        for cat in cats_n_show:
            c = CAT_COLORS_N.get(cat, "#6688aa")
            emoji = {"GitHub Trending": "⭐", "Hugging Face": "🤗"}.get(cat, "💻")
            st.markdown(f'''<div class="section-header" style="color:{c}; border-color:{c}">{emoji} {cat}</div>''', unsafe_allow_html=True)

            sources_cat = num_src[num_src["categorie"] == cat]["nom"].tolist() if not num_src.empty else []
            df_n = num_art[num_art["source"].isin(sources_cat)] if sources_cat else num_art

            if df_n.empty:
                st.markdown('<div style="color:#4a6a8a; font-size:0.8rem; margin-bottom:1rem">Aucun article pour cette catégorie.</div>', unsafe_allow_html=True)
                continue

            for src_name in sources_cat:
                df_src = df_n[df_n["source"] == src_name].head(8)
                if df_src.empty:
                    continue
                emoji_src = num_src[num_src["nom"] == src_name]["emoji"].values
                e = emoji_src[0] if len(emoji_src) > 0 else "📌"
                st.markdown(f'''<div style="font-family:Space Mono,monospace; font-size:0.65rem; color:{c}; text-transform:uppercase;
                    letter-spacing:0.1em; margin: 0.8rem 0 0.4rem 0; opacity:0.8">{e} {src_name}</div>''', unsafe_allow_html=True)
                for _, row in df_src.iterrows():
                    url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Voir le projet</a>' if row["url"] else ""
                    st.markdown(f"""
                    <div class="signal-card" style="border-color:{c}; margin-bottom:0.4rem">
                        <div class="signal-title" style="font-size:0.84rem">{row["titre"]}</div>
                        <div class="signal-meta">{row["date"]} · {row["source"]}</div>
                        <div class="signal-note">{row["resume"]}</div>
                        <div style="margin-top:0.3rem">{url_html}</div>
                    </div>""", unsafe_allow_html=True)

    with st.expander("Ajouter une source"):
        st.info("Éditez `data/numerique_rss.csv` dans GitHub.")
        st.code("NOM,URL_FLUX,CATEGORIE,EMOJI", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — SYNTHÈSE IA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    try:
        from google import genai as genai_client
        api_key = st.secrets["GEMINI_API_KEY"]
        api_ok  = True
    except Exception:
        api_ok = False

    if not api_ok:
        st.error("Clé GEMINI_API_KEY introuvable. Va dans Settings → Secrets sur Streamlit Cloud.")
        st.stop()

    st.markdown('<div class="section-header">Synthèse IA — analyse personnalisée des tendances</div>', unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def charger_toutes_sources(pp, tp, ep, ecp, rp, mp, np_):
        dfs = []
        for path, n in [(pp, 5), (tp, 4), (ep, 5), (ecp, 5), (rp, 3), (mp, 3), (np_, 3)]:
            df = fetch_rss(path, max_per_source=n)
            if not df.empty: dfs.append(df)
        if not dfs: return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["titre"]).sort_values("date", ascending=False)

    with st.spinner("Chargement de toutes les sources…"):
        tous_articles = charger_toutes_sources(pers_rss_path, thema_rss_path, energie_rss_path, economie_rss_path, regl_rss_path, marches_rss_path, numerique_rss_path)

    nb_art = len(tous_articles)
    nb_src = sum(len(pd.read_csv(p)) for p in [pers_rss_path, thema_rss_path, energie_rss_path, economie_rss_path, regl_rss_path, marches_rss_path, numerique_rss_path] if os.path.exists(p))
    st.markdown(f"""
    <div style="background:#0d1520; border:1px solid #1a2a3a; border-radius:4px;
                padding:0.7rem 1rem; margin-bottom:1rem; font-size:0.78rem; color:#4a6a8a;
                font-family:Space Mono,monospace;">
        {nb_art} articles chargés · {nb_src} sources actives
        (personnes suivies + veille thématique + énergie + économie)
    </div>""", unsafe_allow_html=True)

    def titres_prompt(df, n=15):
        return "\n".join(f"- [{r['date']}] {r['titre']} ({r['source']})" for _, r in df.head(n).iterrows())

    def articles_theme(mots_cles, df, n=12):
        if not mots_cles: return df.head(n)
        mask = df["titre"].str.lower().apply(lambda t: any(m in t for m in mots_cles))
        return df[mask].head(n)

    def appel_gemini(prompt):
        try:
            client   = genai_client.Client(api_key=api_key)
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return response.text.strip()
        except Exception as e:
            return f"Erreur Gemini : {e}"

    THEMES = {
        "⚡ Énergie":   ["énergie", "energy", "solaire", "éolien", "nucléaire", "hydrogène", "batterie", "renouvelable", "pétrole", "gaz", "électrique", "iea", "rte"],
        "🤖 IA":        ["intelligence artificielle", "artificial intelligence", "machine learning", "llm", "gpt", "mistral", "gemini", "openai", "deepmind", "modèle", "chatgpt"],
        "🚗 Transport": ["transport", "mobilité", "véhicule", "voiture", "aviation", "train", "autonome", "ferroviaire", "fret"],
    }
    THEME_COLORS = {"⚡ Énergie": "#ffaa00", "🤖 IA": "#00e5ff", "🚗 Transport": "#aa88ff"}

    focus_pers  = "\n".join(f"- {r['nom']} ({r['courant']}) : {r['focus']}" for _, r in personnes.iterrows())
    sources_act = " · ".join(tous_articles["source"].unique().tolist()[:20]) if not tous_articles.empty else "—"

    _, col_btn = st.columns([4, 1])
    with col_btn:
        generer = st.button("✨ Générer", use_container_width=True, type="primary")

    if "syntheses" not in st.session_state:
        st.session_state.syntheses = {}

    if generer:
        st.session_state.syntheses = {}

        with st.spinner("Analyse globale…"):
            prompt_global = f"""Tu es un analyste senior en innovation et prospective technologique.
Tu prépares une note de veille ACTUALISEE et PERSONNALISÉE pour un veilleur qui suit spécifiquement ces personnes référentes :
{focus_pers}

Ses sources actives ce jour (incluant flux institutionnels INSEE, IEA, BCE, OCDE) : {sources_act}

Articles récents issus de toutes ces sources :
{titres_prompt(tous_articles, n=30)}

En 5 à 7 phrases en français, rédige une synthèse actualisée de la situation globale de l'innovation
TELLE QU'ELLE APPARAÎT À TRAVERS LE PRISME de ces personnes et de ces sources — pas un résumé générique.
Mets en avant ce que ces voix signalent, les convergences ou divergences entre leurs angles,
et les signaux forts qui émergent de cette veille particulière avec les informations de ce jour.
Intègre les données macro et énergie si elles ressortent des flux institutionnels."""
            st.session_state.syntheses["global"] = appel_gemini(prompt_global)

        for theme, mots_cles in THEMES.items():
            with st.spinner(f"Analyse {theme}…"):
                arts = articles_theme(mots_cles, tous_articles)
                pers_theme = personnes[personnes["focus"].str.lower().apply(
                    lambda f: any(m in str(f).lower() for m in mots_cles)
                )] if mots_cles else personnes
                pers_ctx = "\n".join(f"- {r['nom']} : {r['focus']}" for _, r in pers_theme.iterrows()) \
                           if not pers_theme.empty else "Aucune personne spécifiquement filtrée sur ce thème."

                prompt = f"""Tu es un expert en {theme.split(' ')[1]} rédigeant une note de veille personnalisée.

Personnes référentes suivies sur ce thème :
{pers_ctx}

Articles récents filtrés sur ce thème, issus des sources surveillées
(incluant flux institutionnels INSEE, IEA, BCE, OCDE si pertinents) :
{titres_prompt(arts) if not arts.empty else "Peu d'articles détectés sur ce thème dans les sources suivies."}

En 4 à 5 phrases en français, synthétise les tendances de ce jour sur {theme}
TELLES QU'ELLES RESSORTENT de ces sources et de ces personnes spécifiquement.
Cite si pertinent ce que signalent ces voix particulières.
Intègre les chiffres ou décisions officielles actualisées si présents dans les flux.
Identifie ruptures et signaux à surveiller."""
                st.session_state.syntheses[theme] = {
                    "texte":    appel_gemini(prompt),
                    "nb":       len(arts),
                    "articles": arts,
                }

    # ── Affichage ──────────────────────────────────────────────────────────────
    if st.session_state.syntheses:
        if "global" in st.session_state.syntheses:
            st.markdown(f"""
            <div class="synthese-card" style="border:1px solid #00e5ff33; border-left:3px solid #00e5ff">
                <div class="synthese-theme" style="color:#00e5ff">◈ Situation globale · vue de ta veille</div>
                {st.session_state.syntheses["global"]}
            </div>""", unsafe_allow_html=True)

        cols_t = st.columns(3)
        for theme, col in zip(THEMES.keys(), cols_t):
            if theme not in st.session_state.syntheses: continue
            data = st.session_state.syntheses[theme]
            c    = THEME_COLORS.get(theme, "#6688aa")
            with col:
                st.markdown(f"""
                <div class="synthese-card" style="border:1px solid {c}33; border-top:2px solid {c}; min-height:260px">
                    <div class="synthese-theme" style="color:{c}">{theme} · {data["nb"]} articles</div>
                    {data["texte"]}
                </div>""", unsafe_allow_html=True)
                with st.expander(f"Sources ({data['nb']})"):
                    for _, row in data["articles"].iterrows():
                        url_html = f'<a class="person-link" href="{row.get("url","")}" target="_blank">→ Lire</a>' if row.get("url","") else ""
                        st.markdown(f"""
                        <div class="signal-card" style="border-color:#1a2a3a; padding:0.4rem 0.7rem; margin-bottom:0.3rem">
                            <div class="signal-title" style="font-size:0.78rem">{row["titre"]}</div>
                            <div class="signal-meta">{row["date"]} · {row["source"]}</div>
                            {url_html}
                        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#0d1520; border:1px dashed #1a2a3a; border-radius:4px;
                    padding:3rem; text-align:center; color:#4a6a8a;">
            <div style="font-size:2rem; margin-bottom:0.8rem">🧠</div>
            <div style="font-family:Space Mono; font-size:0.8rem">
                Clique sur <b style="color:#e8f4ff">✨ Générer</b> pour analyser les tendances
            </div>
            <div style="font-size:0.72rem; margin-top:0.5rem">
                Résumé global + fiches Énergie · IA · Transport — contextualisés à ta veille
            </div>
        </div>""", unsafe_allow_html=True)
