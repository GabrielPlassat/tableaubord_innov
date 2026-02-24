import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import feedparser
import datetime

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Innovation Radar",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset & base */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    background-color: #080c14;
    color: #c8d8e8;
    font-family: 'DM Sans', sans-serif;
}
.stApp { background-color: #080c14; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }

/* Header */
.radar-header {
    display: flex; align-items: baseline; gap: 1rem;
    border-bottom: 1px solid #1a2a3a;
    padding-bottom: 0.8rem; margin-bottom: 1.5rem;
}
.radar-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem; font-weight: 700;
    color: #00e5ff; letter-spacing: 0.08em;
    text-transform: uppercase;
}
.radar-subtitle {
    font-size: 0.75rem; color: #4a6a8a;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.12em;
}

/* Metric cards */
.metric-card {
    background: #0d1520;
    border: 1px solid #1a2a3a;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #00e5ff44; }
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem; color: #4a6a8a;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem; font-weight: 700; color: #e8f4ff;
    line-height: 1;
}
.metric-delta-up { color: #00e5a0; font-size: 0.8rem; font-family: 'Space Mono', monospace; }
.metric-delta-down { color: #ff4d6d; font-size: 0.8rem; font-family: 'Space Mono', monospace; }
.metric-note { font-size: 0.72rem; color: #4a6a8a; margin-top: 0.4rem; }

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem; color: #00e5ff;
    text-transform: uppercase; letter-spacing: 0.2em;
    border-left: 2px solid #00e5ff;
    padding-left: 0.6rem; margin: 1.5rem 0 1rem 0;
}

/* Tags */
.tag {
    display: inline-block;
    background: #0d2030; border: 1px solid #1a3a5a;
    border-radius: 2px; padding: 1px 7px;
    font-size: 0.65rem; color: #6aadcc;
    font-family: 'Space Mono', monospace;
    margin: 1px 2px;
}
.tag-domaine-tech { border-color: #00e5ff44; color: #00e5ff; }
.tag-domaine-energie { border-color: #ffaa0044; color: #ffaa00; }
.tag-domaine-agri { border-color: #00e5a044; color: #00e5a0; }
.tag-domaine-mat { border-color: #aa88ff44; color: #aa88ff; }
.tag-domaine-gouv { border-color: #ff8844; color: #ff8844; }
.tag-domaine-climat { border-color: #44aaff44; color: #44aaff; }

/* Person card */
.person-card {
    background: #0d1520; border: 1px solid #1a2a3a;
    border-radius: 4px; padding: 1rem;
    margin-bottom: 0.8rem; position: relative;
}
.person-name {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem; font-weight: 700; color: #e8f4ff;
}
.person-courant {
    font-size: 0.72rem; color: #00e5ff;
    margin: 0.15rem 0 0.5rem 0;
}
.person-focus { font-size: 0.78rem; color: #8aaabb; line-height: 1.4; }
.person-note { font-size: 0.72rem; color: #4a7a8a; margin-top: 0.4rem; font-style: italic; }
.person-link {
    display: inline-block; margin-top: 0.5rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; color: #00e5ff;
    text-decoration: none; border-bottom: 1px solid #00e5ff44;
}

/* Signal card */
.signal-card {
    background: #0d1520; border-left: 3px solid;
    padding: 0.8rem 1rem; margin-bottom: 0.7rem;
    border-radius: 0 4px 4px 0;
}
.signal-title { font-size: 0.88rem; color: #e8f4ff; font-weight: 500; }
.signal-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; color: #4a6a8a; margin-top: 0.3rem;
}
.signal-note { font-size: 0.75rem; color: #7a9aaa; margin-top: 0.35rem; }

/* Plotly override */
.js-plotly-plot .plotly .modebar { background: transparent !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #0d1520;
    padding: 4px;
    border-radius: 4px;
    border: 1px solid #1a2a3a;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem; color: #4a6a8a;
    text-transform: uppercase; letter-spacing: 0.08em;
    background: transparent; border-radius: 2px;
    padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background: #1a2a3a !important; color: #00e5ff !important;
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#080c14", plot_bgcolor="#080c14",
    font=dict(family="DM Sans", color="#8aaabb"),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#1a2a3a", zerolinecolor="#1a2a3a"),
    yaxis=dict(gridcolor="#1a2a3a", zerolinecolor="#1a2a3a"),
)

DOMAINE_COLORS = {
    "Énergie": "#ffaa00", "Tech": "#00e5ff", "Tech/IA": "#00e5ff",
    "Agri": "#00e5a0", "Agri/Food": "#00e5a0", "Matériaux": "#aa88ff",
    "Gouvernance": "#ff8844", "Climat": "#44aaff", "Aviation": "#ff6688",
    "Construction": "#aabb66",
}

def color_for(domaine):
    for k, v in DOMAINE_COLORS.items():
        if k.lower() in domaine.lower():
            return v
    return "#6688aa"

def stars(s):
    count = s.count("★") if isinstance(s, str) else int(s)
    return "★" * count + "☆" * (5 - count)

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    energie  = pd.read_csv(os.path.join(base, "data", "energie.csv"))
    economie = pd.read_csv(os.path.join(base, "data", "economie.csv"))
    projets  = pd.read_csv(os.path.join(base, "data", "projets.csv"))
    personnes = pd.read_csv(os.path.join(base, "data", "personnes.csv"))
    signaux  = pd.read_csv(os.path.join(base, "data", "signaux_faibles.csv"))
    return energie, economie, projets, personnes, signaux

energie, economie, projets, personnes, signaux = load_data()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="radar-header">
    <span class="radar-title">◈ Innovation Radar</span>
    <span class="radar-subtitle">Tableau de bord prospectif — v0.2</span>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["⚡ Énergie", "📈 Économie", "🔬 Projets & TRL", "👤 Veille Personnes", "📡 Signaux Faibles"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ÉNERGIE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-header">Prix & production par source</div>', unsafe_allow_html=True)

    # Last period metrics
    latest = energie[energie["date"] == energie["date"].max()]
    cols = st.columns(len(latest))
    for i, (_, row) in enumerate(latest.iterrows()):
        delta_class = "metric-delta-up" if row["variation_pct"] >= 0 else "metric-delta-down"
        delta_symbol = "▲" if row["variation_pct"] >= 0 else "▼"
        c = color_for(row["source"])
        cols[i].markdown(f"""
        <div class="metric-card" style="border-top: 2px solid {c}">
            <div class="metric-label">{row['source']}</div>
            <div class="metric-value">{row['prix_eur_mwh']} €/MWh</div>
            <div class="{delta_class}">{delta_symbol} {abs(row['variation_pct'])}% prod.</div>
            <div class="metric-note">{row['note']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Évolution des prix</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for src in energie["source"].unique():
            d = energie[energie["source"] == src]
            fig.add_trace(go.Scatter(
                x=d["date"], y=d["prix_eur_mwh"], name=src,
                mode="lines+markers",
                line=dict(color=color_for(src), width=2),
                marker=dict(size=5),
            ))
        fig.update_layout(**PLOTLY_LAYOUT, title=dict(text="Prix €/MWh", font=dict(size=11, color="#4a6a8a")), height=280)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(
            energie, x="date", y="production_twh", color="source",
            color_discrete_map={s: color_for(s) for s in energie["source"].unique()},
            barmode="group",
        )
        fig2.update_layout(**PLOTLY_LAYOUT, title=dict(text="Production TWh", font=dict(size=11, color="#4a6a8a")), height=280)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Données brutes — éditable dans data/energie.csv</div>', unsafe_allow_html=True)
    st.dataframe(energie, use_container_width=True, hide_index=True,
                 column_config={"prix_eur_mwh": "Prix (€/MWh)", "production_twh": "Prod. (TWh)", "variation_pct": "Var. %"})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ÉCONOMIE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">Indicateurs macroéconomiques — T1 2024</div>', unsafe_allow_html=True)

    cols = st.columns(len(economie))
    for i, (_, row) in enumerate(economie.iterrows()):
        g = row["croissance_pct"]
        delta_class = "metric-delta-up" if g >= 0 else "metric-delta-down"
        delta_symbol = "▲" if g >= 0 else "▼"
        cols[i].markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{row['pays']}</div>
            <div class="metric-value" style="font-size:1.2rem">{row['pib_milliards_usd']:,} Md$</div>
            <div class="{delta_class}">{delta_symbol} {abs(g)}% croissance</div>
            <div class="metric-note">Inflation {row['inflation_pct']}% · Chômage {row['chomage_pct']}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=economie["pays"], y=economie["croissance_pct"],
            marker_color=["#00e5a0" if v >= 0 else "#ff4d6d" for v in economie["croissance_pct"]],
            text=economie["croissance_pct"].apply(lambda x: f"{x:+.1f}%"),
            textposition="outside",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title=dict(text="Croissance PIB %", font=dict(size=11, color="#4a6a8a")), height=300)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=economie["inflation_pct"], y=economie["chomage_pct"],
            mode="markers+text",
            marker=dict(size=14, color="#00e5ff", opacity=0.8),
            text=economie["pays"], textposition="top center",
            textfont=dict(size=10, color="#8aaabb"),
        ))
        fig2.update_layout(**PLOTLY_LAYOUT,
            title=dict(text="Inflation vs Chômage", font=dict(size=11, color="#4a6a8a")),
            xaxis_title="Inflation %", yaxis_title="Chômage %", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Notes contextuelles</div>', unsafe_allow_html=True)
    for _, row in economie.iterrows():
        st.markdown(f"""<div class="signal-card" style="border-color: #1a3a5a">
            <div class="signal-title">{row['pays']} — {row['trimestre']}</div>
            <div class="signal-note">{row['note']}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PROJETS & COURBE DE GARTNER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    GARTNER_PHASES = [
        "Innovation Trigger",
        "Peak of Inflated Expectations",
        "Trough of Disillusionment",
        "Slope of Enlightenment",
        "Plateau of Productivity",
    ]
    PHASE_X = {p: i for i, p in enumerate(GARTNER_PHASES)}

    # Hype curve path
    x_curve = np.linspace(0, 4, 300)
    def hype(x):
        return (
            2.0 * np.exp(-((x - 1.0)**2) / 0.2)
            - 1.5 * np.exp(-((x - 2.0)**2) / 0.08)
            + 1.2 * (1 - np.exp(-((x - 3.2)**2) / 0.3)) * (x > 2.5)
            + 0.3 * x * (x < 1)
        )
    y_curve = hype(x_curve)
    # Normalize
    y_curve = (y_curve - y_curve.min()) / (y_curve.max() - y_curve.min())

    fig = go.Figure()
    # Curve
    fig.add_trace(go.Scatter(
        x=x_curve, y=y_curve,
        mode="lines", line=dict(color="#1a3a5a", width=2), showlegend=False,
        hoverinfo="skip",
    ))
    # Phase labels
    for p, xi in PHASE_X.items():
        fig.add_annotation(
            x=xi, y=-0.12,
            text=p, showarrow=False,
            font=dict(size=8.5, color="#4a6a8a", family="Space Mono"),
            xanchor="center",
        )

    # Project dots
    jitter = {"Innovation Trigger": 0, "Peak of Inflated Expectations": 0,
               "Trough of Disillusionment": 0, "Slope of Enlightenment": 0,
               "Plateau of Productivity": 0}

    for _, row in projets.iterrows():
        phase = row["phase_gartner"]
        xi = PHASE_X.get(phase, 0)
        x_proj = xi + np.random.uniform(-0.18, 0.18)
        x_proj = max(0, min(4, x_proj))
        # Find y on curve
        idx = np.argmin(np.abs(x_curve - xi))
        y_proj = y_curve[idx] + np.random.uniform(-0.04, 0.04)
        y_proj = max(0.02, min(0.98, y_proj))

        c = color_for(row["domaine"])
        trl_size = 8 + row["trl"] * 1.8

        fig.add_trace(go.Scatter(
            x=[x_proj], y=[y_proj],
            mode="markers+text",
            marker=dict(size=trl_size, color=c, opacity=0.85,
                        line=dict(color="#080c14", width=1.5)),
            text=[row["nom"]],
            textposition="top center",
            textfont=dict(size=8, color="#c8d8e8"),
            name=row["nom"],
            hovertemplate=(
                f"<b>{row['nom']}</b><br>"
                f"Domaine: {row['domaine']}<br>"
                f"TRL: {row['trl']}<br>"
                f"Phase: {row['phase_gartner']}<br>"
                f"Potentiel: {row['potentiel']}<br>"
                f"<extra></extra>"
            ),
        ))

    gartner_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}
    fig.update_layout(
        **gartner_layout,
        height=460,
        title=dict(text="Courbe de Gartner — positionnement des projets (taille = TRL)",
                   font=dict(size=11, color="#4a6a8a")),
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.4, 4.4], gridcolor="#1a2a3a"),
        yaxis=dict(visible=False, range=[-0.25, 1.1], gridcolor="#1a2a3a"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Filter
    st.markdown('<div class="section-header">Détail des projets</div>', unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        domaines = ["Tous"] + sorted(projets["domaine"].unique().tolist())
        filtre_dom = st.selectbox("Domaine", domaines, label_visibility="collapsed")
    with col_f2:
        phases = ["Toutes les phases"] + GARTNER_PHASES
        filtre_phase = st.selectbox("Phase Gartner", phases, label_visibility="collapsed")

    df_f = projets.copy()
    if filtre_dom != "Tous":
        df_f = df_f[df_f["domaine"] == filtre_dom]
    if filtre_phase != "Toutes les phases":
        df_f = df_f[df_f["phase_gartner"] == filtre_phase]

    df_f = df_f.sort_values("trl", ascending=False)

    for _, row in df_f.iterrows():
        c = color_for(row["domaine"])
        url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lien</a>' if pd.notna(row["url"]) and row["url"] else ""
        st.markdown(f"""
        <div class="signal-card" style="border-color: {c}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <span style="font-family:Space Mono; font-size:0.88rem; color:#e8f4ff; font-weight:700">{row['nom']}</span>
                    &nbsp;<span class="tag" style="border-color:{c}44; color:{c}">{row['domaine']}</span>
                    &nbsp;<span class="tag">TRL {row['trl']}</span>
                </div>
                <div style="font-family:Space Mono; font-size:0.75rem; color:{c}">{row['potentiel']}</div>
            </div>
            <div style="font-size:0.72rem; color:#4a6a8a; margin:0.2rem 0;">{row['phase_gartner']}</div>
            <div class="signal-note">{row['description']}</div>
            <div style="font-size:0.68rem; color:#344a5a; margin-top:0.3rem;">Acteurs : {row['acteurs_cles']}</div>
            {url_html}
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PERSONNES RÉFÉRENTES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">Personnes suivies</div>', unsafe_allow_html=True)

    courants = ["Tous"] + sorted(personnes["courant"].unique().tolist())
    filtre_courant = st.selectbox("Filtrer par courant de pensée", courants, label_visibility="visible")
    df_p = personnes if filtre_courant == "Tous" else personnes[personnes["courant"] == filtre_courant]

    cols = st.columns(2)
    for i, (_, row) in enumerate(df_p.iterrows()):
        with cols[i % 2]:
            url_html = f'<a class="person-link" href="{row["url_profil"]}" target="_blank">→ Profil</a>' if pd.notna(row["url_profil"]) else ""
            rss_html = f'&nbsp;&nbsp;<a class="person-link" href="{row["url_flux"]}" target="_blank">RSS</a>' if pd.notna(row["url_flux"]) and row["url_flux"] else ""
            dernier = f'<span style="font-family:Space Mono;font-size:0.6rem;color:#4a6a8a">Dernier signal : {row["derniere_publication"]}</span>' if pd.notna(row.get("derniere_publication", None)) and row.get("derniere_publication", None) else ""
            st.markdown(f"""
            <div class="person-card">
                <div class="person-name">{row['nom']}</div>
                <div class="person-courant">{row['courant']}</div>
                <div class="person-focus">{row['focus']}</div>
                <div class="person-note">{row['note']}</div>
                <div style="margin-top:0.5rem; display:flex; align-items:center; gap: 1rem;">
                    {url_html}{rss_html}&nbsp;&nbsp;{dernier}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Ajouter une personne</div>', unsafe_allow_html=True)
    st.info("💡 Pour ajouter une personne référente, éditez directement le fichier `data/personnes.csv` dans GitHub.", icon=None)
    with st.expander("Voir le modèle de ligne CSV à copier-coller"):
        st.code("NOM,COURANT,PLATEFORME,URL_PROFIL,URL_FLUX,FOCUS,DATE_MAJ,NOTE", language="text")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SIGNAUX FAIBLES
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)  # rafraîchit toutes les heures
def fetch_rss_feeds(sources_path):
    import feedparser, datetime, os
    sources = pd.read_csv(sources_path)
    items = []
    for _, src in sources.iterrows():
        try:
            feed = feedparser.parse(src["url_flux"])
            for entry in feed.entries[:5]:  # 5 articles max par source
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                date_str = datetime.datetime(*pub[:6]).strftime("%Y-%m-%d") if pub else "—"
                items.append({
                    "date": date_str,
                    "titre": entry.get("title", "Sans titre"),
                    "source": src["nom"],
                    "domaine": src["domaine"],
                    "url": entry.get("link", ""),
                    "resume": entry.get("summary", "")[:200].replace("<p>","").replace("</p>","").strip() + "…",
                    "type": src["type"],
                    "origine": "🔴 Live RSS",
                })
        except Exception:
            pass  # si un flux échoue, on continue sans bloquer
    df = pd.DataFrame(items)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df

with tabs[4]:
    st.markdown('<div class="section-header">Signaux faibles — flux automatiques</div>', unsafe_allow_html=True)

    base = os.path.dirname(os.path.abspath(__file__))
    sources_path = os.path.join(base, "data", "sources_rss.csv")
    sources_df = pd.read_csv(sources_path)

    # ── Contrôles ─────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        dom_opts = ["Tous"] + sorted(sources_df["domaine"].unique().tolist())
        filtre_s_dom = st.selectbox("Domaine", dom_opts, key="sf_dom", label_visibility="collapsed")
    with col2:
        type_opts = ["Tous"] + sorted(sources_df["type"].unique().tolist())
        filtre_type = st.selectbox("Type de source", type_opts, key="sf_type", label_visibility="collapsed")
    with col3:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Section RSS Live ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📡 Articles récents — RSS live</div>', unsafe_allow_html=True)

    with st.spinner("Chargement des flux RSS…"):
        rss_df = fetch_rss_feeds(sources_path)

    if rss_df.empty:
        st.warning("Aucun flux RSS chargé. Vérifiez votre connexion ou les URLs dans sources_rss.csv")
    else:
        df_rss_f = rss_df.copy()
        if filtre_s_dom != "Tous":
            df_rss_f = df_rss_f[df_rss_f["domaine"] == filtre_s_dom]
        if filtre_type != "Tous":
            df_rss_f = df_rss_f[df_rss_f["type"] == filtre_type]

        for _, row in df_rss_f.head(30).iterrows():
            c = color_for(row["domaine"])
            url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire l\'article</a>' if row["url"] else ""
            st.markdown(f"""
            <div class="signal-card" style="border-color: {c}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div class="signal-title">{row['titre']}</div>
                    <span class="tag" style="white-space:nowrap; margin-left:8px">{row['origine']}</span>
                </div>
                <div class="signal-meta">{row['date']} · {row['source']} · {row['domaine']}</div>
                <div class="signal-note">{row['resume']}</div>
                <div style="margin-top:0.4rem">{url_html}</div>
            </div>""", unsafe_allow_html=True)

    # ── Section manuelle (CSV) ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Signaux curatés manuellement</div>', unsafe_allow_html=True)

    trl_min, trl_max = st.slider("Filtrer par TRL estimé", 1, 9, (1, 9))
    df_s = signaux.copy()
    if filtre_s_dom != "Tous":
        df_s = df_s[df_s["domaine"] == filtre_s_dom]
    df_s = df_s[(df_s["trl_estime"] >= trl_min) & (df_s["trl_estime"] <= trl_max)]
    df_s = df_s.sort_values("date", ascending=False)

    for _, row in df_s.iterrows():
        c = color_for(row["domaine"])
        tags_html = "".join([f'<span class="tag">{t.strip()}</span>' for t in str(row["tags"]).split(",")])
        url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Source</a>' if pd.notna(row["url"]) else ""
        st.markdown(f"""
        <div class="signal-card" style="border-color: {c}">
            <div style="display:flex; justify-content:space-between">
                <div class="signal-title">{row['titre']}</div>
                <div style="font-family:Space Mono; font-size:0.75rem; color:{c}">{row['intensite']}</div>
            </div>
            <div class="signal-meta">{row['date']} · {row['domaine']} · TRL ~{row['trl_estime']} · {row['source']}</div>
            <div class="signal-note">{row['note']}</div>
            <div style="margin-top:0.5rem">{tags_html} &nbsp; {url_html}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Ajouter un signal manuel</div>', unsafe_allow_html=True)
    st.info("💡 Éditez `data/signaux_faibles.csv` dans GitHub pour ajouter un nouveau signal.", icon=None)
    with st.expander("Voir le modèle de ligne CSV"):
        st.code("DATE,TITRE,DOMAINE,TRL_ESTIME,INTENSITE,SOURCE,URL,TAGS,NOTE", language="text")

