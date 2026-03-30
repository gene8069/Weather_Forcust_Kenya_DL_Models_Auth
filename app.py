"""
Kenya Local Weather Forecasting System — with User Authentication
=================================================================
Streamlit + Supabase auth & database
"""

import streamlit as st
import pandas as pd
import numpy as np
import json, os, joblib, warnings, hashlib, re
from datetime import date, timedelta
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kenya Weather Forecast",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

  .hero {
    background: linear-gradient(135deg, #0d3b2e 0%, #1a6b3c 50%, #0d3b2e 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    border: 1px solid #2ecc7133;
  }
  .hero h1 { color: #2ecc71; font-size: 2rem; margin: 0; font-weight: 700; }
  .hero p  { color: #a8d5b5; margin: 0.4rem 0 0; font-size: 0.95rem; }

  .auth-box {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 16px; padding: 2rem; max-width: 420px;
    margin: 2rem auto;
  }
  .auth-box h2 { color: #2ecc71; font-size: 1.4rem; margin-bottom: 1.2rem; }

  .metric-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center;
  }
  .metric-card .val { font-size: 1.8rem; font-weight: 700; color: #2ecc71; }
  .metric-card .lbl { font-size: 0.8rem; color: #8b949e; margin-top: 4px; }

  .forecast-row {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 0.8rem 1.2rem; margin: 0.4rem 0;
    display: flex; align-items: center; justify-content: space-between;
  }
  .day-badge {
    background: #1f2d3d; color: #58a6ff; font-weight: 600;
    padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;
    min-width: 90px; text-align: center;
  }
  .weather-val { color: #e6edf3; font-size: 0.9rem; text-align: center; min-width: 80px; }
  .weather-lbl { color: #8b949e; font-size: 0.7rem; }

  .section-title {
    color: #e6edf3; font-size: 1.15rem; font-weight: 600;
    border-left: 3px solid #2ecc71; padding-left: 0.8rem;
    margin: 1.5rem 0 1rem;
  }
  .welcome-badge {
    background: #1a3d2b; border: 1px solid #2ecc7155;
    border-radius: 10px; padding: 0.8rem 1.2rem; margin-bottom: 1rem;
    color: #2ecc71; font-weight: 600;
  }
  .history-row {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.7rem 1rem; margin: 0.3rem 0;
    display: flex; justify-content: space-between; align-items: center;
  }

  div[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #30363d; }
  div[data-testid="stSidebar"] * { color: #e6edf3 !important; }
  .stTextInput > div > div > input {
    background: #0d1117 !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 8px !important;
  }
  .stSelectbox > div > div { background: #0d1117 !important; color: #e6edf3 !important; }
  .stMultiSelect > div > div { background: #0d1117 !important; }
  .stButton > button {
    background: #2ecc71; color: #0d1117; font-weight: 700;
    border: none; border-radius: 8px; padding: 0.5rem 1.5rem; width: 100%;
  }
  .stButton > button:hover { background: #27ae60; }
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
MODEL_DIR = "kenya_models"
DATA_PATH = "kenya_weather_data/kenya_all_counties.csv"

# ── Supabase setup ────────────────────────────────────────────────────────────
# Install: pip install supabase
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    url  = st.secrets["SUPABASE_URL"]
    key  = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ── Password hashing ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# ── Auth functions ────────────────────────────────────────────────────────────
def sign_up(name, email, password, county, occupation, preferred_vars):
    """Register a new user in Supabase."""
    try:
        # Check if email already exists
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return False, "Email already registered. Please log in."

        user_data = {
            "name":           name,
            "email":          email,
            "password_hash":  hash_password(password),
            "home_county":    county,
            "occupation":     occupation,
            "preferred_vars": preferred_vars,  # stored as JSON array
            "created_at":     date.today().isoformat(),
        }
        supabase.table("users").insert(user_data).execute()
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Error: {e}"


def sign_in(email, password):
    """Authenticate user against Supabase."""
    try:
        result = supabase.table("users") \
            .select("*") \
            .eq("email", email) \
            .eq("password_hash", hash_password(password)) \
            .execute()
        if result.data:
            return True, result.data[0]
        return False, "Invalid email or password."
    except Exception as e:
        return False, f"Error: {e}"


def save_forecast_history(user_id, county, forecast_df):
    """Save a forecast run to the user's history."""
    try:
        record = {
            "user_id":      user_id,
            "county":       county,
            "forecast_date": date.today().isoformat(),
            "forecast_data": forecast_df.to_json(orient="records", date_format="iso"),
        }
        supabase.table("forecast_history").insert(record).execute()
    except Exception as e:
        st.warning(f"Could not save forecast history: {e}")


def get_forecast_history(user_id):
    """Fetch user's past forecast runs."""
    try:
        result = supabase.table("forecast_history") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("forecast_date", desc=True) \
            .limit(20) \
            .execute()
        return result.data or []
    except:
        return []


# ── Model loading ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model_and_meta():
    import tensorflow as tf
    with open(f"{MODEL_DIR}/model_metadata.json") as f:
        meta = json.load(f)
    keras_path = f"{MODEL_DIR}/best_model_{meta['best_model']}.keras"
    h5_path    = f"{MODEL_DIR}/best_model_{meta['best_model']}.h5"
    if os.path.exists(keras_path):
        model = tf.keras.models.load_model(keras_path)
    else:
        model = tf.keras.models.load_model(h5_path, compile=False)
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    scalers = joblib.load(f"{MODEL_DIR}/scalers.pkl")
    return model, meta, scalers


@st.cache_data(ttl=86400)
def load_data():
    import requests, time
    df        = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df        = df.sort_values(["county","date"]).reset_index(drop=True)
    last_date = df["date"].max().date()
    today     = date.today()
    gap_days  = (today - last_date).days

    if gap_days <= 1:
        return df

    gap_start     = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    gap_end       = today.strftime("%Y-%m-%d")
    county_coords = df.groupby("county")[["latitude","longitude"]].first().to_dict("index")
    new_rows      = []

    for county, coords in county_coords.items():
        try:
            params = {
                "latitude": coords["latitude"], "longitude": coords["longitude"],
                "start_date": gap_start, "end_date": gap_end,
                "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
                         "precipitation_sum,windspeed_10m_max,shortwave_radiation_sum,"
                         "et0_fao_evapotranspiration",
                "hourly": "relativehumidity_2m,surface_pressure",
                "timezone": "Africa/Nairobi",
            }
            resp = requests.get("https://archive-api.open-meteo.com/v1/archive",
                                params=params, timeout=30)
            if resp.status_code != 200:
                continue
            data      = resp.json()
            daily_df  = pd.DataFrame(data["daily"])
            daily_df.rename(columns={"time":"date"}, inplace=True)
            daily_df["date"] = pd.to_datetime(daily_df["date"])
            hourly_df = pd.DataFrame(data["hourly"])
            hourly_df["time"] = pd.to_datetime(hourly_df["time"])
            hourly_df["date"] = hourly_df["time"].dt.normalize()
            hourly_daily = hourly_df.groupby("date")[
                ["relativehumidity_2m","surface_pressure"]].mean().reset_index()
            merged = pd.merge(daily_df, hourly_daily, on="date", how="left")
            merged.rename(columns={
                "temperature_2m_max":"temp_max_c","temperature_2m_min":"temp_min_c",
                "temperature_2m_mean":"temp_mean_c","precipitation_sum":"rainfall_mm",
                "windspeed_10m_max":"windspeed_kmh","shortwave_radiation_sum":"solar_radiation_mjm2",
                "et0_fao_evapotranspiration":"evapotranspiration_mm",
                "relativehumidity_2m":"humidity_pct","surface_pressure":"pressure_hpa",
            }, inplace=True)
            merged["county"]    = county
            merged["latitude"]  = coords["latitude"]
            merged["longitude"] = coords["longitude"]
            new_rows.append(merged)
            time.sleep(2)
        except Exception:
            continue

    if new_rows:
        new_df = pd.concat(new_rows, ignore_index=True)
        df     = pd.concat([df, new_df], ignore_index=True)
        df.drop_duplicates(subset=["county","date"], keep="last", inplace=True)
        df     = df.sort_values(["county","date"]).reset_index(drop=True)
        df.to_csv(DATA_PATH, index=False)
    return df


# ── Feature engineering ───────────────────────────────────────────────────────
def engineer_features(cdf):
    cdf = cdf.copy()
    TARGETS = ["temp_mean_c","rainfall_mm","humidity_pct","windspeed_kmh","pressure_hpa"]
    for col in TARGETS:
        if col in cdf.columns:
            cdf[col] = cdf[col].interpolate().ffill().bfill()
    cdf["day_of_year"] = cdf["date"].dt.dayofyear
    cdf["month"]       = cdf["date"].dt.month
    cdf["week"]        = cdf["date"].dt.isocalendar().week.astype(int)
    cdf["sin_doy"]     = np.sin(2 * np.pi * cdf["day_of_year"] / 365)
    cdf["cos_doy"]     = np.cos(2 * np.pi * cdf["day_of_year"] / 365)
    cdf["sin_month"]   = np.sin(2 * np.pi * cdf["month"] / 12)
    cdf["cos_month"]   = np.cos(2 * np.pi * cdf["month"] / 12)
    for col in TARGETS:
        if col in cdf.columns:
            for lag in [1,3,7]:
                cdf[f"{col}_lag{lag}"] = cdf[col].shift(lag)
            for win in [7,14]:
                cdf[f"{col}_roll{win}mean"] = cdf[col].rolling(win, min_periods=1).mean()
    cdf.dropna(inplace=True)
    return cdf


def predict_county(county, df, model, meta, scalers):
    FEATURE_COLS  = meta["feature_cols"]
    TARGET_COLS   = meta["target_cols"]
    LOOKBACK      = meta["lookback"]
    FORECAST_DAYS = meta["forecast_days"]

    cdf  = df[df["county"] == county].copy().reset_index(drop=True)
    cdf  = engineer_features(cdf)
    for c in FEATURE_COLS:
        if c not in cdf.columns:
            cdf[c] = 0.0

    scaler     = scalers[county]
    scaled     = scaler.transform(cdf[FEATURE_COLS])
    X_input    = scaled[-LOOKBACK:].reshape(1, LOOKBACK, len(FEATURE_COLS))
    pred_norm  = model.predict(X_input, verbose=0)[0]

    target_idx = [FEATURE_COLS.index(t) for t in TARGET_COLS]
    dummy      = np.zeros((FORECAST_DAYS, len(FEATURE_COLS)))
    dummy[:, target_idx] = pred_norm
    inv        = scaler.inverse_transform(dummy)
    pred_real  = inv[:, target_idx]

    last_date = cdf["date"].max()
    dates     = pd.date_range(last_date + timedelta(days=1), periods=FORECAST_DAYS)
    fc = pd.DataFrame(pred_real, columns=TARGET_COLS)
    fc.insert(0, "date", dates)
    fc["temp_mean_c"]   = fc["temp_mean_c"].clip(5, 45)
    fc["rainfall_mm"]   = fc["rainfall_mm"].clip(0, 200)
    fc["humidity_pct"]  = fc["humidity_pct"].clip(0, 100)
    fc["windspeed_kmh"] = fc["windspeed_kmh"].clip(0, 120)
    fc["pressure_hpa"]  = fc["pressure_hpa"].clip(850, 1050)
    return fc


def rain_emoji(mm):
    if mm < 1:    return "☀️"
    elif mm < 5:  return "🌤️"
    elif mm < 15: return "🌧️"
    else:         return "⛈️"


VAR_LABELS = {
    "temp_mean_c":   "Temperature (°C)",
    "rainfall_mm":   "Rainfall (mm)",
    "humidity_pct":  "Humidity (%)",
    "windspeed_kmh": "Wind Speed (km/h)",
    "pressure_hpa":  "Pressure (hPa)",
}

ALL_COUNTIES = [
    "Nairobi","Mombasa","Kwale","Kilifi","Tana River","Lamu","Taita Taveta",
    "Garissa","Wajir","Mandera","Marsabit","Isiolo","Meru","Tharaka Nithi",
    "Embu","Kitui","Machakos","Makueni","Nyandarua","Nyeri","Kirinyaga",
    "Murang'a","Kiambu","Turkana","West Pokot","Samburu","Trans Nzoia",
    "Uasin Gishu","Elgeyo Marakwet","Nandi","Baringo","Laikipia","Nakuru",
    "Narok","Kajiado","Kericho","Bomet","Kakamega","Vihiga","Bungoma",
    "Busia","Siaya","Kisumu","Homa Bay","Migori","Kisii","Nyamira"
]

OCCUPATIONS = [
    "Farmer", "Pastoralist", "Transport Operator", "Emergency Planner",
    "Researcher", "Student", "Business Owner", "Other"
]


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"   # login | signup


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES (shown when not logged in)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.user is None:

    st.markdown("""
    <div class="hero">
      <h1>🌦️ Kenya Weather Forecasting System</h1>
      <p>Deep Learning · All 47 Counties · Personalised 7-Day Forecasts</p>
    </div>""", unsafe_allow_html=True)

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    if st.session_state.auth_page == "login":
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown("## 👤 Sign In")

            email    = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            if st.button("Sign In →"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, result = sign_in(email, password)
                    if ok:
                        st.session_state.user = result
                        st.success(f"Welcome back, {result['name']}!")
                        st.rerun()
                    else:
                        st.error(result)

            st.markdown("---")
            st.markdown("<center>Don't have an account?</center>", unsafe_allow_html=True)
            if st.button("Create Account"):
                st.session_state.auth_page = "signup"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── SIGN UP ───────────────────────────────────────────────────────────────
    elif st.session_state.auth_page == "signup":
        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            st.markdown("## 🌱 Create Account")

            name       = st.text_input("Full Name", placeholder="e.g. John Kamau")
            email      = st.text_input("Email Address", placeholder="you@example.com")
            password   = st.text_input("Password", type="password", placeholder="Min 6 characters")
            password2  = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
            county     = st.selectbox("Your Home County", sorted(ALL_COUNTIES))
            occupation = st.selectbox("Occupation", OCCUPATIONS)
            pref_vars  = st.multiselect(
                "Preferred Weather Variables",
                options=list(VAR_LABELS.values()),
                default=["Temperature (°C)", "Rainfall (mm)"],
                help="These will be highlighted in your personal forecast"
            )

            if st.button("Create Account →"):
                if not all([name, email, password, password2]):
                    st.error("Please fill in all fields.")
                elif not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif password != password2:
                    st.error("Passwords do not match.")
                elif not pref_vars:
                    st.error("Please select at least one weather variable.")
                else:
                    ok, msg = sign_up(name, email, password, county, occupation,
                                      json.dumps(pref_vars))
                    if ok:
                        st.success(msg + " Please sign in.")
                        st.session_state.auth_page = "login"
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("---")
            st.markdown("<center>Already have an account?</center>", unsafe_allow_html=True)
            if st.button("Back to Sign In"):
                st.session_state.auth_page = "login"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()   # don't render anything else if not logged in


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP (only reached when logged in)
# ══════════════════════════════════════════════════════════════════════════════
user         = st.session_state.user
model, meta, scalers = load_model_and_meta()
df           = load_data()
comparison_df = pd.read_csv(f"{MODEL_DIR}/model_comparison.csv")

# Parse preferred vars
try:
    pref_vars = json.loads(user.get("preferred_vars", "[]"))
except:
    pref_vars = ["Temperature (°C)", "Rainfall (mm)"]

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {user['name']}")
    st.markdown(f"📍 *{user['home_county']}*")
    st.markdown(f"💼 *{user.get('occupation', '')}*")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠  My Dashboard",
        "🗺️  Kenya Map",
        "📍  County Forecast",
        "📊  Model Comparison",
        "📈  Predicted vs Actual",
        "📋  My Forecast History",
    ])
    st.markdown("---")
    st.markdown("**Model:** GRU Neural Network")
    st.markdown("**Coverage:** 47 Counties")
    st.markdown("**Horizon:** 7 Days")
    st.markdown("---")
    if st.button("🚪 Sign Out"):
        st.session_state.user = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  My Dashboard":
    st.markdown(f"""
    <div class="hero">
      <h1>👋 Welcome back, {user['name']}!</h1>
      <p>Here is your personalised 7-day weather forecast for <b>{user['home_county']}</b> County</p>
    </div>""", unsafe_allow_html=True)

    # Auto-forecast home county
    with st.spinner(f"🔮 Forecasting {user['home_county']}..."):
        fc = predict_county(user["home_county"], df, model, meta, scalers)
        save_forecast_history(user["id"], user["home_county"], fc)

    # Summary metrics — show only preferred vars
    VAR_MAP_REV = {v: k for k, v in VAR_LABELS.items()}
    pref_cols   = [VAR_MAP_REV.get(v) for v in pref_vars if VAR_MAP_REV.get(v)]

    st.markdown('<div class="section-title">Your Preferred Variables — 7-Day Summary</div>',
                unsafe_allow_html=True)

    metric_data = {
        "temp_mean_c":   (f"{fc['temp_mean_c'].mean():.1f}°C",  "Avg Temperature"),
        "rainfall_mm":   (f"{fc['rainfall_mm'].sum():.1f}mm",   "Total Rainfall"),
        "humidity_pct":  (f"{fc['humidity_pct'].mean():.0f}%",  "Avg Humidity"),
        "windspeed_kmh": (f"{fc['windspeed_kmh'].mean():.1f}km/h","Avg Wind"),
        "pressure_hpa":  (f"{fc['pressure_hpa'].mean():.0f}hPa","Avg Pressure"),
    }
    cols_to_show = pref_cols if pref_cols else list(metric_data.keys())
    cols = st.columns(len(cols_to_show))
    for col, var in zip(cols, cols_to_show):
        val, lbl = metric_data[var]
        col.markdown(f"""
        <div class="metric-card">
          <div class="val">{val}</div>
          <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    # Daily forecast cards
    st.markdown(f'<div class="section-title">Daily Forecast — {user["home_county"]}</div>',
                unsafe_allow_html=True)
    for _, row in fc.iterrows():
        emoji = rain_emoji(row["rainfall_mm"])
        st.markdown(f"""
        <div class="forecast-row">
          <span class="day-badge">{row['date'].strftime('%a %d %b')}</span>
          <div class="weather-val">{emoji} {row['temp_mean_c']:.1f}°C<br><span class="weather-lbl">Temp</span></div>
          <div class="weather-val">💧 {row['rainfall_mm']:.1f}mm<br><span class="weather-lbl">Rain</span></div>
          <div class="weather-val">💦 {row['humidity_pct']:.0f}%<br><span class="weather-lbl">Humidity</span></div>
          <div class="weather-val">💨 {row['windspeed_kmh']:.1f}km/h<br><span class="weather-lbl">Wind</span></div>
          <div class="weather-val">🔵 {row['pressure_hpa']:.0f}hPa<br><span class="weather-lbl">Pressure</span></div>
        </div>""", unsafe_allow_html=True)

    def hex_to_rgba(hex_color, alpha=0.15):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{alpha})"
   # Trend chart for preferred variables
    import plotly.graph_objects as go
    st.markdown('<div class="section-title">Trend Charts</div>', unsafe_allow_html=True)
    days = [d.strftime("%a %d") for d in fc["date"]]
    colors_map = {
        "temp_mean_c":"#ef5350","rainfall_mm":"#42a5f5",
        "humidity_pct":"#26c6da","windspeed_kmh":"#ffa726","pressure_hpa":"#ab47bc"
    }
    for var in cols_to_show:
        fig = go.Figure(go.Scatter(
            x=days, y=fc[var], mode="lines+markers",
            line=dict(color=colors_map.get(var,"#2ecc71"), width=2.5),
            marker=dict(size=7), name=VAR_LABELS.get(var, var),
            fill="tozeroy",
            fillcolor=hex_to_rgba(colors_map.get(var,"#2ecc71"), 0.15)  # Use the function instead of string concatenation
        ))
        fig.update_layout(
            title=VAR_LABELS.get(var, var), height=220,
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font=dict(color="#e6edf3", size=11),
            margin=dict(t=35, b=20, l=40, r=20),
            xaxis=dict(gridcolor="#30363d"),
            yaxis=dict(gridcolor="#30363d"),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COUNTY FORECAST (pick any county)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📍  County Forecast":
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.markdown("""
    <div class="hero">
      <h1>📍 County Forecast</h1>
      <p>Predict weather for any of Kenya's 47 counties</p>
    </div>""", unsafe_allow_html=True)

    counties   = sorted(df["county"].unique().tolist())
    default_i  = counties.index(user["home_county"]) if user["home_county"] in counties else 0
    selected   = st.selectbox("Select County", counties, index=default_i)

    with st.spinner(f"🔮 Predicting {selected}..."):
        fc = predict_county(selected, df, model, meta, scalers)
        save_forecast_history(user["id"], selected, fc)

    # Summary
    st.markdown('<div class="section-title">7-Day Summary</div>', unsafe_allow_html=True)
    m1,m2,m3,m4,m5 = st.columns(5)
    for col, val, lbl in [
        (m1, f"{fc['temp_mean_c'].mean():.1f}°C",  "Avg Temperature"),
        (m2, f"{fc['rainfall_mm'].sum():.1f}mm",   "Total Rainfall"),
        (m3, f"{fc['humidity_pct'].mean():.0f}%",  "Avg Humidity"),
        (m4, f"{fc['windspeed_kmh'].mean():.1f}km/h","Avg Wind"),
        (m5, f"{fc['pressure_hpa'].mean():.0f}hPa","Avg Pressure"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="val">{val}</div>
          <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    # Daily cards
    st.markdown('<div class="section-title">Daily Breakdown</div>', unsafe_allow_html=True)
    for _, row in fc.iterrows():
        emoji = rain_emoji(row["rainfall_mm"])
        st.markdown(f"""
        <div class="forecast-row">
          <span class="day-badge">{row['date'].strftime('%a %d %b')}</span>
          <div class="weather-val">{emoji} {row['temp_mean_c']:.1f}°C<br><span class="weather-lbl">Temp</span></div>
          <div class="weather-val">💧 {row['rainfall_mm']:.1f}mm<br><span class="weather-lbl">Rain</span></div>
          <div class="weather-val">💦 {row['humidity_pct']:.0f}%<br><span class="weather-lbl">Humidity</span></div>
          <div class="weather-val">💨 {row['windspeed_kmh']:.1f}km/h<br><span class="weather-lbl">Wind</span></div>
          <div class="weather-val">🔵 {row['pressure_hpa']:.0f}hPa<br><span class="weather-lbl">Pressure</span></div>
        </div>""", unsafe_allow_html=True)

    # Trend charts
    st.markdown('<div class="section-title">7-Day Trend Charts</div>', unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=3,
        subplot_titles=["Temperature (°C)","Rainfall (mm)","Humidity (%)",
                        "Wind Speed (km/h)","Pressure (hPa)",""],
        vertical_spacing=0.15)
    days = [d.strftime("%a %d") for d in fc["date"]]
    for (vals, color, row, col) in [
        (fc["temp_mean_c"],  "#ef5350",1,1),(fc["rainfall_mm"],  "#42a5f5",1,2),
        (fc["humidity_pct"],"#26c6da",1,3),(fc["windspeed_kmh"],"#ffa726",2,1),
        (fc["pressure_hpa"],"#ab47bc",2,2),
    ]:
        fig.add_trace(go.Scatter(x=days, y=vals, mode="lines+markers",
            line=dict(color=color,width=2.5), marker=dict(size=7), showlegend=False),
            row=row, col=col)
    fig.update_layout(height=420, paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        font=dict(color="#e6edf3",size=11), margin=dict(t=40,b=20,l=20,r=20))
    fig.update_xaxes(gridcolor="#30363d", tickfont=dict(size=9))
    fig.update_yaxes(gridcolor="#30363d")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FORECAST HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋  My Forecast History":
    st.markdown("""
    <div class="hero">
      <h1>📋 My Forecast History</h1>
      <p>All your previous forecast lookups saved automatically</p>
    </div>""", unsafe_allow_html=True)

    history = get_forecast_history(user["id"])

    if not history:
        st.info("No forecast history yet. Run a forecast on the Dashboard or County Forecast page!")
    else:
        st.markdown(f'<div class="section-title">Last {len(history)} Forecasts</div>',
                    unsafe_allow_html=True)
        for record in history:
            fc_data = pd.read_json(record["forecast_data"])
            avg_temp = fc_data["temp_mean_c"].mean() if "temp_mean_c" in fc_data else 0
            total_rain = fc_data["rainfall_mm"].sum() if "rainfall_mm" in fc_data else 0
            st.markdown(f"""
            <div class="history-row">
              <div>
                <b style="color:#e6edf3;">📍 {record['county']}</b>
                <span style="color:#8b949e; font-size:0.8rem; margin-left:10px;">
                  {record['forecast_date']}
                </span>
              </div>
              <div style="color:#8b949e; font-size:0.85rem;">
                🌡️ {avg_temp:.1f}°C avg &nbsp;|&nbsp; 💧 {total_rain:.1f}mm total
              </div>
            </div>""", unsafe_allow_html=True)

            with st.expander(f"View full forecast — {record['county']} ({record['forecast_date']})"):
                st.dataframe(fc_data.round(2), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: KENYA MAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️  Kenya Map":
    import folium
    from streamlit_folium import st_folium

    st.markdown("""
    <div class="hero">
      <h1>🗺️ Kenya Weather Map</h1>
      <p>Click any county marker to see its 7-day forecast</p>
    </div>""", unsafe_allow_html=True)

    @st.cache_data
    def build_all_forecasts():
        forecasts = {}
        for county in df["county"].unique():
            try:
                forecasts[county] = predict_county(county, df, model, meta, scalers)
            except:
                pass
        return forecasts

    with st.spinner("🔮 Generating forecasts for all 47 counties..."):
        all_forecasts = build_all_forecasts()

    county_coords = df.groupby("county")[["latitude","longitude"]].first().to_dict("index")

    def temp_color(t):
        if t < 15: return "#4fc3f7"
        elif t < 20: return "#81c784"
        elif t < 25: return "#aed581"
        elif t < 30: return "#ffb74d"
        else: return "#ef5350"

    kenya_map = folium.Map(location=[0.023, 37.906], zoom_start=6,
                           tiles="CartoDB dark_matter")

    for county, fc in all_forecasts.items():
        coords   = county_coords.get(county, {})
        lat, lon = coords.get("latitude", 0), coords.get("longitude", 0)
        avg_temp = fc["temp_mean_c"].mean()
        color    = temp_color(avg_temp)
        rows = "".join([
            f"<tr><td style='padding:5px 8px;color:#aaa;'><b>{r['date'].strftime('%a %d %b')}</b></td>"
            f"<td style='padding:5px 8px;'>{rain_emoji(r['rainfall_mm'])} {r['temp_mean_c']:.1f}°C</td>"
            f"<td style='padding:5px 8px;color:#64b5f6;'>💧 {r['rainfall_mm']:.1f}mm</td>"
            f"<td style='padding:5px 8px;color:#80cbc4;'>💦 {r['humidity_pct']:.0f}%</td>"
            f"<td style='padding:5px 8px;color:#ffcc02;'>💨 {r['windspeed_kmh']:.1f}km/h</td></tr>"
            for _, r in fc.iterrows()
        ])
        popup_html = f"""
        <div style='font-family:Arial;background:#1a1a2e;color:#e0e0e0;width:380px;border-radius:10px;overflow:hidden;'>
          <div style='background:linear-gradient(135deg,#1a6b3c,#2ecc71);padding:10px 14px;'>
            <b style='font-size:15px;'>📍 {county} County</b><br>
            <span style='font-size:11px;'>7-Day · Avg {avg_temp:.1f}°C · Rain {fc['rainfall_mm'].sum():.0f}mm</span>
          </div>
          <table style='width:100%;border-collapse:collapse;font-size:12px;'>
            <tr style='background:#0d2a1e;color:#2ecc71;'>
              <th style='padding:5px 8px;'>Day</th><th>Temp</th><th>Rain</th><th>Humidity</th><th>Wind</th>
            </tr>{rows}
          </table>
        </div>"""
        folium.CircleMarker(
            location=[lat, lon], radius=13, color="white", weight=1.5,
            fill=True, fill_color=color, fill_opacity=0.9,
            tooltip=folium.Tooltip(f"<b>{county}</b> · {avg_temp:.1f}°C", sticky=True),
            popup=folium.Popup(folium.IFrame(popup_html, width=400, height=250), max_width=410)
        ).add_to(kenya_map)

    st_folium(kenya_map, width="100%", height=600)

    # Temperature legend
    cols = st.columns(5)
    for col, (rng, clr) in zip(cols, [
        ("<15°C","#4fc3f7"),("15-20°C","#81c784"),("20-25°C","#aed581"),
        ("25-30°C","#ffb74d"),(">30°C","#ef5350")
    ]):
        col.markdown(f"""
        <div style='text-align:center;background:#161b22;border-radius:8px;
                    padding:8px;border:1px solid #30363d;'>
          <div style='width:18px;height:18px;border-radius:50%;background:{clr};margin:0 auto 4px;'></div>
          <div style='font-size:11px;color:#e6edf3;'>{rng}</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MODEL COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  Model Comparison":
    import plotly.graph_objects as go

    st.markdown("""
    <div class="hero">
      <h1>📊 Model Comparison</h1>
      <p>LSTM vs GRU vs ConvLSTM — MAE, RMSE and R²</p>
    </div>""", unsafe_allow_html=True)

    models     = comparison_df["Model"].tolist()
    colors_map = {"LSTM":"#42a5f5","GRU":"#2ecc71","ConvLSTM":"#ffa726"}

    col1,col2,col3 = st.columns(3)
    for col, metric, title, lower in [
        (col1,"Overall_MAE","Mean Absolute Error",True),
        (col2,"Overall_RMSE","Root Mean Squared Error",True),
        (col3,"Overall_R2","R² Score",False),
    ]:
        vals   = comparison_df[metric].tolist()
        best_i = vals.index(min(vals)) if lower else vals.index(max(vals))
        fig = go.Figure(go.Bar(
            x=models, y=vals,
            marker_color=[colors_map.get(m,"#666") for m in models],
            marker_line_color=["gold" if i==best_i else "rgba(0,0,0,0)" for i in range(len(models))],
            marker_line_width=3,
            text=[f"{v:.4f}" for v in vals], textposition="outside",
            textfont=dict(color="#e6edf3", size=11)
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(color="#e6edf3",size=13)),
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font=dict(color="#e6edf3"), height=280,
            margin=dict(t=40,b=20,l=20,r=20),
            yaxis=dict(gridcolor="#30363d"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)")
        )
        col.plotly_chart(fig, use_container_width=True)

    best    = comparison_df.loc[comparison_df["Overall_RMSE"].idxmin(), "Model"]
    best_r2 = comparison_df.loc[comparison_df["Overall_RMSE"].idxmin(), "Overall_R2"]
    st.success(f"🏆 Best Model: **{best}** — Lowest RMSE with R² = {best_r2:.4f}")
    st.dataframe(comparison_df, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTED VS ACTUAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈  Predicted vs Actual":
    import plotly.graph_objects as go

    st.markdown("""
    <div class="hero">
      <h1>📈 Predicted vs Actual</h1>
      <p>Validate model accuracy against real historical observations</p>
    </div>""", unsafe_allow_html=True)

    counties   = sorted(df["county"].unique().tolist())
    default_i  = counties.index(user["home_county"]) if user["home_county"] in counties else 0
    col1,col2,col3 = st.columns(3)
    county_sel = col1.selectbox("County", counties, index=default_i)
    var_sel    = col2.selectbox("Variable", list(VAR_LABELS.values()))
    n_points   = col3.slider("Points", 30, 200, 90)

    var_col    = {v:k for k,v in VAR_LABELS.items()}[var_sel]

    with st.spinner("Loading validation data..."):
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        FEATURE_COLS = meta["feature_cols"]
        TARGET_COLS  = meta["target_cols"]
        LOOKBACK     = meta["lookback"]

        cdf = df[df["county"]==county_sel].copy().reset_index(drop=True)
        cdf = engineer_features(cdf)
        for c in FEATURE_COLS:
            if c not in cdf.columns:
                cdf[c] = 0.0

        scaler     = scalers[county_sel]
        scaled     = scaler.transform(cdf[FEATURE_COLS])
        target_idx = [FEATURE_COLS.index(t) for t in TARGET_COLS]
        var_i      = TARGET_COLS.index(var_col)
        n          = len(scaled)
        test_start = int(n * 0.85)
        actuals, preds = [], []

        for i in range(test_start, min(test_start+n_points, n-1)):
            X_in   = scaled[i-LOOKBACK:i].reshape(1, LOOKBACK, len(FEATURE_COLS))
            p_norm = model.predict(X_in, verbose=0)[0]
            dummy  = np.zeros((7, len(FEATURE_COLS)))
            dummy[:, target_idx] = p_norm
            inv    = scaler.inverse_transform(dummy)
            preds.append(inv[0, target_idx[var_i]])
            actuals.append(cdf.iloc[i][var_col])

        dates_plot = cdf.iloc[test_start:test_start+len(actuals)]["date"].tolist()

    mae  = mean_absolute_error(actuals, preds)
    rmse = np.sqrt(mean_squared_error(actuals, preds))
    r2   = r2_score(actuals, preds)

    m1,m2,m3 = st.columns(3)
    for col,val,lbl in [(m1,f"{mae:.4f}","MAE"),(m2,f"{rmse:.4f}","RMSE"),(m3,f"{r2:.4f}","R²")]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="val">{val}</div>
          <div class="lbl">{county_sel} · {var_sel} · {lbl}</div>
        </div>""", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates_plot, y=actuals, name="Actual",
        line=dict(color="#42a5f5",width=2), mode="lines"))
    fig.add_trace(go.Scatter(x=dates_plot, y=preds, name="Predicted",
        line=dict(color="#2ecc71",width=2,dash="dash"), mode="lines"))
    fig.update_layout(height=380, paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#e6edf3"), legend=dict(bgcolor="#0d1117"),
        xaxis=dict(gridcolor="#30363d"), yaxis=dict(gridcolor="#30363d",title=var_sel),
        margin=dict(t=20,b=20,l=20,r=20), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)