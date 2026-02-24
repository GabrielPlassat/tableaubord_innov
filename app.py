import os
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
html, body, [class*="css"] {
    background-color: #080c14; color: #c8d8e8; font-family: 'DM Sans', sans-serif;
}
.stApp { background-color: #080c14; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }

.radar-header {
    display: flex; align-items: baseline; gap: 1rem;
    border-bottom: 1px solid #1a2a3a; padding-bottom: 0.8rem; margin-bottom: 1.5rem;
}
.radar-title {
    font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700;
    color: #00e5ff; letter-spacing: 0.08em; text-transform: uppercase;
}
.radar-subtitle { font-size: 0.75rem; color: #4a6a8a; font-family: 'Space Mono', monospace; letter-spacing: 0.12em; }

.metric-card {
    background: #0d1520; border: 1px solid #1a2a3a;
    border-radius: 4px; padding: 1rem 1.2rem; transition: border-color 0.2s;
}
.metric-card:hover { border-color: #00e5ff44; }
.metric-label { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #4a6a8a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; color: #e8f4ff; line-height: 1; }
.metric-delta-up   { color: #00e5a0; font-size: 0.8rem; font-family: 'Space Mono', monospace; }
.metric-delta-down { color: #ff4d6d; font-size: 0.8rem; font-family: 'Space Mono', monospace; }
.metric-note { font-size: 0.72rem; color: #4a6a8a; margin-top: 0.4rem; }

.section-header {
    font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #00e5ff;
    text-transform: uppercase; letter-spacing: 0.2em;
    border-left: 2px solid #00e5ff; padding-left: 0.6rem; margin: 1.5rem 0 1rem 0;
}
.section-header-orange {
    font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #ffaa00;
    text-transform: uppercase; letter-spacing: 0.2em;
    border-left: 2px solid #ffaa00; padding-left: 0.6rem; margin: 1.5rem 0 1rem 0;
}
.section-header-green {
    font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #00e5a0;
    text-transform: uppercase; letter-spacing: 0.2em;
    border-left: 2px solid #00e5a0; padding-left: 0.6rem; margin: 1.5rem 0 1rem 0;
}

.tag {
    display: inline-block; background: #0d2030; border: 1px solid #1a3a5a;
    border-radius: 2px; padding: 1px 7px;
    font-size: 0.65rem; color: #6aadcc; font-family: 'Space Mono', monospace; margin: 1px 2px;
}
.person-card {
    background: #0d1520; border: 1px solid #1a2a3a; border-radius: 4px; padding: 1rem; margin-bottom: 0.8rem;
}
.person-name    { font-family: 'Space Mono', monospace; font-size: 0.9rem; font-weight: 700; color: #e8f4ff; }
.person-courant { font-size: 0.72rem; color: #00e5ff; margin: 0.15rem 0 0.5rem 0; }
.person-focus   { font-size: 0.78rem; color: #8aaabb; line-height: 1.4; }
.person-note    { font-size: 0.72rem; color: #4a7a8a; margin-top: 0.4rem; font-style: italic; }
.person-link    {
    display: inline-block; margin-top: 0.5rem; font-family: 'Space Mono', monospace;
    font-size: 0.62rem; color: #00e5ff; text-decoration: none; border-bottom: 1px solid #00e5ff44;
}
.signal-card {
    background: #0d1520; border-left: 3px solid;
    padding: 0.8rem 1rem; margin-bottom: 0.7rem; border-radius: 0 4px 4px 0;
}
.signal-title { font-size: 0.88rem; color: #e8f4ff; font-weight: 500; }
.signal-meta  { font-family: 'Space Mono', monospace; font-size: 0.62rem; color: #4a6a8a; margin-top: 0.3rem; }
.signal-note  { font-size: 0.75rem; color: #7a9aaa; margin-top: 0.35rem; }

.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: #0d1520; padding: 4px; border-radius: 4px; border: 1px solid #1a2a3a;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #4a6a8a;
    text-transform: uppercase; letter-spacing: 0.08em; background: transparent; border-radius: 2px; padding: 6px 16px;
}
.stTabs [aria-selected="true"] { background: #1a2a3a !important; color: #00e5ff !important; }

.synthese-card {
    background: #0d1520; border-radius: 4px; padding: 1.4rem; margin-bottom: 1.2rem;
    line-height: 1.75; font-size: 0.88rem; color: #c8d8e8;
}
.synthese-theme {
    font-family: 'Space Mono', monospace; font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────────────
PLOTLY_BASE = dict(
    paper_bgcolor="#080c14", plot_bgcolor="#080c14",
    font=dict(family="DM Sans", color="#8aaabb"),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#1a2a3a", zerolinecolor="#1a2a3a"),
    yaxis=dict(gridcolor="#1a2a3a", zerolinecolor="#1a2a3a"),
)
DOMAINE_COLORS = {
    "énergie": "#ffaa00", "energy": "#ffaa00", "prix": "#ffaa00", "renouvelable": "#ffaa00",
    "tech": "#00e5ff", "ia": "#00e5ff", "ai": "#00e5ff",
    "transport": "#aa88ff", "mobilité": "#aa88ff",
    "agri": "#00e5a0", "climat": "#44aaff", "transition": "#44aaff",
    "économie": "#ff8844", "macro": "#ff8844", "bce": "#ff8844", "géopolitique": "#ff8844",
    "industrie": "#aabb66",
}
def color_for(domaine):
    d = str(domaine).lower()
    for k, v in DOMAINE_COLORS.items():
        if k in d:
            return v
    return "#6688aa"

# ── CHARGEMENT DONNÉES STATIQUES ───────────────────────────────────────────────
@st.cache_data
def load_static():
    base = os.path.dirname(os.path.abspath(__file__))
    energie   = pd.read_csv(os.path.join(base, "data", "energie.csv"))
    economie  = pd.read_csv(os.path.join(base, "data", "economie.csv"))
    personnes = pd.read_csv(os.path.join(base, "data", "personnes.csv"))
    return energie, economie, personnes

# ── CHARGEMENT RSS GÉNÉRIQUE ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_rss(path, max_per_source=5):
    try:
        sources = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()
    items = []
    for _, src in sources.iterrows():
        try:
            feed = feedparser.parse(
                src["url_flux"],
                agent="Mozilla/5.0 (compatible; RSSReader/1.0)"
            )
            for entry in feed.entries[:max_per_source]:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                date_str = datetime.datetime(*pub[:6]).strftime("%Y-%m-%d") if pub else "—"
                items.append({
                    "date":      date_str,
                    "titre":     entry.get("title", "Sans titre"),
                    "url":       entry.get("link", ""),
                    "resume":    entry.get("summary", "")[:250]
                                 .replace("<p>","").replace("</p>","")
                                 .replace("<br>","").strip() + "…",
                    "source":    src["nom"],
                    "domaine":   src.get("domaine",   src.get("categorie", "")),
                    "categorie": src.get("categorie", ""),
                    "langue":    src.get("langue",    ""),
                    "courant":   src.get("courant",   ""),
                })
        except Exception:
            pass
    df = pd.DataFrame(items)
    return df.sort_values("date", ascending=False) if not df.empty else df

# ── CHEMINS ────────────────────────────────────────────────────────────────────
base             = os.path.dirname(os.path.abspath(__file__))
pers_rss_path    = os.path.join(base, "data", "personnes_rss.csv")
thema_rss_path   = os.path.join(base, "data", "thematiques_rss.csv")
energie_rss_path = os.path.join(base, "data", "energie_rss.csv")
economie_rss_path= os.path.join(base, "data", "economie_rss.csv")

energie, economie, personnes = load_static()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="radar-header">
    <span class="radar-title">◈ Innovation Radar</span>
    <span class="radar-subtitle">Tableau de bord prospectif</span>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(["⚡📈 Énergie & Économie", "👤 Personnes", "📡 Signaux Faibles", "🧠 Synthèse IA"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ÉNERGIE & ÉCONOMIE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:

    col_ctrl1, col_ctrl2 = st.columns([4, 1])
    with col_ctrl2:
        if st.button("🔄 Rafraîchir", key="ref_ee", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Sous-onglets ────────────────────────────────────────────────────────────
    sub_e, sub_eco = st.tabs(["⚡ Énergie", "📈 Économie"])

    # ── SUB : ÉNERGIE ───────────────────────────────────────────────────────────
    with sub_e:
        st.markdown('<div class="section-header-orange">Indicateurs statiques — prix & production</div>', unsafe_allow_html=True)

        latest = energie[energie["date"] == energie["date"].max()]
        cols = st.columns(len(latest))
        for i, (_, row) in enumerate(latest.iterrows()):
            delta_class  = "metric-delta-up" if row["variation_pct"] >= 0 else "metric-delta-down"
            delta_symbol = "▲" if row["variation_pct"] >= 0 else "▼"
            c = "#ffaa00"
            cols[i].markdown(f"""
            <div class="metric-card" style="border-top:2px solid {c}">
                <div class="metric-label">{row['source']}</div>
                <div class="metric-value">{row['prix_eur_mwh']} €/MWh</div>
                <div class="{delta_class}">{delta_symbol} {abs(row['variation_pct'])}% prod.</div>
                <div class="metric-note">{row['note']}</div>
            </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            for src in energie["source"].unique():
                d = energie[energie["source"] == src]
                fig.add_trace(go.Scatter(
                    x=d["date"], y=d["prix_eur_mwh"], name=src,
                    mode="lines+markers", line=dict(width=2), marker=dict(size=5),
                ))
            fig.update_layout(**PLOTLY_BASE, height=260,
                title=dict(text="Prix €/MWh", font=dict(size=11, color="#4a6a8a")))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.bar(energie, x="date", y="production_twh", color="source", barmode="group")
            fig2.update_layout(**PLOTLY_BASE, height=260,
                title=dict(text="Production TWh", font=dict(size=11, color="#4a6a8a")))
            st.plotly_chart(fig2, use_container_width=True)

        # Flux RSS énergie
        st.markdown('<div class="section-header-orange">📡 Actualités énergie — flux RSS</div>', unsafe_allow_html=True)

        try:
            enr_df = pd.read_csv(energie_rss_path)
            cats   = ["Toutes"] + sorted(enr_df["categorie"].dropna().unique().tolist())
            langs  = ["Toutes"] + sorted(enr_df["langue"].dropna().unique().tolist())
            cf1, cf2 = st.columns(2)
            with cf1:
                filtre_ec = st.selectbox("Catégorie", cats, key="e_cat")
            with cf2:
                filtre_el = st.selectbox("Langue", langs, key="e_lang")
        except Exception:
            filtre_ec = "Toutes"; filtre_el = "Toutes"; enr_df = pd.DataFrame()

        with st.spinner("Chargement flux énergie…"):
            e_articles = fetch_rss(energie_rss_path, max_per_source=4)

        if e_articles.empty:
            st.warning("Aucun article. Vérifiez data/energie_rss.csv")
        else:
            df_e = e_articles.copy()
            if filtre_ec != "Toutes":
                df_e = df_e[df_e["categorie"] == filtre_ec]
            if filtre_el != "Toutes":
                sources_f = enr_df[enr_df["langue"] == filtre_el]["nom"].tolist()
                df_e = df_e[df_e["source"].isin(sources_f)]

            for _, row in df_e.head(30).iterrows():
                url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
                cat_tag  = f'<span class="tag" style="border-color:#ffaa0044; color:#ffaa00">{row["categorie"]}</span>'
                lang_tag = f'<span class="tag">{row["langue"]}</span>'
                st.markdown(f"""
                <div class="signal-card" style="border-color:#ffaa00">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                        <div class="signal-title">{row['titre']}</div>
                        <div style="white-space:nowrap">{cat_tag} {lang_tag}</div>
                    </div>
                    <div class="signal-meta">{row['date']} · {row['source']}</div>
                    <div class="signal-note">{row['resume']}</div>
                    <div style="margin-top:0.4rem">{url_html}</div>
                </div>""", unsafe_allow_html=True)

        with st.expander("Ajouter une source énergie"):
            st.info("Éditez `data/energie_rss.csv` dans GitHub.")
            st.code("NOM,URL_FLUX,CATEGORIE,LANGUE", language="text")

    # ── SUB : ÉCONOMIE ──────────────────────────────────────────────────────────
    with sub_eco:
        st.markdown('<div class="section-header-green">Indicateurs statiques — macro</div>', unsafe_allow_html=True)

        cols = st.columns(len(economie))
        for i, (_, row) in enumerate(economie.iterrows()):
            g = row["croissance_pct"]
            delta_class  = "metric-delta-up" if g >= 0 else "metric-delta-down"
            delta_symbol = "▲" if g >= 0 else "▼"
            cols[i].markdown(f"""
            <div class="metric-card" style="border-top:2px solid #00e5a0">
                <div class="metric-label">{row['pays']}</div>
                <div class="metric-value" style="font-size:1.2rem">{row['pib_milliards_usd']:,} Md$</div>
                <div class="{delta_class}">{delta_symbol} {abs(g)}% croissance</div>
                <div class="metric-note">Inflation {row['inflation_pct']}% · Chômage {row['chomage_pct']}%</div>
            </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Bar(
                x=economie["pays"], y=economie["croissance_pct"],
                marker_color=["#00e5a0" if v >= 0 else "#ff4d6d" for v in economie["croissance_pct"]],
                text=economie["croissance_pct"].apply(lambda x: f"{x:+.1f}%"),
                textposition="outside",
            ))
            fig.update_layout(**PLOTLY_BASE, height=280,
                title=dict(text="Croissance PIB %", font=dict(size=11, color="#4a6a8a")))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=economie["inflation_pct"], y=economie["chomage_pct"],
                mode="markers+text",
                marker=dict(size=14, color="#00e5a0", opacity=0.8),
                text=economie["pays"], textposition="top center",
                textfont=dict(size=10, color="#8aaabb"),
            ))
            fig2.update_layout(**PLOTLY_BASE, height=280,
                title=dict(text="Inflation vs Chômage", font=dict(size=11, color="#4a6a8a")),
                xaxis_title="Inflation %", yaxis_title="Chômage %")
            st.plotly_chart(fig2, use_container_width=True)

        # Flux RSS économie
        st.markdown('<div class="section-header-green">📡 Actualités économie — flux RSS</div>', unsafe_allow_html=True)

        try:
            eco_df = pd.read_csv(economie_rss_path)
            cats_eco  = ["Toutes"] + sorted(eco_df["categorie"].dropna().unique().tolist())
            langs_eco = ["Toutes"] + sorted(eco_df["langue"].dropna().unique().tolist())
            cf1, cf2 = st.columns(2)
            with cf1:
                filtre_ecc = st.selectbox("Catégorie", cats_eco, key="eco_cat")
            with cf2:
                filtre_ecl = st.selectbox("Langue", langs_eco, key="eco_lang")
        except Exception:
            filtre_ecc = "Toutes"; filtre_ecl = "Toutes"; eco_df = pd.DataFrame()

        with st.spinner("Chargement flux économie…"):
            eco_articles = fetch_rss(economie_rss_path, max_per_source=4)

        if eco_articles.empty:
            st.warning("Aucun article. Vérifiez data/economie_rss.csv")
        else:
            df_eco = eco_articles.copy()
            if filtre_ecc != "Toutes":
                df_eco = df_eco[df_eco["categorie"] == filtre_ecc]
            if filtre_ecl != "Toutes":
                sources_f = eco_df[eco_df["langue"] == filtre_ecl]["nom"].tolist()
                df_eco = df_eco[df_eco["source"].isin(sources_f)]

            for _, row in df_eco.head(30).iterrows():
                url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
                cat_tag  = f'<span class="tag" style="border-color:#00e5a044; color:#00e5a0">{row["categorie"]}</span>'
                lang_tag = f'<span class="tag">{row["langue"]}</span>'
                st.markdown(f"""
                <div class="signal-card" style="border-color:#00e5a0">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                        <div class="signal-title">{row['titre']}</div>
                        <div style="white-space:nowrap">{cat_tag} {lang_tag}</div>
                    </div>
                    <div class="signal-meta">{row['date']} · {row['source']}</div>
                    <div class="signal-note">{row['resume']}</div>
                    <div style="margin-top:0.4rem">{url_html}</div>
                </div>""", unsafe_allow_html=True)

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
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div class="section-header">📡 Derniers articles publiés</div>', unsafe_allow_html=True)
    with st.spinner("Chargement des flux…"):
        pers_articles = fetch_rss(pers_rss_path, max_per_source=4)

    if pers_articles.empty:
        st.warning("Aucun article chargé. Vérifiez les URLs dans data/personnes_rss.csv")
    else:
        df_art = pers_articles.copy()
        if filtre_courant != "Tous":
            df_art = df_art[df_art["courant"] == filtre_courant]
        for _, row in df_art.head(20).iterrows():
            c = color_for(row["domaine"])
            url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
            st.markdown(f"""
            <div class="signal-card" style="border-color:{c}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                    <div class="signal-title">{row['titre']}</div>
                    <span class="tag" style="border-color:{c}44; color:{c}; white-space:nowrap">{row['source'].split('(')[0].strip()}</span>
                </div>
                <div class="signal-meta">{row['date']} · {row['courant']}</div>
                <div class="signal-note">{row['resume']}</div>
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
                <div class="person-name">{row['nom']}</div>
                <div class="person-courant">{row['courant']}</div>
                <div class="person-focus">{row['focus']}</div>
                <div class="person-note">{row['note']}</div>
                <div style="margin-top:0.5rem">{url_html}{rss_html}</div>
            </div>""", unsafe_allow_html=True)

    st.info("💡 Éditez `data/personnes.csv` et `data/personnes_rss.csv` dans GitHub pour ajouter des personnes.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SIGNAUX FAIBLES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    try:
        thema_df = pd.read_csv(thema_rss_path)
        dom_opts  = ["Tous"]  + sorted(thema_df["domaine"].dropna().unique().tolist())
        lang_opts = ["Toutes"]+ sorted(thema_df["langue"].dropna().unique().tolist())
    except Exception:
        thema_df = pd.DataFrame(); dom_opts = ["Tous"]; lang_opts = ["Toutes"]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filtre_t_dom = st.selectbox("Domaine", dom_opts, key="sf_dom")
    with col2:
        filtre_lang = st.selectbox("Langue", lang_opts, key="sf_lang")
    with col3:
        if st.button("🔄 Rafraîchir", key="ref_sf", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div class="section-header">📡 Veille thématique — flux automatiques</div>', unsafe_allow_html=True)
    with st.spinner("Chargement des flux thématiques…"):
        thema_articles = fetch_rss(thema_rss_path, max_per_source=3)

    if thema_articles.empty:
        st.warning("Aucun article chargé.")
    else:
        df_t = thema_articles.copy()
        if filtre_t_dom != "Tous":
            df_t = df_t[df_t["domaine"] == filtre_t_dom]
        if filtre_lang != "Toutes" and not thema_df.empty:
            sources_f = thema_df[thema_df["langue"] == filtre_lang]["nom"].tolist()
            df_t = df_t[df_t["source"].isin(sources_f)]

        for _, row in df_t.head(40).iterrows():
            c = color_for(row["domaine"])
            url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire l\'article</a>' if row["url"] else ""
            st.markdown(f"""
            <div class="signal-card" style="border-color:{c}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                    <div class="signal-title">{row['titre']}</div>
                    <span class="tag">{row['source'].split('/')[0].strip()}</span>
                </div>
                <div class="signal-meta">{row['date']} · {row['domaine']}</div>
                <div class="signal-note">{row['resume']}</div>
                <div style="margin-top:0.4rem">{url_html}</div>
            </div>""", unsafe_allow_html=True)

    with st.expander("Ajouter une source thématique"):
        st.info("Éditez `data/thematiques_rss.csv` dans GitHub.")
        st.code("NOM,URL_FLUX,DOMAINE,LANGUE", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SYNTHÈSE IA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    try:
        from google import genai as genai_client
        api_key = st.secrets["GEMINI_API_KEY"]
        api_ok  = True
    except Exception:
        api_ok = False

    if not api_ok:
        st.error("Clé GEMINI_API_KEY introuvable. Va dans Settings → Secrets sur Streamlit Cloud.")
        st.stop()

    st.markdown('<div class="section-header">Synthèse IA — analyse des tendances</div>', unsafe_allow_html=True)

    @st.cache_data(ttl=3600)
    def charger_toutes_sources(pers_p, thema_p, enr_p, eco_p):
        dfs = []
        for p, max_n in [(pers_p, 5), (thema_p, 4), (enr_p, 4), (eco_p, 4)]:
            df = fetch_rss(p, max_per_source=max_n)
            if not df.empty:
                dfs.append(df)
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["titre"]).sort_values("date", ascending=False)

    with st.spinner("Chargement de toutes les sources…"):
        tous_articles = charger_toutes_sources(pers_rss_path, thema_rss_path, energie_rss_path, economie_rss_path)

    nb_articles = len(tous_articles)
    nb_sources  = sum(len(pd.read_csv(p)) for p in [pers_rss_path, thema_rss_path, energie_rss_path, economie_rss_path] if os.path.exists(p))
    st.markdown(f"""
    <div style="background:#0d1520; border:1px solid #1a2a3a; border-radius:4px;
                padding:0.7rem 1rem; margin-bottom:1rem; font-size:0.78rem; color:#4a6a8a;
                font-family:Space Mono,monospace;">
        {nb_articles} articles · {nb_sources} sources
        · Énergie : {len(energie)} entrées · Économie : {len(economie)} pays
    </div>""", unsafe_allow_html=True)

    def ctx_energie():
        latest = energie[energie["date"] == energie["date"].max()]
        return "\n".join(
            f"- {r['source']} : {r['prix_eur_mwh']} €/MWh, production {r['production_twh']} TWh ({r['note']})"
            for _, r in latest.iterrows()
        )

    def ctx_economie():
        return "\n".join(
            f"- {r['pays']} : PIB {r['pib_milliards_usd']} Md$, croissance {r['croissance_pct']}%, inflation {r['inflation_pct']}% ({r['note']})"
            for _, r in economie.iterrows()
        )

    def articles_theme(mots_cles, df, n=12):
        if not mots_cles:
            return df.head(n)
        mask = df["titre"].str.lower().apply(lambda t: any(m in t for m in mots_cles))
        return df[mask].head(n)

    def titres_prompt(df):
        return "\n".join(f"- [{r['date']}] {r['titre']} ({r['source']})" for _, r in df.iterrows())

    def appel_gemini(prompt):
        try:
            client   = genai_client.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Erreur Gemini : {e}"

    THEMES = {
        "⚡ Énergie":   ["énergie", "energy", "solaire", "éolien", "nucléaire", "hydrogène", "batterie", "renouvelable", "électrique", "pétrole", "gaz"],
        "🤖 IA":        ["intelligence artificielle", "artificial intelligence", "machine learning", "llm", "gpt", "mistral", "gemini", "openai", "deepmind", "modèle", "chatgpt"],
        "🚗 Transport": ["transport", "mobilité", "véhicule", "voiture", "aviation", "train", "autonome", "ferroviaire", "fret"],
    }
    THEME_COLORS = {"⚡ Énergie": "#ffaa00", "🤖 IA": "#00e5ff", "🚗 Transport": "#aa88ff"}

    _, col_btn = st.columns([4, 1])
    with col_btn:
        generer = st.button("✨ Générer", use_container_width=True, type="primary")

    if "syntheses" not in st.session_state:
        st.session_state.syntheses = {}

    if generer:
        st.session_state.syntheses = {}
        ce = ctx_energie()
        ceco = ctx_economie()

        with st.spinner("Analyse globale…"):
            prompt_global = f"""Tu es un analyste senior en innovation et prospective technologique.

Contexte économique :
{ceco}

Contexte énergétique :
{ce}

Articles récents issus de sources de veille :
{titres_prompt(tous_articles.head(30))}

En 5 à 7 phrases en français, rédige une synthèse de la situation globale de l'innovation en ce moment.
Identifie les grandes dynamiques, les tensions et les signaux forts à surveiller.
Sois analytique et précis. Ne liste pas les articles — fais une vraie synthèse éditoriale."""
            st.session_state.syntheses["global"] = appel_gemini(prompt_global)

        for theme, mots_cles in THEMES.items():
            with st.spinner(f"Analyse {theme}…"):
                arts    = articles_theme(mots_cles, tous_articles)
                titres  = titres_prompt(arts)
                prompt  = f"""Tu es un expert en {theme.split(' ')[1]}.

Contexte économique : {ceco}
Contexte énergétique : {ce}

Articles récents :
{titres if titres else "Peu d'articles détectés sur ce thème."}

En 4 à 5 phrases en français, synthétise les principales tendances actuelles sur le thème {theme}.
Identifie les ruptures potentielles, les acteurs clés et les signaux à surveiller.
Sois concis et opérationnel."""
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
                <div class="synthese-theme" style="color:#00e5ff">◈ Situation globale</div>
                {st.session_state.syntheses['global']}
            </div>""", unsafe_allow_html=True)

        cols_t = st.columns(3)
        for i, (theme, col) in enumerate(zip(THEMES.keys(), cols_t)):
            if theme not in st.session_state.syntheses:
                continue
            data = st.session_state.syntheses[theme]
            c    = THEME_COLORS.get(theme, "#6688aa")
            with col:
                st.markdown(f"""
                <div class="synthese-card" style="border:1px solid {c}33; border-top:2px solid {c}; min-height:260px">
                    <div class="synthese-theme" style="color:{c}">{theme} · {data['nb']} articles</div>
                    {data['texte']}
                </div>""", unsafe_allow_html=True)
                with st.expander(f"Sources ({data['nb']})"):
                    for _, row in data["articles"].iterrows():
                        url_html = f'<a class="person-link" href="{row.get("url","")}" target="_blank">→ Lire</a>' if row.get("url","") else ""
                        st.markdown(f"""
                        <div class="signal-card" style="border-color:#1a2a3a; padding:0.4rem 0.7rem; margin-bottom:0.3rem">
                            <div class="signal-title" style="font-size:0.78rem">{row['titre']}</div>
                            <div class="signal-meta">{row['date']} · {row['source']}</div>
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
                Résumé global + fiches Énergie · IA · Transport
            </div>
        </div>""", unsafe_allow_html=True)
