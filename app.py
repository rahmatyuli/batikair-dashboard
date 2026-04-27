import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Batik Air Fleet Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #F5F7FA; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        border-left: 4px solid #D32F2F;
    }
    [data-testid="stMetricLabel"] { font-size: 0.78rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1a1a2e; }
    [data-testid="stMetricDelta"] { font-size: 0.85rem; }

    /* Section headers */
    .section-header {
        font-size: 1rem;
        font-weight: 700;
        color: #444;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #e0e0e0;
    }

    /* Divider */
    hr { border: none; border-top: 1px solid #e8e8e8; margin: 1rem 0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: white; border-right: 1px solid #eee; }

    /* Plotly charts */
    .stPlotlyChart > div { border-radius: 14px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:0.5rem;">
    <div style="background:#D32F2F; border-radius:12px; padding:10px 14px; font-size:1.6rem;">✈️</div>
    <div>
        <div style="font-size:1.45rem; font-weight:800; color:#1a1a2e; line-height:1.2;">Batik Air — Fleet & Maintenance</div>
        <div style="font-size:0.85rem; color:#888;">Aircraft Fleet Management Dashboard</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ─── File Upload ──────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📂 Upload your fleet data (CSV or Excel)",
    type=["csv", "xlsx", "xls"],
    help="Upload a file containing aircraft fleet and maintenance records.",
)

if uploaded_file is None:
    st.info("👆 Upload a CSV or Excel file to get started.")
    with st.expander("📋 Expected Column Format (click to expand)"):
        st.markdown("Your file can contain **any combination** of these columns — the dashboard auto-detects them:")
        expected = pd.DataFrame({
            "Column Name": [
                "Aircraft ID", "Registration", "Aircraft Type",
                "Status", "Age (Years)", "Total Flight Hours", "Cycles",
                "Last Maintenance Date", "Next Maintenance Date", "Maintenance Type",
                "Maintenance Interval (Days)", "Base Airport",
            ],
            "Description": [
                "Unique aircraft identifier", "ICAO/IATA tail number", "e.g. Boeing 737-900ER",
                "Active / In Maintenance / AOG / Grounded", "Aircraft age in years", "Cumulative flight hours", "Number of flight cycles",
                "Date of last maintenance event", "Scheduled next maintenance date", "e.g. A-Check, C-Check, D-Check",
                "Days between scheduled checks", "Home base / hub",
            ],
        })
        st.dataframe(expected, use_container_width=True, hide_index=True)
    st.stop()

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

df = load_data(uploaded_file)

# Auto-detect date columns and parse
for col in df.columns:
    if any(k in col.lower() for k in ["date", "scheduled", "last", "next"]):
        try:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
        except Exception:
            pass

# Auto-detect key columns by name patterns
def detect_col(df, *keywords):
    for kw in keywords:
        for col in df.columns:
            if kw.lower() in col.lower():
                return col
    return None

col_id       = detect_col(df, "aircraft id", "tail", "registration", "id")
col_type     = detect_col(df, "aircraft type", "type", "model")
col_status   = detect_col(df, "status")
col_age      = detect_col(df, "age")
col_hours    = detect_col(df, "flight hour", "hours", "fh")
col_cycles   = detect_col(df, "cycle")
col_last     = detect_col(df, "last maintenance", "last check", "last maint")
col_next     = detect_col(df, "next maintenance", "next check", "next maint")
col_mtype    = detect_col(df, "maintenance type", "check type", "maint type")
col_base     = detect_col(df, "base", "airport", "hub", "station")

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")

    filtered_df = df.copy()

    if col_status:
        unique_statuses = sorted(df[col_status].dropna().unique().tolist())
        sel_status = st.multiselect("Aircraft Status", unique_statuses, default=unique_statuses)
        filtered_df = filtered_df[filtered_df[col_status].isin(sel_status)]

    if col_type:
        unique_types = sorted(df[col_type].dropna().unique().tolist())
        sel_type = st.multiselect("Aircraft Type", unique_types, default=unique_types)
        filtered_df = filtered_df[filtered_df[col_type].isin(sel_type)]

    if col_base:
        unique_bases = sorted(df[col_base].dropna().unique().tolist())
        sel_base = st.multiselect("Base Airport", unique_bases, default=unique_bases)
        filtered_df = filtered_df[filtered_df[col_base].isin(sel_base)]

    if col_age:
        try:
            min_age = float(df[col_age].min())
            max_age = float(df[col_age].max())
            if min_age < max_age:
                age_range = st.slider("Aircraft Age (Years)", min_age, max_age, (min_age, max_age))
                filtered_df = filtered_df[
                    (filtered_df[col_age] >= age_range[0]) &
                    (filtered_df[col_age] <= age_range[1])
                ]
        except Exception:
            pass

    st.divider()
    st.markdown(f"**{len(filtered_df)}** of **{len(df)}** aircraft shown")
    st.caption(f"Last updated: {datetime.today().strftime('%d %b %Y')}")

# ─── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Fleet Overview</div>', unsafe_allow_html=True)

total = len(filtered_df)
if col_status:
    active    = filtered_df[col_status].str.lower().str.contains("active|operational", na=False).sum()
    in_maint  = filtered_df[col_status].str.lower().str.contains("maintenance|mro|check", na=False).sum()
    aog       = filtered_df[col_status].str.lower().str.contains("aog|grounded|unserviceable", na=False).sum()
    avail_pct = round(active / total * 100, 1) if total > 0 else 0.0
else:
    active = in_maint = aog = 0
    avail_pct = 0.0

avg_age   = round(filtered_df[col_age].mean(), 1)   if col_age   else "—"
avg_hours = int(filtered_df[col_hours].mean())       if col_hours else "—"

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Aircraft",    total)
k2.metric("Active Fleet",      active)
k3.metric("In Maintenance",    in_maint)
k4.metric("AOG / Grounded",    aog)
k5.metric("Availability",      f"{avail_pct}%")
k6.metric("Avg Age (yrs)",     avg_age)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Row 1: Status & Type ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗂️ Fleet Composition</div>', unsafe_allow_html=True)
r1c1, r1c2 = st.columns(2)

BATIK_COLORS = ["#D32F2F", "#1565C0", "#2E7D32", "#F57C00", "#6A1B9A", "#00838F"]

with r1c1:
    if col_status:
        counts = filtered_df[col_status].value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        fig = px.pie(
            counts, names="Status", values="Count",
            title="Fleet Status Distribution",
            hole=0.48,
            color_discrete_sequence=BATIK_COLORS,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=False,
            font=dict(family="Inter, sans-serif", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No 'Status' column detected.")

with r1c2:
    if col_type:
        counts = filtered_df[col_type].value_counts().reset_index()
        counts.columns = ["Type", "Count"]
        fig2 = px.bar(
            counts, x="Count", y="Type",
            title="Aircraft by Type",
            orientation="h",
            color="Count",
            color_continuous_scale=[[0, "#FFCDD2"], [1, "#B71C1C"]],
            text="Count",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(t=50, b=20, l=20, r=20),
            coloraxis_showscale=False,
            font=dict(family="Inter, sans-serif", size=12),
            xaxis_title=None, yaxis_title=None,
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No 'Aircraft Type' column detected.")

# ─── Row 2: Age & Hours ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Fleet Metrics</div>', unsafe_allow_html=True)
r2c1, r2c2 = st.columns(2)

with r2c1:
    if col_age:
        fig3 = px.histogram(
            filtered_df, x=col_age,
            nbins=12,
            title="Aircraft Age Distribution (Years)",
            color_discrete_sequence=["#1565C0"],
            labels={col_age: "Age (Years)"},
        )
        fig3.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(t=50, b=20, l=20, r=20),
            bargap=0.08,
            font=dict(family="Inter, sans-serif", size=12),
            xaxis_title="Age (Years)", yaxis_title="Aircraft Count",
        )
        fig3.add_vline(
            x=filtered_df[col_age].mean(), line_dash="dash",
            line_color="#D32F2F",
            annotation_text=f"Avg {filtered_df[col_age].mean():.1f}y",
            annotation_position="top right",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No 'Age' column detected.")

with r2c2:
    if col_hours and col_id:
        hrs = filtered_df[[col_id, col_hours]].dropna().sort_values(col_hours, ascending=False).head(15)
        fig4 = px.bar(
            hrs, x=col_id, y=col_hours,
            title="Top 15 Aircraft by Flight Hours",
            color=col_hours,
            color_continuous_scale=[[0, "#E8F5E9"], [1, "#1B5E20"]],
            text=col_hours,
        )
        fig4.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig4.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(t=50, b=20, l=20, r=20),
            coloraxis_showscale=False,
            font=dict(family="Inter, sans-serif", size=12),
            xaxis_title=None, yaxis_title="Flight Hours",
        )
        st.plotly_chart(fig4, use_container_width=True)
    elif col_hours:
        fig4 = px.histogram(filtered_df, x=col_hours, title="Flight Hours Distribution",
                            color_discrete_sequence=["#2E7D32"], nbins=12)
        fig4.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("No 'Flight Hours' column detected.")

# ─── Row 3: Maintenance Types & Timeline ──────────────────────────────────────
st.markdown('<div class="section-header">🔧 Maintenance Insights</div>', unsafe_allow_html=True)
r3c1, r3c2 = st.columns(2)

with r3c1:
    if col_mtype:
        mtype_counts = filtered_df[col_mtype].value_counts().reset_index()
        mtype_counts.columns = ["Maintenance Type", "Count"]
        fig5 = px.bar(
            mtype_counts, x="Maintenance Type", y="Count",
            title="Maintenance Events by Type",
            color="Maintenance Type",
            color_discrete_sequence=BATIK_COLORS,
            text="Count",
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=False,
            font=dict(family="Inter, sans-serif", size=12),
            xaxis_title=None, yaxis_title="Count",
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("No 'Maintenance Type' column detected.")

with r3c2:
    if col_next and pd.api.types.is_datetime64_any_dtype(filtered_df[col_next]):
        today = pd.Timestamp.today().normalize()
        future = filtered_df[filtered_df[col_next] >= today].copy()
        future["Days Until"] = (future[col_next] - today).dt.days
        future["Urgency"] = pd.cut(
            future["Days Until"],
            bins=[-1, 14, 30, 90, float("inf")],
            labels=["Overdue/Critical", "Within 2 Weeks", "Within 30 Days", "Planned"],
        )
        urg_counts = future["Urgency"].value_counts().reset_index()
        urg_counts.columns = ["Urgency", "Count"]
        urg_colors = {
            "Overdue/Critical": "#D32F2F",
            "Within 2 Weeks":   "#F57C00",
            "Within 30 Days":   "#FBC02D",
            "Planned":          "#388E3C",
        }
        fig6 = px.bar(
            urg_counts, x="Urgency", y="Count",
            title="Upcoming Maintenance Urgency",
            color="Urgency",
            color_discrete_map=urg_colors,
            text="Count",
        )
        fig6.update_traces(textposition="outside")
        fig6.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=False,
            font=dict(family="Inter, sans-serif", size=12),
            xaxis_title=None, yaxis_title="Aircraft Count",
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("No valid 'Next Maintenance Date' column detected.")

# ─── Maintenance Schedule Table ───────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Upcoming Maintenance Schedule</div>', unsafe_allow_html=True)

if col_next and pd.api.types.is_datetime64_any_dtype(filtered_df[col_next]):
    today = pd.Timestamp.today().normalize()
    upcoming = filtered_df[filtered_df[col_next] >= today].copy()
    upcoming["Days Until Next Check"] = (upcoming[col_next] - today).dt.days
    upcoming = upcoming.sort_values("Days Until Next Check")

    # Format date columns for display
    display_cols = [c for c in [col_id, col_type, col_status, col_mtype, col_last, col_next, "Days Until Next Check"] if c and c in upcoming.columns]
    display_df = upcoming[display_cols].copy()
    for dc in [col_last, col_next]:
        if dc and dc in display_df.columns:
            display_df[dc] = display_df[dc].dt.strftime("%d %b %Y")

    def highlight_urgency(row):
        days = row.get("Days Until Next Check", 999)
        if isinstance(days, (int, float)):
            if days <= 14:
                return ["background-color: #FFEBEE"] * len(row)
            elif days <= 30:
                return ["background-color: #FFF8E1"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display_df.style.apply(highlight_urgency, axis=1),
        use_container_width=True,
        hide_index=True,
        height=320,
    )
else:
    st.markdown("#### Full Fleet Data")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=300)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
col_dl, col_info = st.columns([1, 3])
with col_dl:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Data (CSV)",
        data=csv,
        file_name="batikair_fleet_export.csv",
        mime="text/csv",
    )
with col_info:
    st.caption(f"Batik Air Fleet Dashboard • {len(filtered_df)} records • Generated {datetime.today().strftime('%d %B %Y')}")
