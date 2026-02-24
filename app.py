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
    historique = pd.read_csv(os.path.join(base, "data", "projets_historique.csv"))
    personnes = pd.read_csv(os.path.join(base, "data", "personnes.csv"))
    signaux  = pd.read_csv(os.path.join(base, "data", "signaux_faibles.csv"))
    return energie, economie, projets, personnes, signaux

energie, economie, projets, historique, personnes, signaux = load_data()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="radar-header">
    <span class="radar-title">◈ Innovation Radar</span>
    <span class="radar-subtitle">Tableau de bord prospectif — v0.2</span>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_personnes_rss(path):
    import feedparser, datetime
    sources = pd.read_csv(path)
    items = []
    for _, src in sources.iterrows():
        try:
            feed = feedparser.parse(
                src["url_flux"],
                agent="Mozilla/5.0 (compatible; RSSReader/1.0)"
            )
            for entry in feed.entries[:4]:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                date_str = datetime.datetime(*pub[:6]).strftime("%Y-%m-%d") if pub else "—"
                items.append({
                    "date": date_str,
                    "titre": entry.get("title", "Sans titre"),
                    "nom": src["nom"],
                    "courant": src["courant"],
                    "domaine": src["domaine"],
                    "url_profil": src["url_profil"],
                    "url": entry.get("link", ""),
                    "resume": entry.get("summary", "")[:220]
                              .replace("<p>","").replace("</p>","")
                              .replace("<br>","").replace("</br>","").strip() + "…",
                })
        except Exception:
            pass
    df = pd.DataFrame(items)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df


# ── FONCTION RSS THÉMATIQUES ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_thematiques_rss(path):
    import feedparser, datetime
    sources = pd.read_csv(path)
    items = []
    for _, src in sources.iterrows():
        try:
            feed = feedparser.parse(
                src["url_flux"],
                agent="Mozilla/5.0 (compatible; RSSReader/1.0)"
            )
            for entry in feed.entries[:3]:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                date_str = datetime.datetime(*pub[:6]).strftime("%Y-%m-%d") if pub else "—"
                items.append({
                    "date": date_str,
                    "titre": entry.get("title", "Sans titre"),
                    "source": src["nom"],
                    "domaine": src["domaine"],
                    "langue": src["langue"],
                    "url": entry.get("link", ""),
                    "resume": entry.get("summary", "")[:220]
                              .replace("<p>","").replace("</p>","")
                              .replace("<br>","").replace("</br>","").strip() + "…",
                })
        except Exception:
            pass
    df = pd.DataFrame(items)
    if not df.empty:
        df = df.sort_values("date", ascending=False)
    return df

if "session_start" not in st.session_state:
   st.session_state.session_start = pd.Timestamp.now()

nouveautes = projets[pd.to_datetime(projets["date_maj"]) >= pd.Timestamp.now() - pd.Timedelta(days=7)]
if not nouveautes.empty:
    noms = " · ".join(f"<b>{n}</b>" for n in nouveautes["nom"].tolist())
    st.markdown(f"""
    <div style="background:#0d2010; border:1px solid #00e5a044; border-radius:4px;
                padding:0.6rem 1rem; margin-bottom:1rem; font-size:0.78rem; color:#00e5a0;
                font-family:Space Mono,monospace;">
        🟢 Mis à jour cette semaine : {noms}
    </div>""", unsafe_allow_html=True)

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

    MOMENTUM_SYMBOL = {"↑": "▲", "→": "■", "↓": "▼"}
    MOMENTUM_COLOR  = {"↑": "#00e5a0", "→": "#ffaa00", "↓": "#ff4d6d"}
    MOMENTUM_LABEL  = {"↑": "Accélère", "→": "Plateau", "↓": "Décline"}

    # ── Hype curve ─────────────────────────────────────────────────────────────
    x_curve = np.linspace(0, 4, 300)
    def hype(x):
        return (
            2.0 * np.exp(-((x - 1.0)**2) / 0.2)
            - 1.5 * np.exp(-((x - 2.0)**2) / 0.08)
            + 1.2 * (1 - np.exp(-((x - 3.2)**2) / 0.3)) * (x > 2.5)
            + 0.3 * x * (x < 1)
        )
    y_curve = hype(x_curve)
    y_curve = (y_curve - y_curve.min()) / (y_curve.max() - y_curve.min())

    # ── Filtres ─────────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        dom_opts = ["Tous"] + sorted(projets["domaine"].unique().tolist())
        filtre_dom = st.selectbox("Domaine", dom_opts, key="g_dom")
    with col_f2:
        mom_opts = ["Tous", "↑ Accélère", "→ Plateau", "↓ Décline"]
        filtre_mom = st.selectbox("Momentum", mom_opts, key="g_mom")
    with col_f3:
        phases_opts = ["Toutes"] + GARTNER_PHASES
        filtre_phase = st.selectbox("Phase", phases_opts, key="g_phase")

    df_g = projets.copy()
    if filtre_dom != "Tous":
        df_g = df_g[df_g["domaine"] == filtre_dom]
    if filtre_mom != "Tous":
        arrow = filtre_mom[0]
        df_g = df_g[df_g["momentum"] == arrow]
    if filtre_phase != "Toutes":
        df_g = df_g[df_g["phase_gartner"] == filtre_phase]

    # ── Courbe de Gartner interactive ──────────────────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_curve, y=y_curve, mode="lines",
        line=dict(color="#1a3a5a", width=2),
        showlegend=False, hoverinfo="skip",
    ))
    for p, xi in PHASE_X.items():
        fig.add_annotation(
            x=xi, y=-0.14, text=p, showarrow=False,
            font=dict(size=8, color="#4a6a8a", family="Space Mono"), xanchor="center",
        )

    for _, row in df_g.iterrows():
        xi   = PHASE_X.get(row["phase_gartner"], 0)
        np.random.seed(hash(row["nom"]) % (2**31))
        x_p  = np.clip(xi + np.random.uniform(-0.15, 0.15), 0, 4)
        idx  = np.argmin(np.abs(x_curve - xi))
        y_p  = np.clip(y_curve[idx] + np.random.uniform(-0.03, 0.03), 0.02, 0.98)

        c    = color_for(row["domaine"])
        m    = row.get("momentum", "→")
        mc   = MOMENTUM_COLOR.get(m, "#ffaa00")
        size = 8 + row["trl"] * 1.8

        fig.add_trace(go.Scatter(
            x=[x_p], y=[y_p],
            mode="markers+text",
            marker=dict(
                size=size, color=c, opacity=0.85,
                line=dict(color=mc, width=2.5),
                symbol="circle",
            ),
            text=[f"{MOMENTUM_SYMBOL.get(m,'■')} {row['nom']}"],
            textposition="top center",
            textfont=dict(size=7.5, color="#c8d8e8"),
            name=row["nom"],
            hovertemplate=(
                f"<b>{row['nom']}</b><br>"
                f"Domaine : {row['domaine']}<br>"
                f"TRL : {row['trl']}<br>"
                f"Phase : {row['phase_gartner']}<br>"
                f"Momentum : {MOMENTUM_LABEL.get(m, m)}<br>"
                f"Potentiel : {row['potentiel']}<br>"
                f"Maj : {row['date_maj']}<br>"
                f"<extra></extra>"
            ),
        ))

    fig.update_layout(
        paper_bgcolor="#080c14", plot_bgcolor="#080c14",
        font=dict(family="DM Sans", color="#8aaabb"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=480,
        title=dict(
            text="Courbe de Gartner  ·  taille = TRL  ·  bordure = momentum  ·  cliquer pour détail",
            font=dict(size=10, color="#4a6a8a")
        ),
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.4, 4.4]),
        yaxis=dict(visible=False, range=[-0.28, 1.12]),
    )

    # Légende momentum
    for i, (arrow, label) in enumerate(MOMENTUM_LABEL.items()):
        fig.add_annotation(
            x=4.38,
            y=1.08 - i * 0.07,
            text=f"{MOMENTUM_SYMBOL[arrow]}  {label}",
            showarrow=False,
            font=dict(size=9, color=MOMENTUM_COLOR[arrow], family="Space Mono"),
            xanchor="right",
        )

    # Clic sur un projet → fiche détail
    selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="gartner_chart")

    # ── Fiche détail (si clic) ─────────────────────────────────────────────────
    projet_selectionne = None
    if selected and selected.get("selection") and selected["selection"].get("points"):
        point = selected["selection"]["points"][0]
        curve_index = point.get("curve_number", 0)
        if curve_index > 0:  # index 0 = la courbe elle-même
            projet_selectionne = df_g.iloc[curve_index - 1] if curve_index - 1 < len(df_g) else None

    if projet_selectionne is not None:
        row = projet_selectionne
        c   = color_for(row["domaine"])
        m   = row.get("momentum", "→")
        mc  = MOMENTUM_COLOR.get(m, "#ffaa00")
        url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lien externe</a>' if pd.notna(row.get("url","")) and row.get("url","") else ""
        st.markdown(f"""
        <div style="background:#0d1a28; border:1px solid {c}55; border-left: 3px solid {c};
                    border-radius:4px; padding:1.2rem 1.4rem; margin: 0.5rem 0 1rem 0;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start">
                <div>
                    <span style="font-family:Space Mono; font-size:1rem; color:#e8f4ff; font-weight:700">{row['nom']}</span>
                    &nbsp;<span class="tag" style="border-color:{c}44; color:{c}">{row['domaine']}</span>
                    &nbsp;<span class="tag">TRL {row['trl']}</span>
                </div>
                <span style="font-family:Space Mono; font-size:0.9rem; color:{mc}">
                    {MOMENTUM_SYMBOL.get(m,'■')} {MOMENTUM_LABEL.get(m,m)}
                </span>
            </div>
            <div style="font-size:0.72rem; color:#4a6a8a; margin: 0.3rem 0;">{row['phase_gartner']} · Mis à jour : {row['date_maj']}</div>
            <div style="font-size:0.85rem; color:#c8d8e8; margin: 0.6rem 0; line-height:1.5">{row['description']}</div>
            <div style="font-size:0.72rem; color:#4a6a8a;">Acteurs clés : {row['acteurs_cles']}</div>
            <div style="margin-top:0.6rem; font-family:Space Mono; font-size:1rem; color:{c}">{row['potentiel']}</div>
            <div style="margin-top:0.4rem">{url_html}</div>
        </div>""", unsafe_allow_html=True)

        # TRL tracker pour ce projet
        hist = historique[historique["nom"] == row["nom"]]
        if not hist.empty:
            st.markdown('<div class="section-header">📈 Évolution TRL</div>', unsafe_allow_html=True)
            fig_trl = go.Figure()
            fig_trl.add_trace(go.Scatter(
                x=hist["date"], y=hist["trl"],
                mode="lines+markers+text",
                line=dict(color=c, width=2),
                marker=dict(size=8, color=c),
                text=hist["note"],
                textposition="top center",
                textfont=dict(size=8, color="#8aaabb"),
                hovertemplate="<b>TRL %{y}</b><br>%{text}<extra></extra>",
            ))
            fig_trl.update_layout(
                paper_bgcolor="#080c14", plot_bgcolor="#080c14",
                font=dict(family="DM Sans", color="#8aaabb"),
                margin=dict(l=10, r=10, t=20, b=10),
                height=200,
                xaxis=dict(gridcolor="#1a2a3a"),
                yaxis=dict(gridcolor="#1a2a3a", range=[0, 10], dtick=1, title="TRL"),
                showlegend=False,
            )
            st.plotly_chart(fig_trl, use_container_width=True)

    # ── Liste des projets ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Tous les projets</div>', unsafe_allow_html=True)

    df_g_sorted = df_g.sort_values("trl", ascending=False)
    for _, row in df_g_sorted.iterrows():
        c  = color_for(row["domaine"])
        m  = row.get("momentum", "→")
        mc = MOMENTUM_COLOR.get(m, "#ffaa00")
        url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lien</a>' if pd.notna(row.get("url","")) and row.get("url","") else ""
        st.markdown(f"""
        <div class="signal-card" style="border-color: {c}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <span style="font-family:Space Mono; font-size:0.88rem; color:#e8f4ff; font-weight:700">{row['nom']}</span>
                    &nbsp;<span class="tag" style="border-color:{c}44; color:{c}">{row['domaine']}</span>
                    &nbsp;<span class="tag">TRL {row['trl']}</span>
                </div>
                <div style="display:flex; gap:0.8rem; align-items:center">
                    <span style="font-family:Space Mono; font-size:0.8rem; color:{mc}">{MOMENTUM_SYMBOL.get(m,'■')} {MOMENTUM_LABEL.get(m,m)}</span>
                    <span style="font-family:Space Mono; font-size:0.75rem; color:{c}">{row['potentiel']}</span>
                </div>
            </div>
            <div style="font-size:0.72rem; color:#4a6a8a; margin:0.2rem 0;">{row['phase_gartner']} · Maj : {row['date_maj']}</div>
            <div class="signal-note">{row['description']}</div>
            <div style="font-size:0.68rem; color:#344a5a; margin-top:0.3rem;">Acteurs : {row['acteurs_cles']}</div>
            {url_html}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Ajouter / modifier un projet</div>', unsafe_allow_html=True)
    st.info("💡 Éditez `data/projets.csv` dans GitHub. Momentum : ↑ accélère · → plateau · ↓ décline")
    with st.expander("Modèle de ligne — projets.csv"):
        st.code("NOM,DOMAINE,TRL,PHASE_GARTNER,POTENTIEL,DESCRIPTION,ACTEURS_CLES,DATE_MAJ,URL,MOMENTUM", language="text")
    with st.expander("Modèle de ligne — projets_historique.csv"):
        st.code("NOM,DATE,TRL,NOTE", language="text")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PERSONNES RÉFÉRENTES  (remplace tout le bloc "with tabs[3]:" existant)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    base = os.path.dirname(os.path.abspath(__file__))
    pers_rss_path = os.path.join(base, "data", "personnes_rss.csv")
    pers_rss_df   = pd.read_csv(pers_rss_path)

    # ── Filtres ────────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        courants = ["Tous"] + sorted(pers_rss_df["courant"].unique().tolist())
        filtre_courant = st.selectbox("Filtrer par courant de pensée", courants)
    with col_f2:
        if st.button("🔄 Rafraîchir", key="refresh_pers", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Derniers articles RSS ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📡 Derniers articles publiés</div>', unsafe_allow_html=True)

    with st.spinner("Chargement des flux…"):
        pers_articles = fetch_personnes_rss(pers_rss_path)

    if pers_articles.empty:
        st.warning("Aucun article chargé. Vérifiez les URLs dans data/personnes_rss.csv")
    else:
        df_articles = pers_articles.copy()
        if filtre_courant != "Tous":
            df_articles = df_articles[df_articles["courant"] == filtre_courant]

        for _, row in df_articles.head(20).iterrows():
            c = color_for(row["domaine"])
            url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire</a>' if row["url"] else ""
            st.markdown(f"""
            <div class="signal-card" style="border-color: {c}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                    <div class="signal-title">{row['titre']}</div>
                    <span class="tag" style="white-space:nowrap; border-color:{c}44; color:{c}">{row['nom'].split('(')[0].strip()}</span>
                </div>
                <div class="signal-meta">{row['date']} · {row['courant']}</div>
                <div class="signal-note">{row['resume']}</div>
                <div style="margin-top:0.4rem">{url_html}</div>
            </div>""", unsafe_allow_html=True)
  
    # ── Profils ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Profils suivis</div>', unsafe_allow_html=True)

    df_p = personnes if filtre_courant == "Tous" else personnes[personnes["courant"] == filtre_courant]
    cols = st.columns(2)
    for i, (_, row) in enumerate(df_p.iterrows()):
        with cols[i % 2]:
            url_html  = f'<a class="person-link" href="{row["url_profil"]}" target="_blank">→ Profil</a>' if pd.notna(row.get("url_profil","")) and row.get("url_profil","") else ""
            rss_html  = f'&nbsp;&nbsp;<a class="person-link" href="{row["url_flux"]}" target="_blank">RSS</a>'  if pd.notna(row.get("url_flux",""))  and row.get("url_flux","")  else ""
            st.markdown(f"""
            <div class="person-card">
                <div class="person-name">{row['nom']}</div>
                <div class="person-courant">{row['courant']}</div>
                <div class="person-focus">{row['focus']}</div>
                <div class="person-note">{row['note']}</div>
                <div style="margin-top:0.5rem">{url_html}{rss_html}</div>
            </div>""", unsafe_allow_html=True)

    # ── Ajouter une personne ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">Ajouter une personne</div>', unsafe_allow_html=True)
    st.info("💡 Éditez `data/personnes.csv` (profil) et `data/personnes_rss.csv` (flux RSS) dans GitHub.")
    with st.expander("Modèle de ligne — personnes_rss.csv"):
        st.code("NOM,URL_FLUX,DOMAINE,COURANT,URL_PROFIL", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SIGNAUX FAIBLES  (remplace tout le bloc "with tabs[4]:" existant)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    base = os.path.dirname(os.path.abspath(__file__))
    thema_path = os.path.join(base, "data", "thematiques_rss.csv")
    thema_df   = pd.read_csv(thema_path)

    # ── Filtres ────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        dom_opts = ["Tous"] + sorted(thema_df["domaine"].unique().tolist())
        filtre_t_dom = st.selectbox("Domaine", dom_opts, key="sf_dom")
    with col2:
        lang_opts = ["Toutes"] + sorted(thema_df["langue"].unique().tolist())
        filtre_lang = st.selectbox("Langue", lang_opts, key="sf_lang")
    with col3:
        if st.button("🔄 Rafraîchir", key="refresh_sf", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Flux thématiques live ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📡 Veille thématique — flux automatiques</div>', unsafe_allow_html=True)

    with st.spinner("Chargement des flux thématiques…"):
        thema_articles = fetch_thematiques_rss(thema_path)

    if thema_articles.empty:
        st.warning("Aucun article chargé.")
    else:
        df_t = thema_articles.copy()
        if filtre_t_dom != "Tous":
            df_t = df_t[df_t["domaine"] == filtre_t_dom]
        if filtre_lang != "Toutes":
            df_t = df_t[df_t["langue"] == filtre_lang]

        for _, row in df_t.head(40).iterrows():
            c = color_for(row["domaine"])
            url_html = f'<a class="person-link" href="{row["url"]}" target="_blank">→ Lire l\'article</a>' if row["url"] else ""
            lang_badge = f'<span class="tag">{row["langue"]}</span>'
            st.markdown(f"""
            <div class="signal-card" style="border-color: {c}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                    <div class="signal-title">{row['titre']}</div>
                    {lang_badge}
                </div>
                <div class="signal-meta">{row['date']} · {row['source']} · {row['domaine']}</div>
                <div class="signal-note">{row['resume']}</div>
                <div style="margin-top:0.4rem">{url_html}</div>
            </div>""", unsafe_allow_html=True)
    with st.expander("Ajouter une source thématique RSS"):
        st.info("Éditez `data/thematiques_rss.csv` dans GitHub.")
        st.code("NOM,URL_FLUX,DOMAINE,LANGUE", language="text")


