# ✈️ Batik Air KPI Dashboard

An interactive Streamlit dashboard for monitoring Batik Air's maintenance and operational KPIs from **January 2025 to March 2026**.

## 📊 KPI Sections

| Section | Metrics |
|---|---|
| **Dispatch Reliability** | DR %, Tech Delay Count, Target vs Actual |
| **DMI** | Close Rate, Avg Open DMI/AC, 1st Extension %, Investigate % |
| **On-Time Performance** | OTP %, Target 85% (data from Jan 2026) |

## 🚀 Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/batik-air-kpi.git
cd batik-air-kpi

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your repository, branch (`main`), and set the **Main file path** to `app.py`
5. Click **"Deploy"**

> No secrets or environment variables are required — all data is embedded in `app.py`.

## 📁 File Structure

```
batik-air-kpi/
├── app.py              # Main Streamlit dashboard
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) — Web app framework
- [Plotly](https://plotly.com/python/) — Interactive charts
- [Pandas](https://pandas.pydata.org/) — Data manipulation

## 📌 Notes

- OTP data is only available from **Jan 2026 onward** (Jan–Dec 2025 pending).
- All KPI data is sourced from `Batik_Air_KPI_Trend_2025_2026.xlsx`.
- The month range slider in the sidebar allows filtering all charts simultaneously.
