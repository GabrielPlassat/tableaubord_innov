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

# ── CHEMINS ────────────────────────────────────────────────────────────────────
base              = os.path.dirname(os.path.abspath(__file__))
pers_rss_path     = os.path.join(base, "data", "personnes_rss.csv")
thema_rss_path    = os.path.join(base, "data", "thematiques_rss.csv")
energie_rss_path  = os.path.join(base, "data", "energie_rss.csv")
economie_rss_path = os.path.join(base, "data", "economie_rss.csv")
regl_rss_path     = os.path.join(base, "data", "reglementation_rss.csv")
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

tabs = st.tabs(["⚡📈 Énergie & Économie", "👤 Personnes", "📡 Signaux Faibles", "⚖️ Réglementation", "🧠 Synthèse IA"])


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
# TAB 5 — SYNTHÈSE IA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
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
    def charger_toutes_sources(pp, tp, ep, ecp, rp):
        dfs = []
        for path, n in [(pp, 5), (tp, 4), (ep, 5), (ecp, 5), (rp, 3)]:
            df = fetch_rss(path, max_per_source=n)
            if not df.empty: dfs.append(df)
        if not dfs: return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["titre"]).sort_values("date", ascending=False)

    with st.spinner("Chargement de toutes les sources…"):
        tous_articles = charger_toutes_sources(pers_rss_path, thema_rss_path, energie_rss_path, economie_rss_path, regl_rss_path)

    nb_art = len(tous_articles)
    nb_src = sum(len(pd.read_csv(p)) for p in [pers_rss_path, thema_rss_path, energie_rss_path, economie_rss_path, regl_rss_path] if os.path.exists(p))
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
Tu prépares une note de veille PERSONNALISÉE pour un veilleur qui suit spécifiquement ces personnes référentes :
{focus_pers}

Ses sources actives ce jour (incluant flux institutionnels INSEE, IEA, BCE, OCDE) : {sources_act}

Articles récents issus de toutes ces sources :
{titres_prompt(tous_articles, n=30)}

En 5 à 7 phrases en français, rédige une synthèse de la situation globale de l'innovation
TELLE QU'ELLE APPARAÎT À TRAVERS LE PRISME de ces personnes et de ces sources — pas un résumé générique.
Mets en avant ce que ces voix signalent, les convergences ou divergences entre leurs angles,
et les signaux forts qui émergent de cette veille particulière ce jour.
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

En 4 à 5 phrases en français, synthétise les tendances sur {theme}
TELLES QU'ELLES RESSORTENT de ces sources et de ces personnes spécifiquement.
Cite si pertinent ce que signalent ces voix particulières.
Intègre les chiffres ou décisions officielles récentes si présents dans les flux.
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
