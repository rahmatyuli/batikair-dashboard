import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Batik Air KPI Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2e3555;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
    }
    .metric-title { font-size: 0.78rem; color: #8892b0; font-weight: 600;
                    text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 2.0rem; font-weight: 800; margin: 6px 0 4px; }
    .metric-sub   { font-size: 0.75rem; color: #8892b0; }
    .meet  { color: #4ade80; }
    .below { color: #f87171; }
    .section-header {
        font-size: 1.1rem; font-weight: 700; color: #ccd6f6;
        border-left: 4px solid #60a5fa; padding-left: 10px; margin: 1.5rem 0 0.8rem;
    }
    div[data-testid="stMetricValue"] > div { font-size: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
MONTHS = [
    "JAN 25","FEB 25","MAR 25","APR 25","MAY 25","JUN 25",
    "JUL 25","AUG 25","SEP 25","OCT 25","NOV 25","DEC 25",
    "JAN 26","FEB 26","MAR 26",
]

@st.cache_data
def load_data():
    # ── Section 1: Dispatch Reliability ──────────────────────────────────────
    dr = pd.DataFrame({
        "Month": MONTHS,
        "Flight_Cycles":       [7919,6993,6426,8152,7704,7600,8818,8616,7885,8228,8213,8695,8396,6681,7667],
        "Tech_Delay_Count":    [108,85,67,87,59,57,44,49,54,53,51,89,103,69,50],
        "DR_Pct":              [98.64,98.78,98.96,98.93,99.23,99.25,99.50,99.43,99.32,99.36,99.38,98.98,98.77,98.97,99.35],
        "DR_Target":           [99.14,99.14,99.14,99.14,99.14,99.26,99.26,99.26,99.26,99.26,99.26,99.26,99.26,99.26,99.26],
        "Status":              ["BELOW","BELOW","BELOW","BELOW","MEET","BELOW","MEET","MEET","MEET","MEET","MEET","BELOW","BELOW","BELOW","MEET"],
    })

    # ── Section 2: DMI ───────────────────────────────────────────────────────
    dmi = pd.DataFrame({
        "Month": MONTHS,
        "Flight_Cycles":       [7919,6993,6426,8152,7704,7600,8818,8616,7885,8228,8213,8695,8396,6681,7667],
        "Rate_Close_DMI":      [87.86,88.09,88.27,91.38,87.42,84.54,88.09,86.56,90.57,80.32,85.79,93.40,90.08,88.71,86.77],
        "Rate_Close_Target":   [84.7,84.7,84.7,84.7,84.7,72.54,72.54,72.54,72.54,72.54,72.54,72.54,72.54,72.54,81.18],
        "Avg_Open_DMI":        [50,43,40,28,39,49,43,57,38,85,55,27,49,36,50],
        "Avg_Open_DMI_per_AC": [0.769,0.662,0.615,0.431,0.600,0.754,0.683,0.905,0.603,1.349,0.873,0.435,0.790,0.581,0.806],
        "Target_Open_per_AC":  [1.54,1.54,1.54,1.54,1.54,2.20,2.20,2.20,2.20,2.20,2.20,2.20,2.20,2.20,2.27],
        "Investigate_DMI":     [0.73,1.11,0.59,0.31,0.32,0.95,4.99,0.94,5.21,6.02,5.43,0.49,1.42,4.70,4.50],
        "Target_Investigate":  [13.09]*5 + [21.76]*10,
        "DMI_1st_Ext":         [14.08,9.70,14.40,14.46,25.48,24.61,17.17,16.63,13.54,14.01,19.71,16.15,21.62,18.18,19.75],
        "Target_1st_Ext":      [14.78]*5 + [14.95]*10,
    })

    # ── Section 3: OTP ───────────────────────────────────────────────────────
    # ✅ FIX BUG 1: Removed the accidental '+ [72.0, 74.77, 80.78]' duplication.
    # OTP_Pct now has exactly 15 values matching MONTHS (was 18, causing a crash).
    otp = pd.DataFrame({
        "Month": MONTHS,
        "Flight_Cycles":  [7919,6993,6426,8152,7704,7600,8818,8616,7885,8228,8213,8695,8396,6681,7667],
        "OTP_Pct":        [74.83,68.40,82.00,69.47,75.21,71.81,61.76,55.24,71.42,75.97,77.73,73.07,72.00,74.77,80.78],
        "OTP_Target":     [85.0] * 15,
        "Status":         ["BELOW"] * 15,
    })

    return dr, dmi, otp

dr_df, dmi_df, otp_df = load_data()

# ── Colour helpers ────────────────────────────────────────────────────────────
CLR_MEET  = "#4ade80"
CLR_BELOW = "#f87171"
CLR_BLUE  = "#60a5fa"
CLR_AMBER = "#fbbf24"
CLR_GRID  = "rgba(255,255,255,0.07)"

def status_color(s):  return CLR_MEET if s == "MEET" else CLR_BELOW

def bar_colors(series, target_series):
    return [CLR_MEET if v >= t else CLR_BELOW for v, t in zip(series, target_series)]

def plotly_layout(title="", height=340):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#ccd6f6")),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8892b0", size=11),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        margin=dict(l=40, r=20, t=45, b=50),
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(gridcolor=CLR_GRID, zeroline=False),
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # ✅ FIX BUG 2: Changed use_column_width (deprecated) → use_container_width
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Batik_Air_logo.svg/320px-Batik_Air_logo.svg.png",
        use_container_width=True,
    )
    st.markdown("---")
    st.markdown("### 📊 KPI Dashboard")
    section = st.radio(
        "Select Section",
        ["🏠 Overview", "✈️ Dispatch Reliability", "🔧 DMI", "⏱️ On-Time Performance"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    all_months = MONTHS
    sel = st.select_slider("Month Range", options=all_months,
                           value=(all_months[0], all_months[-1]))
    idx_start = all_months.index(sel[0])
    idx_end   = all_months.index(sel[1]) + 1

    dr_f   = dr_df.iloc[idx_start:idx_end].reset_index(drop=True)
    dmi_f  = dmi_df.iloc[idx_start:idx_end].reset_index(drop=True)
    otp_f  = otp_df.iloc[idx_start:idx_end].reset_index(drop=True)

    st.markdown("---")
    st.caption("Data: Jan 2025 – Mar 2026")

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if section == "🏠 Overview":
    st.markdown("## ✈️ Batik Air — KPI Performance Trend  `JAN 2025 – MAR 2026`")

    latest_dr   = dr_df.iloc[-1]
    latest_dmi  = dmi_df.iloc[-1]
    latest_otp  = otp_df.iloc[-1]

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Dispatch Reliability", f"{latest_dr['DR_Pct']:.2f}%",
         f"Target {latest_dr['DR_Target']:.2f}%", latest_dr['Status']),
        (c2, "Tech Delay Count", f"{int(latest_dr['Tech_Delay_Count'])}",
         "Mar 26", "MEET" if latest_dr['Tech_Delay_Count'] < 60 else "BELOW"),
        (c3, "DMI Close Rate", f"{latest_dmi['Rate_Close_DMI']:.2f}%",
         f"Target {latest_dmi['Rate_Close_Target']:.2f}%",
         "MEET" if latest_dmi['Rate_Close_DMI'] >= latest_dmi['Rate_Close_Target'] else "BELOW"),
        (c4, "Avg Open DMI/AC", f"{latest_dmi['Avg_Open_DMI_per_AC']:.3f}",
         f"Target {latest_dmi['Target_Open_per_AC']:.2f}",
         "MEET" if latest_dmi['Avg_Open_DMI_per_AC'] <= latest_dmi['Target_Open_per_AC'] else "BELOW"),
        (c5, "OTP", f"{latest_otp['OTP_Pct']:.1f}%",
         "Target 85.00%", latest_otp['Status']),
    ]
    for col, title, val, sub, stat in cards:
        color_cls = "meet" if stat == "MEET" else "below"
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value {color_cls}">{val}</div>
            <div class="metric-sub">{sub} &nbsp; {'🟢' if stat=='MEET' else '🔴'}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Dispatch Reliability Trend</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dr_f["Month"], y=dr_f["DR_Target"],
                                 name="Target", line=dict(color=CLR_AMBER, dash="dash", width=1.5)))
        fig.add_trace(go.Scatter(x=dr_f["Month"], y=dr_f["DR_Pct"],
                                 name="DR %", line=dict(color=CLR_BLUE, width=2.5),
                                 mode="lines+markers",
                                 marker=dict(color=[status_color(s) for s in dr_f["Status"]], size=7)))
        fig.update_layout(**plotly_layout("", 270))
        fig.update_yaxes(range=[98.4, 99.7])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">DMI Close Rate Trend</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Rate_Close_Target"],
                                  name="Target", line=dict(color=CLR_AMBER, dash="dash", width=1.5)))
        fig2.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Rate_Close_DMI"],
                                  name="Close Rate %", line=dict(color="#a78bfa", width=2.5),
                                  mode="lines+markers",
                                  marker=dict(
                                      color=[CLR_MEET if v >= t else CLR_BELOW
                                             for v,t in zip(dmi_f["Rate_Close_DMI"], dmi_f["Rate_Close_Target"])],
                                      size=7)))
        fig2.update_layout(**plotly_layout("", 270))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Monthly Flight Cycles</div>', unsafe_allow_html=True)
    fig3 = go.Figure(go.Bar(x=dr_f["Month"], y=dr_f["Flight_Cycles"],
                             marker_color=CLR_BLUE, opacity=0.8,
                             text=dr_f["Flight_Cycles"], textposition="outside",
                             textfont=dict(size=9)))
    fig3.update_layout(**plotly_layout("", 260))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-header">Period Summary Table</div>', unsafe_allow_html=True)
    summary = dr_f[["Month","Flight_Cycles","Tech_Delay_Count","DR_Pct","DR_Target","Status"]].copy()
    summary.columns = ["Month","Flt Cycles","Tech Delays","DR (%)","Target (%)","Status"]

    def highlight_status(row):
        color = "#14532d" if row["Status"] == "MEET" else "#450a0a"
        return [f"background-color: {color}; color: white" if col == "Status" else "" for col in row.index]

    st.dataframe(summary.style.apply(highlight_status, axis=1)
                 .format({"DR (%)": "{:.2f}", "Target (%)": "{:.2f}"}),
                 use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – DISPATCH RELIABILITY
# ══════════════════════════════════════════════════════════════════════════════
elif section == "✈️ Dispatch Reliability":
    st.markdown("## ✈️ Aircraft Dispatch Reliability")

    meet_count  = (dr_f["Status"] == "MEET").sum()
    below_count = (dr_f["Status"] == "BELOW").sum()
    avg_dr      = dr_f["DR_Pct"].mean()
    avg_target  = dr_f["DR_Target"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Dispatch Reliability", f"{avg_dr:.2f}%", f"{avg_dr - avg_target:+.2f}% vs target")
    m2.metric("Months Meeting Target", f"{meet_count}/{len(dr_f)}")
    m3.metric("Avg Tech Delay Count", f"{dr_f['Tech_Delay_Count'].mean():.1f}")
    m4.metric("Total Flight Cycles", f"{dr_f['Flight_Cycles'].sum():,}")

    st.markdown('<div class="section-header">Dispatch Reliability vs Target</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dr_f["Month"], y=dr_f["DR_Target"],
                             name="Target", line=dict(color=CLR_AMBER, dash="dash", width=2),
                             mode="lines"))
    fig.add_trace(go.Scatter(x=dr_f["Month"], y=dr_f["DR_Pct"],
                             name="Dispatch Reliability (%)",
                             line=dict(color=CLR_BLUE, width=2.5),
                             mode="lines+markers+text",
                             text=[f"{v:.2f}" for v in dr_f["DR_Pct"]],
                             textposition="top center", textfont=dict(size=9),
                             marker=dict(color=[status_color(s) for s in dr_f["Status"]], size=9)))
    fig.update_layout(**plotly_layout("", 380))
    fig.update_yaxes(range=[98.3, 99.75])
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Technical Delay Count</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=dr_f["Month"], y=dr_f["Tech_Delay_Count"],
            marker_color=[CLR_BELOW if v > 70 else CLR_MEET for v in dr_f["Tech_Delay_Count"]],
            text=dr_f["Tech_Delay_Count"], textposition="outside", textfont=dict(size=9)
        ))
        fig2.update_layout(**plotly_layout("", 310))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">DR vs Target (Delta)</div>', unsafe_allow_html=True)
        delta = dr_f["DR_Pct"] - dr_f["DR_Target"]
        fig3 = go.Figure(go.Bar(
            x=dr_f["Month"], y=delta,
            marker_color=[CLR_MEET if v >= 0 else CLR_BELOW for v in delta],
            text=[f"{v:+.2f}" for v in delta], textposition="outside", textfont=dict(size=9)
        ))
        fig3.add_hline(y=0, line_color="white", line_width=1)
        fig3.update_layout(**plotly_layout("", 310))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-header">Detailed Data</div>', unsafe_allow_html=True)
    display = dr_f.copy()
    display["vs Target"] = (display["DR_Pct"] - display["DR_Target"]).round(2)
    display.columns = ["Month","Flight Cycles","Tech Delays","DR (%)","Target (%)","Status","vs Target"]
    st.dataframe(
        display.style
        .apply(lambda row: [f"background-color: {'#14532d' if row['Status']=='MEET' else '#450a0a'}; color:white"
                            if col == "Status" else "" for col in row.index], axis=1)
        .format({"DR (%)": "{:.2f}", "Target (%)": "{:.2f}", "vs Target": "{:+.2f}"}),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – DMI
# ══════════════════════════════════════════════════════════════════════════════
elif section == "🔧 DMI":
    st.markdown("## 🔧 Deferred Maintenance Item (DMI)")

    avg_close   = dmi_f["Rate_Close_DMI"].mean()
    avg_open_ac = dmi_f["Avg_Open_DMI_per_AC"].mean()
    avg_ext     = dmi_f["DMI_1st_Ext"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg DMI Close Rate",  f"{avg_close:.2f}%")
    m2.metric("Avg Open DMI/AC",     f"{avg_open_ac:.3f}", delta=f"Target {dmi_f['Target_Open_per_AC'].mean():.2f}")
    m3.metric("Avg DMI 1st Ext.",    f"{avg_ext:.2f}%")
    m4.metric("Avg Open DMI Count",  f"{dmi_f['Avg_Open_DMI'].mean():.1f}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">DMI Close Rate vs Target</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Rate_Close_Target"],
                                 name="Target", line=dict(color=CLR_AMBER, dash="dash", width=2)))
        colors = [CLR_MEET if v >= t else CLR_BELOW
                  for v,t in zip(dmi_f["Rate_Close_DMI"], dmi_f["Rate_Close_Target"])]
        fig.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Rate_Close_DMI"],
                                 name="Close Rate %", line=dict(color="#a78bfa", width=2.5),
                                 mode="lines+markers",
                                 marker=dict(color=colors, size=9)))
        fig.update_layout(**plotly_layout("", 300))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Avg Open DMI per Aircraft vs Target</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Target_Open_per_AC"],
                                  name="Target", line=dict(color=CLR_AMBER, dash="dash", width=2)))
        colors2 = [CLR_MEET if v <= t else CLR_BELOW
                   for v,t in zip(dmi_f["Avg_Open_DMI_per_AC"], dmi_f["Target_Open_per_AC"])]
        fig2.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Avg_Open_DMI_per_AC"],
                                  name="Avg Open/AC", line=dict(color="#34d399", width=2.5),
                                  mode="lines+markers",
                                  marker=dict(color=colors2, size=9)))
        fig2.update_layout(**plotly_layout("", 300))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">DMI 1st Extension vs Target</div>', unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=dmi_f["Month"], y=dmi_f["Target_1st_Ext"],
                                  name="Target", line=dict(color=CLR_AMBER, dash="dash", width=2)))
        fig3.add_trace(go.Bar(x=dmi_f["Month"], y=dmi_f["DMI_1st_Ext"],
                              name="1st Ext %",
                              marker_color=[CLR_BELOW if v > t else CLR_MEET
                                            for v,t in zip(dmi_f["DMI_1st_Ext"], dmi_f["Target_1st_Ext"])],
                              opacity=0.75))
        fig3.update_layout(**plotly_layout("", 300))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Average Open DMI Count</div>', unsafe_allow_html=True)
        fig4 = go.Figure(go.Bar(x=dmi_f["Month"], y=dmi_f["Avg_Open_DMI"],
                                 marker_color=CLR_BLUE, opacity=0.8,
                                 text=dmi_f["Avg_Open_DMI"].astype(int),
                                 textposition="outside", textfont=dict(size=9)))
        fig4.update_layout(**plotly_layout("", 300))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">Detailed DMI Data</div>', unsafe_allow_html=True)
    cols_show = ["Month","Rate_Close_DMI","Rate_Close_Target","Avg_Open_DMI",
                 "Avg_Open_DMI_per_AC","Target_Open_per_AC","DMI_1st_Ext","Target_1st_Ext"]
    display = dmi_f[cols_show].copy()
    display.columns = ["Month","Close Rate (%)","Close Target (%)","Avg Open DMI",
                       "Open/AC","Target Open/AC","1st Ext (%)","Target 1st Ext (%)"]
    st.dataframe(display.style.format({c: "{:.2f}" for c in display.columns[1:]}),
                 use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – OTP
# ══════════════════════════════════════════════════════════════════════════════
elif section == "⏱️ On-Time Performance":
    st.markdown("## ⏱️ On-Time Performance (OTP)")

    # ✅ FIX BUG 3 & 4: Removed stale dropna() logic and "data pending" banner.
    # All 15 months now have real OTP data. Metrics are now dynamic (not hardcoded).
    avg_otp    = otp_f["OTP_Pct"].mean()
    latest_otp = otp_f.iloc[-1]
    latest_month = latest_otp["Month"]
    latest_val   = latest_otp["OTP_Pct"]
    latest_delta = latest_val - latest_otp["OTP_Target"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Avg OTP (Selected Range)", f"{avg_otp:.2f}%", f"{avg_otp - 85:.2f}% vs target 85%")
    m2.metric("Months of Data", f"{len(otp_f)}")
    # ✅ BUG 4 fixed: metric now reads from filtered data, not hardcoded
    m3.metric(f"Latest OTP ({latest_month})", f"{latest_val:.2f}%", f"{latest_delta:+.2f}% vs target")

    st.markdown('<div class="section-header">OTP Trend vs Target (85%)</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=otp_f["Month"], y=otp_f["OTP_Target"],
        name="Target (85%)", line=dict(color=CLR_AMBER, dash="dash", width=2)
    ))
    # ✅ FIX BUG 5: Bar colours are now dynamic — green if OTP >= target, red if below
    fig.add_trace(go.Bar(
        x=otp_f["Month"],
        y=otp_f["OTP_Pct"],
        name="OTP (%)",
        marker_color=[CLR_MEET if v >= t else CLR_BELOW
                      for v, t in zip(otp_f["OTP_Pct"], otp_f["OTP_Target"])],
        opacity=0.85,
        text=[f"{v:.2f}%" for v in otp_f["OTP_Pct"]],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(**plotly_layout("", 400))
    fig.update_yaxes(range=[50, 95])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">OTP Data Table</div>', unsafe_allow_html=True)
    disp = otp_f[["Month","Flight_Cycles","OTP_Pct","OTP_Target","Status"]].copy()
    disp.columns = ["Month","Flight Cycles","OTP (%)","Target (%)","Status"]

    def highlight_otp_status(row):
        color = "#14532d" if row["Status"] == "MEET" else "#450a0a"
        return [f"background-color: {color}; color: white" if col == "Status" else "" for col in row.index]

    st.dataframe(
        disp.style
        .apply(highlight_otp_status, axis=1)
        .format({"OTP (%)": "{:.2f}", "Target (%)": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
