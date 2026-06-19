import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import base64
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cloverkey Revenue Forecast",
    page_icon="🍀",
    layout="wide",
)

# ── Asset loading ──────────────────────────────────────────────────────────────
DESIGN_DIR = r"\\kgs-fs04\Users\houstonp\Desktop\design_handoff_revenue_forecast"

@st.cache_data
def load_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    SHAMROCK_B64 = load_b64(os.path.join(DESIGN_DIR, "assets", "shamrock-green.png"))
    CHART_B64    = load_b64(os.path.join(DESIGN_DIR, "model_comparison.png"))
    HAS_ASSETS   = True
except Exception:
    SHAMROCK_B64 = ""
    CHART_B64    = ""
    HAS_ASSETS   = False

# ── Design system CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
:root{
  --forest:#06524B; --pine:#03332E; --apple:#408A47; --light-apple:#C0E3B8;
  --cream:#FAF7F1;  --paper:#F6F3EC; --ink:#1A1F1D;  --ink-muted:#4A5552;
  --ink-subtle:#7A8582; --line:#E3E0D6;
}
html,body,[class*="css"],.stApp{
  font-family:'Outfit',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  color:var(--ink);
}
.stApp{ background:var(--cream); }
.block-container{ padding-top:0.6rem; max-width:98%; padding-left:2rem; padding-right:2rem; }
header[data-testid="stHeader"]{ background:transparent; }
[data-testid="stSidebar"]{ display:none !important; }
h1,h2,h3{ color:var(--forest); letter-spacing:-0.02em; font-weight:800; }

/* Hide sidebar collapse arrow */
[data-testid="stSidebarCollapsedControl"]{ display:none !important; }
[data-testid="stSidebarCollapseButton"]{ display:none !important; }
button[kind="header"]{ display:none !important; }

/* Sidebar shell */
[data-testid="stSidebar"]{
  display:block !important;
  background:var(--forest) !important;
  min-width:220px !important; max-width:220px !important;
}
[data-testid="stSidebar"] > div:first-child{ padding-top:0; border-right:none; }
section[data-testid="stSidebar"] .block-container{ padding:0; max-width:none; }

/* Sidebar nav buttons */
section[data-testid="stSidebar"] .stButton > button{
  background:transparent !important; color:#ffffff !important;
  border:none !important; border-left:3px solid transparent !important;
  border-radius:8px !important;
  padding:11px 13px !important; font-weight:500 !important; font-size:14px !important;
  text-align:left !important; box-shadow:none !important;
  justify-content:flex-start !important; width:100% !important;
  transition:background 100ms, color 100ms !important; letter-spacing:-0.01em !important;
}
section[data-testid="stSidebar"] .stButton > button:hover{
  background:rgba(255,255,255,0.1) !important; color:#fff !important;
}
section[data-testid="stSidebar"] .stButton > button:active{
  background:rgba(255,255,255,0.15) !important; transform:none !important;
}

/* Inputs */
.stTextInput input,.stNumberInput input{
  border:1.5px solid #B8B4A8 !important; border-radius:8px !important;
  background:#fff !important; padding:13px 16px !important;
  font-size:17px !important; font-family:'Outfit',sans-serif !important;
  color:var(--ink) !important; caret-color:#06524B !important;
}
.stTextInput input:focus,.stNumberInput input:focus{
  border-color:var(--forest) !important;
  box-shadow:0 0 0 3px rgba(6,82,75,0.14) !important;
  background:#fff !important;
}
.stTextInput label,.stNumberInput label,
[data-testid="stWidgetLabel"] label,.stSelectbox label{
  font-size:12px !important; font-weight:700 !important;
  text-transform:uppercase; letter-spacing:0.1em;
  color:var(--ink-muted) !important;
}


/* Primary button (main content area) */
.stButton > button{
  background:var(--forest); color:#fff; border:none; border-radius:8px;
  padding:12px 26px; font-weight:700; font-size:15px;
  font-family:'Outfit',sans-serif; letter-spacing:-0.01em;
  box-shadow:0 2px 8px rgba(6,82,75,0.22);
  transition:background 120ms,transform 120ms;
}
.stButton > button:hover{ background:var(--pine); color:#fff; }
.stButton > button:active{ background:var(--pine); transform:scale(0.98); }


/* Input card container */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:#fff !important; border:1px solid #E3E0D6 !important;
  border-radius:14px !important; box-shadow:0 1px 2px rgba(6,82,75,0.06) !important;
  padding:8px 14px !important;
}

/* Hide number input steppers */
[data-testid="stNumberInput"] button{ display:none !important; }

/* Field labels — muted grey-green */
.stTextInput label,.stNumberInput label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label{
  color:#4A5552 !important;
}

/* Checkbox */
[data-testid="stCheckbox"] {
  display: flex !important;
  align-items: center !important;
  padding-top: 28px !important;
}
[data-testid="stCheckbox"] label {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  color: var(--ink) !important;
}
/* Visible square — unchecked */
[data-testid="stCheckbox"] label[data-baseweb="checkbox"] > span:first-child {
  background: #ffffff !important;
  border: 2px solid #888 !important;
  border-radius: 3px !important;
  width: 20px !important;
  height: 20px !important;
  box-shadow: none !important;
}
/* Visible square — checked */
[data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input[aria-checked="true"]) > span:first-child {
  background: #2D7D6E !important;
  border-color: #2D7D6E !important;
}
/* Checkmark icon */
[data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input[aria-checked="true"]) > span:first-child svg {
  fill: #ffffff !important;
}
/* Focus ring */
[data-testid="stCheckbox"] label[data-baseweb="checkbox"]:focus-within > span:first-child {
  outline: 2px solid #2D7D6E !important;
  outline-offset: 2px !important;
}

/* Tabular numbers */
[data-testid="stMetricValue"],.ck-num{ font-variant-numeric:tabular-nums; }

/* Alerts */
.stSuccess{
  background:#E6EFEC; border-left:4px solid #06524B;
  color:#03332E; border-radius:6px;
}
</style>
""", unsafe_allow_html=True)

# ── Load model artifact ────────────────────────────────────────────────────────
ARTIFACT_PATH = r"C:\Users\houstonp\Downloads\cloverkey_forecast_v2.joblib"

@st.cache_resource
def load_artifact():
    return joblib.load(ARTIFACT_PATH)

artifact      = load_artifact()
model         = artifact["model"]
scaler        = artifact["scaler"]
residuals     = artifact["residual_quantiles"]
comp_table    = artifact["comp_table"]
coefficients  = artifact["coefficients"]
intercept     = artifact["intercept"]
training_mape = artifact["training_mape"]
n_stores      = artifact["n_training_stores"]

LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prediction_ledger.csv")

# ── Helpers ────────────────────────────────────────────────────────────────────

def predict(adc, size, pd_flag):
    log_adic    = np.log(adc)
    log_size    = np.log(size)
    adic_x_size = log_adic * log_size
    raw    = np.array([[log_adic, log_size, pd_flag, adic_x_size]])
    scaled = scaler.transform(raw)
    log_pred = model.predict(scaled)[0]
    return (
        np.exp(log_pred),
        np.exp(log_pred + residuals["p25"]),
        np.exp(log_pred + residuals["p75"]),
        log_pred, log_adic, log_size, scaled[0],
    )


def driver_decomposition(adc, size, pd_flag, point, scaled_row):
    """
    Proportional log-space decomposition: each term's share of log(point)
    maps to a dollar contribution. All contributions sum to point.
    """
    betas = [
        coefficients["log_adic"],
        coefficients["log_size"],
        coefficients["payroll_deduction_encoded"],
        coefficients["adic_x_size"],
    ]
    log_parts = [b * x for b, x in zip(betas, scaled_row)]
    total_log = intercept + sum(log_parts)

    def dollar(lp):
        return (lp / total_log) * point if total_log != 0 else 0

    base_d  = dollar(intercept)
    adc_d   = dollar(log_parts[0])
    size_d  = dollar(log_parts[1])
    pd_d    = dollar(log_parts[2])
    ix_d    = dollar(log_parts[3])

    pd_note = (
        f"+{pd_d/point*100:.0f}% staff spending uplift"
        if pd_flag and pd_d > 0
        else "Not available — no uplift applied"
    )
    pd_bar  = "#C0E3B8" if pd_flag else "#E3E0D6"
    pd_txt  = "#06524B" if pd_flag else "#7A8582"

    return [
        ("Base revenue",        "Any staffed hospital gift shop",            base_d, "#9FB5AE", "#1A1F1D"),
        ("Daily census (ADC)",  f"{int(adc):,} average daily patients",      adc_d,  "#06524B", "#06524B"),
        ("Shop size",           f"{int(size):,} sq ft of retail space",      size_d, "#06524B", "#06524B"),
        ("ADC × size synergy",  "Larger hospitals amplify larger shops",      ix_d,   "#06524B", "#06524B"),
        ("Payroll deduction",   pd_note,                                     pd_d,   pd_bar,    pd_txt),
    ]


def get_comps(log_adic_in, log_size_in, pd_flag, top_n=3):
    pool = [s for s in comp_table if s["payroll_deduction_encoded"] == pd_flag] or comp_table
    ranked = sorted(
        pool,
        key=lambda s: (s["log_adic"] - log_adic_in) ** 2 + (s["log_size"] - log_size_in) ** 2,
    )
    return ranked[:top_n]


def fmt(v):
    return f"${v:,.0f}"


def save_forecast(row):
    print(f"[SAVE] Attempting to save: {row}", flush=True)
    print(f"[SAVE] Ledger path: {LEDGER_PATH}", flush=True)
    print(f"[SAVE] Ledger exists before save: {os.path.exists(LEDGER_PATH)}", flush=True)
    df = pd.DataFrame([row])
    try:
        if os.path.exists(LEDGER_PATH):
            df.to_csv(LEDGER_PATH, mode="a", header=False, index=False)
        else:
            df.to_csv(LEDGER_PATH, index=False)
        print(f"[SAVE] Success. Rows now in ledger: {len(pd.read_csv(LEDGER_PATH))}", flush=True)
    except Exception as e:
        print(f"[SAVE] ERROR: {e}", flush=True)


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    shamrock_img_sb = (
        f'<img src="data:image/png;base64,{SHAMROCK_B64}" style="height:40px;width:auto;filter:brightness(0) invert(1);" />'
        if HAS_ASSETS else "🍀"
    )
    st.markdown(f"""
<div style="padding:28px 20px 20px;">
  <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:6px;">
    {shamrock_img_sb}
    <span style="font-size:30px;font-weight:800;color:#fff;letter-spacing:-0.03em;
                 font-family:'Outfit',sans-serif;">Cloverkey</span>
  </div>
  <div style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.2em;
              color:#C0E3B8;margin-bottom:20px;font-family:'Outfit',sans-serif;text-align:left;">
    Revenue Intelligence
  </div>
  <div style="border-top:1px solid rgba(255,255,255,0.12);padding-top:18px;">
  </div>
</div>
""", unsafe_allow_html=True)

    pages = ["Revenue Forecast", "About This Model", "Saved Forecasts"]
    if "page" not in st.session_state:
        st.session_state.page = "Revenue Forecast"

    icons = {"Revenue Forecast": "▸", "About This Model": "▸", "Saved Forecasts": "▸"}
    active_idx = pages.index(st.session_state.page) + 1
    st.markdown(f"""
<style>
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]
  > div:nth-child({active_idx}) button {{
  background:rgba(255,255,255,0.12) !important;
  color:#fff !important;
  font-weight:700 !important;
  border-left:3px solid #C0E3B8 !important;
}}
</style>""", unsafe_allow_html=True)
    for p in pages:
        is_active = st.session_state.page == p
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            if not is_active:
                st.session_state.page = p
                st.rerun()

    st.markdown(f"""
<div style="margin:24px 12px 0;padding:16px 0 0;border-top:1px solid rgba(255,255,255,0.12);">
  <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;
              color:#ffffff;font-family:'Outfit',sans-serif;margin-bottom:8px;">Model</div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;">
    <span style="font-size:11px;font-weight:600;color:#ffffff;
                 background:rgba(255,255,255,0.08);border-radius:6px;padding:3px 9px;
                 font-family:'Outfit',sans-serif;">V2 &middot; {n_stores} stores</span>
    <span style="font-size:11px;font-weight:700;color:#ffffff;
                 background:rgba(192,227,184,0.12);border-radius:6px;padding:3px 9px;
                 font-family:'Outfit',sans-serif;">MAPE {training_mape}%</span>
  </div>
</div>
""", unsafe_allow_html=True)

page = st.session_state.page

# ════════════════════════════════════════════════════════════════════════════════
# PAGE — Revenue Forecast
# ════════════════════════════════════════════════════════════════════════════════
if page == "Revenue Forecast":
    with st.container(border=True):
        st.markdown(
            '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">'
            '<span style="font-size:18px;font-weight:700;color:#1A1F1D;letter-spacing:-0.01em;">Prospect inputs</span>'
            '<span style="font-size:12px;color:#7A8582;">Enter three facts about the prospect</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        hosp_name  = st.text_input("Hospital name", placeholder="e.g. Memorial Regional Medical Center")
        c1, c2, c3 = st.columns(3)
        adc_input  = c1.number_input("Average daily census", min_value=1, max_value=2000, value=240, step=1)
        size_input = c2.number_input("Gift shop square footage", min_value=50, max_value=10000, value=900, step=10)
        pd_toggle  = c3.checkbox("Payroll deduction available?", value=False)

    pd_select  = "Yes" if pd_toggle else "No"
    submitted  = st.button("Generate Forecast", use_container_width=True)

    # ── Results ────────────────────────────────────────────────────────────────
    if submitted:
        pd_flag = 1 if pd_select == "Yes" else 0
        point, low, high, log_pred, log_adic_in, log_size_in, scaled_row = predict(
            adc_input, size_input, pd_flag
        )
        drivers = driver_decomposition(adc_input, size_input, pd_flag, point, scaled_row)
        comps   = get_comps(log_adic_in, log_size_in, pd_flag)
        display_name = hosp_name.strip() or "This Hospital"
        st.session_state["last_forecast"] = {
            "display_name": display_name,
            "adc_input":    adc_input,
            "size_input":   size_input,
            "pd_select":    pd_select,
            "point":        point,
            "low":          low,
            "high":         high,
            "comps":        comps,
            "drivers":      drivers,
        }

    if "last_forecast" in st.session_state:
        lf = st.session_state["last_forecast"]
        point        = lf["point"]
        low          = lf["low"]
        high         = lf["high"]
        comps        = lf["comps"]
        drivers      = lf["drivers"]
        display_name = lf["display_name"]
        adc_input    = lf["adc_input"]
        size_input   = lf["size_input"]
        pd_select    = lf["pd_select"]

        display_name = hosp_name.strip() or "This Hospital"
        meta_str = (
            f"{display_name} &middot; {int(adc_input):,} ADC &middot; "
            f"{int(size_input):,} sq ft &middot; Payroll deduction: {pd_select}"
        )
        rng = high - low
        pct = round(max(0, min(100, (point - low) / rng * 100))) if rng > 0 else 50

        # ── Hero card ──────────────────────────────────────────────────────────
        st.markdown(f"""
<div style="position:relative;overflow:hidden;border-radius:16px;padding:38px 44px 34px;
            margin:8px 0 24px;
            background:linear-gradient(150deg,#06524B 0%,#063f3a 58%,#03332E 100%);
            box-shadow:0 18px 40px rgba(6,82,75,0.28),0 4px 10px rgba(6,82,75,0.12);">

  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div style="font-size:11.5px;font-weight:700;text-transform:uppercase;
                letter-spacing:0.2em;color:#C0E3B8;">Projected Annual Revenue</div>
    <div style="font-size:11px;font-weight:700;letter-spacing:0.14em;color:#9FD493;
                border:1px solid rgba(192,227,184,0.4);border-radius:999px;padding:5px 12px;">
      MATURE &middot; T12
    </div>
  </div>

  <div style="text-align:center;margin:18px 0 6px;">
    <div style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.22em;
                color:#C0E3B8;margin-bottom:8px;">Most Likely</div>
    <div style="font-size:92px;line-height:1;font-weight:800;color:#fff;
                letter-spacing:-0.03em;font-variant-numeric:tabular-nums;">{fmt(point)}</div>
    <div style="font-size:15px;color:rgba(255,255,255,0.62);margin-top:14px;">{meta_str}</div>
  </div>

  <div style="margin-top:26px;">
    <div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:12px;">
      <div>
        <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.16em;color:#9FD493;">Conservative</div>
        <div style="font-size:32px;font-weight:700;color:#fff;letter-spacing:-0.02em;
                    font-variant-numeric:tabular-nums;margin-top:4px;">{fmt(low)}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:2px;">P25 estimate</div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.16em;color:#9FD493;">Optimistic</div>
        <div style="font-size:32px;font-weight:700;color:#fff;letter-spacing:-0.02em;
                    font-variant-numeric:tabular-nums;margin-top:4px;">{fmt(high)}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:2px;">P75 estimate</div>
      </div>
    </div>
    <div style="position:relative;height:8px;border-radius:999px;background:rgba(255,255,255,0.14);">
      <div style="position:absolute;left:0;top:0;bottom:0;border-radius:999px;
                  background:linear-gradient(90deg,rgba(192,227,184,0.55),#C0E3B8);
                  width:{pct}%;"></div>
      <div style="position:absolute;top:50%;left:{pct}%;transform:translate(-50%,-50%);
                  width:18px;height:18px;border-radius:50%;background:#fff;
                  box-shadow:0 0 0 5px rgba(192,227,184,0.28),0 1px 4px rgba(0,0,0,0.3);"></div>
    </div>
    <div style="font-size:11.5px;color:rgba(255,255,255,0.5);margin-top:14px;text-align:center;">
      Range reflects the P25&ndash;P75 spread of comparable mature stores.
      Marker shows the most&#8209;likely point estimate.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Driver breakdown ───────────────────────────────────────────────────
        rows_html = ""
        for lbl, note, amt, bc, ac in drivers:
            w = f"{max(0, amt / point * 100):.1f}%" if point > 0 else "0%"
            amt_str = fmt(amt) if amt >= 0 else f"−{fmt(-amt)}"
            rows_html += f"""
<div style="display:grid;grid-template-columns:260px 1fr 160px;align-items:center;
            gap:24px;padding:14px 0;border-bottom:1px solid #EFEBE2;">
  <div>
    <div style="font-size:16px;font-weight:600;color:#1A1F1D;letter-spacing:-0.01em;">{lbl}</div>
    <div style="font-size:13px;color:#7A8582;margin-top:2px;">{note}</div>
  </div>
  <div style="height:16px;border-radius:999px;background:#F1EFE8;position:relative;overflow:hidden;">
    <div style="position:absolute;left:0;top:0;bottom:0;border-radius:999px;
                background:{bc};width:{w};"></div>
  </div>
  <div style="font-size:18px;font-weight:700;color:{ac};text-align:right;
              font-variant-numeric:tabular-nums;letter-spacing:-0.01em;">{amt_str}</div>
</div>"""

        st.markdown(f"""
<div style="background:#fff;border:1px solid #E3E0D6;border-radius:14px;padding:28px 36px;
            box-shadow:0 1px 2px rgba(6,82,75,0.06);margin-bottom:24px;">
  <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:16px;">
    <span style="font-size:21px;font-weight:700;color:#1A1F1D;letter-spacing:-0.01em;">
      What's driving this forecast
    </span>
    <span style="font-size:13px;color:#7A8582;">
      Each input's contribution to the most-likely figure
    </span>
  </div>
  {rows_html}
  <div style="display:grid;grid-template-columns:260px 1fr 160px;align-items:center;
              gap:24px;padding:18px 0 0;">
    <div style="font-size:13px;font-weight:700;color:#1A1F1D;text-transform:uppercase;
                letter-spacing:0.1em;">Most likely total</div>
    <div></div>
    <div style="font-size:22px;font-weight:800;color:#06524B;text-align:right;
                font-variant-numeric:tabular-nums;letter-spacing:-0.02em;">{fmt(point)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Comparable stores ──────────────────────────────────────────────────
        comp_rows_html = ""
        for c in comps:
            pill = (
                '<span style="background:#C0E3B8;color:#06524B;border-radius:999px;'
                'padding:4px 12px;font-size:13px;font-weight:700;">Yes</span>'
                if c["payroll_deduction_encoded"]
                else
                '<span style="background:#F1EFE8;color:#7A8582;border-radius:999px;'
                'padding:4px 12px;font-size:13px;font-weight:700;">No</span>'
            )
            comp_rows_html += f"""
<div style="display:grid;grid-template-columns:70px 1fr 80px 100px 100px 180px;
            align-items:center;gap:20px;padding:14px 0;border-bottom:1px solid #EFEBE2;">
  <div style="font-size:13px;color:#7A8582;font-weight:600;">#{c["store_num"]}</div>
  <div style="font-size:16px;font-weight:600;color:#1A1F1D;">{c["name"]}</div>
  <div style="font-size:15px;color:#4A5552;">{c["adic"]:,}</div>
  <div style="font-size:15px;color:#4A5552;">{c["size"]:,} sq ft</div>
  <div>{pill}</div>
  <div style="font-size:17px;font-weight:700;color:#06524B;text-align:right;
              font-variant-numeric:tabular-nums;">{fmt(c["t12_revenue"])}</div>
</div>"""

        st.markdown(f"""
<div style="background:#fff;border:1px solid #E3E0D6;border-radius:14px;padding:28px 36px;
            box-shadow:0 1px 2px rgba(6,82,75,0.06);margin-bottom:20px;">
  <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:16px;">
    <span style="font-size:21px;font-weight:700;color:#1A1F1D;letter-spacing:-0.01em;">
      Most similar stores in our fleet
    </span>
    <span style="font-size:13px;color:#7A8582;">
      Matched on ADC, shop size &amp; payroll deduction
    </span>
  </div>
  <div style="display:grid;grid-template-columns:70px 1fr 80px 100px 100px 180px;
              gap:20px;padding:0 0 10px;border-bottom:2px solid #E3E0D6;">
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">Store</div>
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">Name</div>
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">ADC</div>
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">Size</div>
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">Payroll</div>
    <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;
                color:#7A8582;text-align:right;">Actual Annual</div>
  </div>
  {comp_rows_html}
</div>
""", unsafe_allow_html=True)

        # Save button
        col_save, _ = st.columns([1, 4])
        with col_save:
            if st.button("Save Forecast"):
                save_forecast({
                    "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "hospital_name": display_name,
                    "adc":           adc_input,
                    "size":          size_input,
                    "pd":            pd_select,
                    "predicted":     round(point),
                    "low":           round(low),
                    "high":          round(high),
                    "top_comps":     " | ".join(c["name"] for c in comps),
                })
                st.success(f"Forecast for **{display_name}** saved.")

    if "last_forecast" not in st.session_state:
        st.markdown("""
<div style="text-align:center;padding:64px 0;color:#7A8582;font-size:15px;">
  Fill in the fields above and click <strong style="color:#4A5552;">Generate Forecast</strong>
  to see results.
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE — Saved Forecasts
# ════════════════════════════════════════════════════════════════════════════════
elif page == "Saved Forecasts":
    st.markdown("""
<h2 style="font-size:24px;font-weight:800;color:#06524B;letter-spacing:-0.02em;margin-bottom:4px;">
  Saved Forecasts
</h2>
<p style="font-size:15px;color:#7A8582;margin-top:0;margin-bottom:20px;">
  All forecasts saved during this session and previous runs.
</p>
""", unsafe_allow_html=True)

    print(f"[LEDGER PAGE] Ledger path: {LEDGER_PATH}", flush=True)
    print(f"[LEDGER PAGE] File exists: {os.path.exists(LEDGER_PATH)}", flush=True)
    ledger = pd.read_csv(LEDGER_PATH) if os.path.exists(LEDGER_PATH) else pd.DataFrame()
    print(f"[LEDGER PAGE] Rows loaded: {len(ledger)}", flush=True)
    if not ledger.empty:
        print(f"[LEDGER PAGE] Hospitals: {ledger['hospital_name'].tolist()}", flush=True)

    if ledger.empty:
        st.markdown("""
<div style="text-align:center;padding:64px 0;color:#7A8582;font-size:16px;">
  No forecasts saved yet. Generate a forecast and click <strong style="color:#4A5552;">Save Forecast</strong>.
</div>
""", unsafe_allow_html=True)
    else:
        ledger_display = ledger.iloc[::-1].reset_index(drop=True)
        rows_html = ""
        for _, row in ledger_display.iterrows():
            rows_html += f"""
<div style="display:grid;grid-template-columns:140px 1fr 70px 80px 70px 140px 160px 140px;
            align-items:center;gap:16px;padding:14px 0;border-bottom:1px solid #EFEBE2;">
  <div style="font-size:12px;color:#7A8582;">{row.get('timestamp','—')}</div>
  <div style="font-size:15px;font-weight:600;color:#1A1F1D;">{row.get('hospital_name','—')}</div>
  <div style="font-size:14px;color:#4A5552;">{int(row['adc']):,}</div>
  <div style="font-size:14px;color:#4A5552;">{int(row['size']):,}</div>
  <div style="font-size:14px;color:#4A5552;">{row.get('pd','—')}</div>
  <div style="font-size:15px;font-weight:700;color:#92400E;font-variant-numeric:tabular-nums;">${int(row['low']):,}</div>
  <div style="font-size:17px;font-weight:800;color:#06524B;font-variant-numeric:tabular-nums;">${int(row['predicted']):,}</div>
  <div style="font-size:15px;font-weight:700;color:#14532D;font-variant-numeric:tabular-nums;">${int(row['high']):,}</div>
</div>"""

        st.markdown(f"""
<div style="background:#fff;border:1px solid #E3E0D6;border-radius:14px;padding:28px 36px;
            box-shadow:0 1px 2px rgba(6,82,75,0.06);margin-bottom:16px;">
  <div style="display:grid;grid-template-columns:140px 1fr 70px 80px 70px 140px 160px 140px;
              gap:16px;padding:0 0 10px;border-bottom:2px solid #E3E0D6;margin-bottom:2px;">
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">When</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">Hospital</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">ADC</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">Sq Ft</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7A8582;">PD</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#92400E;">Conservative</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#06524B;">Most Likely</div>
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#14532D;">Optimistic</div>
  </div>
  {rows_html}
  <div style="font-size:13px;color:#7A8582;margin-top:14px;">
    {len(ledger_display)} forecast{"s" if len(ledger_display) != 1 else ""} saved
  </div>
</div>
""", unsafe_allow_html=True)

        col_dl, _ = st.columns([1, 5])
        with col_dl:
            st.download_button(
                "Download CSV",
                data=ledger.to_csv(index=False),
                file_name="cloverkey_forecasts.csv",
                mime="text/csv",
            )

# ════════════════════════════════════════════════════════════════════════════════
# PAGE — About This Model
# ════════════════════════════════════════════════════════════════════════════════
elif page == "About This Model":
    # Stat tiles
    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:28px;margin-top:8px;">
  <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:12px;padding:24px 28px;">
    <div style="font-size:52px;font-weight:800;color:#06524B;letter-spacing:-0.03em;
                font-variant-numeric:tabular-nums;">{training_mape}%</div>
    <div style="font-size:14px;font-weight:600;color:#7A8582;margin-top:8px;">
      Average error rate (leave-one-out validation)
    </div>
  </div>
  <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:12px;padding:28px 32px;">
    <div style="font-size:52px;font-weight:800;color:#06524B;letter-spacing:-0.03em;
                font-variant-numeric:tabular-nums;">{n_stores}</div>
    <div style="font-size:14px;font-weight:600;color:#7A8582;margin-top:8px;">
      General acute-care hospitals trained on
    </div>
  </div>
  <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:12px;padding:28px 32px;">
    <div style="font-size:52px;font-weight:800;color:#06524B;letter-spacing:-0.03em;
                font-variant-numeric:tabular-nums;">4</div>
    <div style="font-size:14px;font-weight:600;color:#7A8582;margin-top:8px;">
      Model inputs — ADC, shop size, payroll deduction, ADC&times;size
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # How it was built + Accuracy
    chart_html = ""
    if HAS_ASSETS:
        chart_html = f"""
<div style="border:1px solid #E3E0D6;border-radius:12px;overflow:hidden;margin:20px 0;">
  <img src="data:image/png;base64,{CHART_B64}" style="width:100%;display:block;" />
  <div style="padding:10px 16px;background:#F6F3EC;font-size:12px;color:#7A8582;">
    LOO cross-validated performance on training stores: actual annual revenue (black) vs. the prior
    hand-tuned benchmark (blue) vs. the V2 four-feature log&nbsp;+&nbsp;ADC&times;size interaction model (red).
  </div>
</div>"""

    st.markdown(f"""
<div style="background:#fff;border:1px solid #E3E0D6;border-radius:14px;padding:28px 32px;
            box-shadow:0 1px 2px rgba(6,82,75,0.06);margin-bottom:20px;">

  <div style="font-size:25px;font-weight:800;text-transform:uppercase;letter-spacing:0.18em;
              color:#06524B;margin-bottom:10px;">How it was built</div>
  <p style="font-size:15px;line-height:1.7;color:#1A1F1D;margin:0 0 14px;">
    The model is a four-feature regression trained in log-revenue space, which is the standard
    approach for revenue prediction when target values span a wide range (our training stores range
    from $109K to $1.78M in annual revenue). The four inputs are: average daily census (ADC), gift
    shop square footage, payroll deduction availability, and an ADC&times;size interaction term that
    captures how larger hospitals paired with larger gift shops amplify each other's effect on revenue.
  </p>
  <p style="font-size:15px;line-height:1.7;color:#1A1F1D;margin:0 0 14px;">
    All numeric inputs are log-transformed before fitting. This means the model learns multiplicative
    relationships rather than additive ones — a 10% increase in ADC produces roughly the same
    percentage change in predicted revenue at a small hospital as it does at a large one, rather than
    the same dollar change. Coefficients can be read as elasticities: log_ADC's coefficient is
    approximately 0.44, meaning a 10% increase in ADC predicts roughly a 4.4% increase in revenue,
    holding other inputs constant.
  </p>
  <p style="font-size:15px;line-height:1.7;color:#1A1F1D;margin:0 0 22px;">
    The model predicts mature, steady-state annual revenue — what the store would earn once it reaches
    full ramp, typically 18 to 24 months after opening. Year-1 projections require a separate ramp
    adjustment (see Known Limitations).
  </p>

  <div style="font-size:25px;font-weight:800;text-transform:uppercase;letter-spacing:0.18em;
              color:#06524B;margin-bottom:10px;">Accuracy</div>
  <p style="font-size:15px;line-height:1.7;color:#1A1F1D;margin:0 0 14px;">
    Validated using leave-one-out cross-validation across all {n_stores} training stores. Under LOO,
    each store is held out, the model is refit on the remaining {n_stores - 1}, and the held-out store
    is predicted. The V2 model achieves an <strong>{training_mape}% mean absolute percentage
    error</strong> — an improvement from 25.1% in V1 (a LightGBM + Ridge + Elastic Net ensemble with
    11 features) and 23.0% under the prior hand-tuned per-unit-dollar benchmark. The chart below shows
    model performance on training stores: actual annual revenue, the prior benchmark's predictions, and
    the V2 four-feature model's predictions.
  </p>
  <p style="font-size:15px;line-height:1.7;color:#1A1F1D;margin:0 0 4px;">
    A note on interpretation: {training_mape}% is the average error across stores during
    cross-validation. Performance on any individual bid will vary — most predictions land within the
    displayed confidence range, but the model is not equally accurate at all revenue levels (see Known
    Limitations).
  </p>
  {chart_html}

  <div style="font-size:25px;font-weight:800;text-transform:uppercase;letter-spacing:0.18em;
              color:#06524B;margin:20px 0 14px;">Known limitations</div>
  <div style="display:flex;flex-direction:column;gap:12px;">
    <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:10px;
                padding:18px 20px;display:flex;gap:16px;align-items:flex-start;">
      <div style="font-size:18px;font-weight:800;color:#06524B;min-width:28px;line-height:1.3;">1</div>
      <div>
        <div style="font-size:14px;font-weight:700;color:#1A1F1D;margin-bottom:4px;">
          Specialty hospitals are out of scope
        </div>
        <div style="font-size:13.5px;color:#4A5552;line-height:1.6;">
          The training set is general acute-care hospitals only. For Children's hospital bids, Store 101
          (Boston Children's) is the only available comparable in the current dataset. For Cancer hospital
          bids, use Stores 108 and 122 (Moffitt locations). Do not apply this model directly to specialty
          bids — its coefficients were fit on a different population.
        </div>
      </div>
    </div>
    <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:10px;
                padding:18px 20px;display:flex;gap:16px;align-items:flex-start;">
      <div style="font-size:18px;font-weight:800;color:#06524B;min-width:28px;line-height:1.3;">2</div>
      <div>
        <div style="font-size:14px;font-weight:700;color:#1A1F1D;margin-bottom:4px;">
          Top-decile academic medical centers tend to under-predict
        </div>
        <div style="font-size:13.5px;color:#4A5552;line-height:1.6;">
          Hospitals with ADC above approximately 700 and large gift shops (over 2,000 sq ft) in tier-1
          metros — Brigham and Women's is the canonical example — generate revenue that exceeds the
          model's prediction by 15 to 25%. The model's features don't capture brand premium, urban
          density, or academic prestige effects. Flag these bids for manual review and consider applying
          an uplift based on the comp-set output rather than relying on the point estimate.
        </div>
      </div>
    </div>
    <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:10px;
                padding:18px 20px;display:flex;gap:16px;align-items:flex-start;">
      <div style="font-size:18px;font-weight:800;color:#06524B;min-width:28px;line-height:1.3;">3</div>
      <div>
        <div style="font-size:14px;font-weight:700;color:#1A1F1D;margin-bottom:4px;">
          Dual-store hospitals require an adjustment
        </div>
        <div style="font-size:13.5px;color:#4A5552;line-height:1.6;">
          When two Cloverkey shops operate inside the same hospital (e.g., Northwestern Memorial main
          campus), each shop captures only a portion of the hospital's foot traffic. The training data
          corrects for this by halving ADC and FTE for shared hospitals. When forecasting a new
          dual-store opportunity, divide the hospital's ADC by the number of planned Cloverkey shops
          before entering it.
        </div>
      </div>
    </div>
    <div style="background:#F6F3EC;border:1px solid #E3E0D6;border-radius:10px;
                padding:18px 20px;display:flex;gap:16px;align-items:flex-start;">
      <div style="font-size:18px;font-weight:800;color:#06524B;min-width:28px;line-height:1.3;">4</div>
      <div>
        <div style="font-size:14px;font-weight:700;color:#1A1F1D;margin-bottom:4px;">
          Year-1 ramp must be applied separately
        </div>
        <div style="font-size:13.5px;color:#4A5552;line-height:1.6;">
          This model forecasts mature, steady-state annual revenue. New stores typically reach maturity
          18 to 24 months after opening. For year-1 projections, multiply the point estimate by roughly
          0.55 to 0.75, depending on hospital type and opening timing. A dedicated ramp curve calibrated
          on existing store opening histories should be applied separately rather than baked into this
          model.
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
