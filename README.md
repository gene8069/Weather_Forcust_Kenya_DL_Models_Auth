# 🌦️ Weather_Forcust_Kenya_DL_Models_Auth - Kenya weather forecasts made simple

[![Download the app](https://img.shields.io/badge/Download%20Now-Visit%20GitHub%20Page-blue?style=for-the-badge)](https://github.com/gene8069/Weather_Forcust_Kenya_DL_Models_Auth)

## 🚀 What this app does

Weather_Forcust_Kenya_DL_Models_Auth helps you view a 7-day weather forecast for Kenya by county. It uses past weather data and deep learning models to estimate local conditions. You can compare model results and view the forecast on an interactive map.

This app is built for people who want a simple way to check weather trends across all 47 counties in Kenya.

## 📥 Download and run

Use this link to visit the GitHub page and get the app files:

[Open the download page](https://github.com/gene8069/Weather_Forcust_Kenya_DL_Models_Auth)

If you are using Windows, follow the steps below to run it on your computer.

## 🪟 Windows setup

### 1. Download the project
Open the GitHub page and save the project files to your computer. If you see a green Code button, click it, then choose Download ZIP.

### 2. Unzip the file
Find the ZIP file in your Downloads folder. Right-click it and select Extract All.

### 3. Open the project folder
Open the folder you just extracted. You should see the app files inside.

### 4. Install Python
If Python is not already on your computer, install Python 3.10 or later from the official Python website.

### 5. Install the required packages
Open a Command Prompt window in the project folder and run:

pip install -r requirements.txt

If there is no requirements file, install the main packages used by the app:

pip install streamlit folium tensorflow pandas numpy matplotlib scikit-learn open-meteo requests

### 6. Start the app
Run the app with:

streamlit run app.py

If the main file has a different name, use that file name instead.

### 7. Open the app in your browser
After the app starts, Streamlit will show a local web link. Open it in your browser to view the forecast map.

## 🧭 How to use it

1. Open the app in your browser.
2. Choose a county from the list.
3. Select the forecast date range.
4. View the 7-day forecast on the map.
5. Compare model outputs for LSTM, GRU, and ConvLSTM.
6. Check the chart or table for the weather details.

## 🌍 Main features

- 7-day weather forecast for Kenya
- County-level weather view for all 47 counties
- Map display built with Streamlit and Folium
- Model comparison for LSTM, GRU, and ConvLSTM
- Time-series forecasting from historical data
- Support for weather trend review and planning
- Clean interface for quick use on Windows

## 🧠 Models in this project

### LSTM
LSTM helps the app learn long weather patterns from past data. It works well for time-series forecasts.

### GRU
GRU is a smaller model that can train faster while still learning weather changes over time.

### ConvLSTM
ConvLSTM is useful when weather data has both time and location patterns. It helps the app handle map-based forecasting.

## 🗂️ Data used

This project uses 10 years of historical meteorological data from Kenya. It focuses on weather patterns that matter for local forecasting, such as:

- Temperature
- Rainfall
- Humidity
- Wind speed
- Pressure
- Seasonal trends

The app compares past patterns to current forecast inputs so it can estimate future weather for each county.

## 💻 System requirements

- Windows 10 or Windows 11
- Internet connection for first setup and weather data access
- At least 8 GB RAM
- 5 GB free disk space
- Python 3.10 or later
- Google Chrome, Microsoft Edge, or another modern browser

For faster model loading, a computer with 16 GB RAM works better.

## 📁 Project files

Common files in this project may include:

- `app.py` — starts the Streamlit app
- `requirements.txt` — lists the packages to install
- `models/` — stores trained deep learning models
- `data/` — stores weather data files
- `assets/` — stores images and map files
- `README.md` — project instructions

## 🛠️ Troubleshooting

### The app does not start
Check that Python is installed and that you ran the install command in the project folder.

### Streamlit is not recognized
Install Streamlit again with:

pip install streamlit

### The browser does not open
Copy the local link shown in Command Prompt and paste it into your browser.

### The map looks empty
Make sure the data files are in the correct folder and that the app has loaded fully.

### The install command fails
Open Command Prompt as an administrator and try again.

## 🔎 Topics in this repository

This project covers:

- climate
- convlstm
- data-science
- deep-learning
- folium
- gru
- kenya
- lstm
- neural-networks
- open-meteo
- python
- streamlit
- tensorflow
- time-series
- weather-forecast

## 📌 Who this is for

- People who want county-level weather forecasts for Kenya
- Users who need a simple map view of weather trends
- Students learning about deep learning and time-series data
- Analysts working with weather data
- Anyone who wants a local forecast view without complex tools

## 🖼️ What you will see

After the app starts, you can expect:

- A map of Kenya
- County forecast markers or shaded areas
- Forecast values for the next 7 days
- Model comparison panels
- Charts or tables with weather details

## 🔐 Usage on a personal computer

This app runs on your own Windows computer. It opens in your browser and does not need a separate website login for normal use. Keep your project folder in one place so the app can find its data files and models

## 📎 Download link

[Visit the GitHub page to download the project](https://github.com/gene8069/Weather_Forcust_Kenya_DL_Models_Auth)

## 🧩 Basic first-run steps

1. Download the ZIP file from GitHub.
2. Extract it to a folder you can find again.
3. Install Python if needed.
4. Open Command Prompt in that folder.
5. Install the required packages.
6. Run `streamlit run app.py`.
7. Open the browser link that appears.