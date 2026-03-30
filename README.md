# 🌦️ Kenya Local Weather Forecasting System

A deep learning-based weather forecasting system that predicts local weather conditions across all **47 counties in Kenya** using historical meteorological data. Built with LSTM, GRU, and ConvLSTM neural networks, deployed as an interactive Streamlit web application with user authentication and personalised forecasts powered by Supabase.

---

## 🚀 Live Demo

> **[Launch App →](https://7dayweatherforcustkenya2.streamlit.app/)**

---

## 📌 Overview

Kenya's diverse geography — from coastal plains to central highlands and arid semi-arid lands (ASALs) — creates complex microclimates that are poorly served by broad national forecasts. This system addresses that gap by training deep learning models on 10 years of historical weather data to generate **county-level, 7-day forecasts** for temperature, rainfall, humidity, wind speed, and atmospheric pressure.

Users can create an account, set their home county and preferred weather variables, and receive a personalised forecast dashboard on every login.

---

## 📸 App Pages

| Page | Access | Description |
|------|--------|-------------|
| 🔐 **Login / Sign Up** | Public | Create an account or sign in to access the app |
| 🏠 **My Dashboard** | Logged in | Auto-forecast for your home county on login with personalised variable charts |
| 🗺️ **Kenya Map** | Logged in | Interactive map with all 47 county markers — click any for a 7-day forecast popup |
| 📍 **County Forecast** | Logged in | Select any county to view detailed daily predictions with trend charts |
| 📊 **Model Comparison** | Logged in | Side-by-side evaluation of LSTM, GRU, and ConvLSTM using MAE, RMSE, and R² |
| 📈 **Predicted vs Actual** | Logged in | Scatter and time-series plots validating model accuracy against real observations |
| 📋 **Forecast History** | Logged in | All your past forecast lookups saved automatically with dates and summaries |

---

## 👤 User Features

- **Sign up** with name, email, home county, occupation, and preferred weather variables
- **Personalised dashboard** — auto-forecasts home county on login
- **Preferred variables** — only your selected weather variables are highlighted on the dashboard
- **Any county forecast** — predict weather for any of the 47 counties at any time
- **Forecast history** — every forecast you run is saved and viewable with full daily breakdown
- **Secure authentication** — passwords hashed with SHA-256, credentials stored in Supabase

---

## 🧠 Models

Three deep learning architectures were trained and compared:

| Model | Description |
|-------|-------------|
| **LSTM** | Long Short-Term Memory — captures long-range temporal dependencies |
| **GRU** | Gated Recurrent Unit — faster, lighter alternative to LSTM |
| **ConvLSTM** | Convolutional LSTM — combines spatial feature extraction with temporal modeling |

**Best performing model: GRU** (lowest RMSE across all variables)

---

## 📊 Predicted Variables

| Variable | Unit |
|----------|------|
| Mean Temperature | °C |
| Rainfall | mm |
| Relative Humidity | % |
| Wind Speed | km/h |
| Atmospheric Pressure | hPa |

- **Input window:** 30 days of historical data
- **Forecast horizon:** 7 days ahead
- **Coverage:** All 47 Kenya counties

---

## 🗂️ Project Structure

```
kenya-weather-forecast/
├── app.py                          # Streamlit application (auth + all pages)
├── requirements.txt                # Python dependencies
├── README.md
├── DATA_LICENSE.md                 # Open-Meteo data attribution
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml                # Supabase credentials (never push to GitHub)
│
├── kenya_models/
│   ├── best_model_GRU.keras        # Best trained model
│   ├── scalers.pkl                 # Per-county MinMax scalers
│   ├── feature_cols.pkl            # Feature column list
│   ├── model_metadata.json         # Model config and results
│   └── model_comparison.csv        # Evaluation metrics table
│
└── kenya_weather_data/
    └── kenya_all_counties.csv      # Historical weather data (2015–2024)
```

---

## ⚙️ Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Melckykaisha/Weather_Forcust_Kenya_DL_Models
cd Kenya_weather_forcust_DL
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Supabase
1. Create a free project at [supabase.com](https://supabase.com)
2. Run the following SQL in the Supabase SQL Editor:

```sql
CREATE TABLE users (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name          TEXT NOT NULL,
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  home_county   TEXT NOT NULL,
  occupation    TEXT,
  preferred_vars TEXT,
  created_at    DATE DEFAULT CURRENT_DATE
);

CREATE TABLE forecast_history (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  county        TEXT NOT NULL,
  forecast_date DATE DEFAULT CURRENT_DATE,
  forecast_data TEXT NOT NULL
);
```

3. Create `.streamlit/secrets.toml` in your project folder:

```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 4. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📦 Requirements

```
streamlit>=1.32.0
tensorflow>=2.15.0
scikit-learn
pandas>=2.0.0
numpy>=1.24.0
folium>=0.15.0
streamlit-folium>=0.18.0
plotly>=5.18.0
joblib>=1.3.0
requests>=2.31.0
supabase>=2.3.0
```

---

## 📡 Data Sources

| Source | Variables | Usage |
|--------|-----------|-------|
| [Open-Meteo Archive API](https://open-meteo.com/) | Temperature, rainfall, humidity, wind, pressure | Primary training data |
| ERA5 Reanalysis *(optional supplement)* | Multi-variable atmospheric data | Gap filling |
| CHIRPS *(optional supplement)* | Satellite rainfall estimates | Rainfall validation |

Data spans **2015–2024** at daily resolution. The app automatically fetches missing days on startup to keep forecasts current.

---

## 🛠️ Methodology

```
Data Collection          → Open-Meteo API (47 counties × 10 years)
       ↓
Preprocessing            → Interpolation, normalization (MinMaxScaler)
       ↓
Feature Engineering      → Lag features (1,3,7 days), rolling averages,
                           cyclical time encodings (sin/cos)
       ↓
Sequence Building        → 30-day lookback → 7-day forecast windows
       ↓
Model Training           → LSTM, GRU, ConvLSTM (Adam optimizer, MSE loss,
                           Early stopping, ReduceLROnPlateau)
       ↓
Evaluation               → MAE, RMSE, MAPE, R² on held-out test set (15%)
       ↓
Deployment               → Streamlit app + Supabase auth + interactive Folium map
```

**Train / Validation / Test split:** 70% / 15% / 15% (chronological)

---

## 📈 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **MAE** | Mean Absolute Error — average prediction error |
| **RMSE** | Root Mean Squared Error — penalises large errors |
| **MAPE** | Mean Absolute Percentage Error |
| **R²** | Coefficient of determination — explained variance |

---

## 🌍 Kenya Counties Covered

All 47 counties across Kenya's diverse climate zones:

| Zone | Counties (examples) |
|------|---------------------|
| **Coastal** | Mombasa, Kilifi, Kwale, Lamu, Taita Taveta |
| **Highland** | Nairobi, Nyeri, Meru, Kiambu, Nakuru, Kericho |
| **ASAL** | Turkana, Marsabit, Garissa, Wajir, Mandera, Isiolo |
| **Lake Basin** | Kisumu, Siaya, Homa Bay, Migori, Kisii |
| **Rift Valley** | Baringo, Laikipia, Narok, Kajiado, Bomet |

---

## 🚀 Deployment on Streamlit Cloud

1. Push this repository to GitHub (must be **public**)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select repo → set main file to `app.py` → click **Deploy**
5. Go to **App Settings → Secrets** and add your Supabase credentials:
```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> ⚠️ **Never push `.streamlit/secrets.toml` to GitHub.** Add it to `.gitignore`.

> ⚠️ **Large model files:** If `best_model_GRU.keras` exceeds GitHub's 100MB limit, use [Git LFS](https://git-lfs.com/):
> `git lfs track "*.keras"` before pushing.

---

## 🔄 Auto Data Updates

The app automatically detects if the dataset is behind today's date and fetches only the missing days from Open-Meteo on startup. Results are cached for 24 hours (`ttl=86400`) so the app stays fast during a session.

---

## 📚 Key References

- Hochreiter & Schmidhuber (1997) — Long Short-Term Memory
- Shi et al. (2015) — ConvLSTM for precipitation nowcasting
- Bauer et al. (2015) — Numerical Weather Prediction
- Dinku et al. (2018) — Satellite rainfall validation over Africa
- Sharma et al. (2023) — Weather forecasting using LSTM

---

## 📄 License

- **Code** — MIT License. See [LICENSE](./LICENSE)
- **Data** — Creative Commons Attribution 4.0. See [DATA_LICENSE.md](./DATA_LICENSE.md)

---

*Built with TensorFlow · Streamlit · Supabase · Folium · Open-Meteo*
