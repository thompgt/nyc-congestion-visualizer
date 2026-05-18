import streamlit as st
import plotly.express as px
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from utils.data import load_data
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

df = st.session_state.df.copy()

# --------------------------------------
# Weather API & Visual Analysis
# --------------------------------------
API_KEY = "b1b230ed8664410080803403250504"
BASE_URL = "http://api.weatherapi.com/v1/history.json"

def fetch_weather(date_str, api_key=API_KEY, location="New York"):
	params = {
		"key": api_key,
		"q": location,
		"dt": date_str
	}
	response = requests.get(BASE_URL, params=params)
	data = response.json()
	forecast_day = data["forecast"]["forecastday"][0]["day"]
	return {
		"date": date_str,
		"avgtemp_c": forecast_day["avgtemp_c"],
		"avghumidity": forecast_day["avghumidity"],
		"totalprecip_mm": forecast_day["totalprecip_mm"],
		"condition": forecast_day["condition"]["text"]
	}

traffic_daily = df.groupby("Toll Date")["CRZ Entries"].sum().reset_index()
traffic_daily.rename(columns={"CRZ Entries": "daily_crz_entries"}, inplace=True)

# unique_dates = traffic_daily["Toll Date"].unique()
# weather_records = []
# for date in unique_dates:
# 	try:
# 		weather_data = fetch_weather(date)
# 		weather_records.append(weather_data)
# 	except Exception as e:
# 		print(f"Failed to fetch weather for {date}: {e}")
# weather_df = pd.DataFrame(weather_records)

# Cache weather data
weather_df = pd.read_csv("data/weather.csv")
merged_df = pd.merge(traffic_daily, weather_df, left_on="Toll Date", right_on="date", how="inner")

# --- Bundle Weather Conditions into Categories ---
weather_category_map = {
	"Sunny": "Favorable",
	"Clear": "Favorable",
	"Partly cloudy": "Favorable",
	"Overcast": "Neutral",
	"Cloudy": "Neutral",
	"Patchy rain possible": "Neutral",
	"Light rain": "Neutral",
	"Light freezing rain": "Neutral",
	"Heavy rain": "Unfavorable",
	"Heavy rain at times": "Unfavorable",
	"Moderate or heavy rain shower": "Unfavorable",
	"Moderate rain": "Unfavorable",
	"Moderate rain at times": "Unfavorable",
	"Moderate or heavy snow showers": "Unfavorable",
	"Patchy moderate snow": "Unfavorable",
	"Moderate snow": "Unfavorable"
}
merged_df["weather_category"] = merged_df["condition"].apply(lambda cond: weather_category_map.get(cond, "Neutral"))

features = ["avgtemp_c", "avghumidity", "totalprecip_mm", "condition"]
X = merged_df[features]
y = merged_df["daily_crz_entries"]

preprocessor = ColumnTransformer(transformers=[
	("cat", OneHotEncoder(), ["condition"])
], remainder="passthrough")

pipeline = Pipeline(steps=[
	("preprocessor", preprocessor),
	("regressor", LinearRegression())
])
pipeline.fit(X, y)

model = pipeline.named_steps["regressor"]
feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
coefficients = dict(zip(feature_names, model.coef_))
r_squared = pipeline.score(X, y)

# ---------------------------
# Visual Analysis: Powerful Graphs for Weather & Traffic Variability
# ---------------------------
# Make sure date column is in datetime format
merged_df['Toll Date'] = pd.to_datetime(merged_df['Toll Date'], format='%m/%d/%Y')

# Create the base figure
fig = go.Figure()

# Add line trace for total daily traffic (gray line)
fig.add_trace(go.Scatter(
    x=merged_df['Toll Date'],
    y=merged_df['daily_crz_entries'],
    mode='lines',
    name='Daily Traffic',
    line=dict(color='gray'),
))

# Add scatter markers for weather categories (color-coded)
for weather_type in merged_df['weather_category'].unique():
    weather_data = merged_df[merged_df['weather_category'] == weather_type]
    fig.add_trace(go.Scatter(
        x=weather_data['Toll Date'],
        y=weather_data['daily_crz_entries'],
        mode='markers',
        name=weather_type,
        marker=dict(size=8, line=dict(width=1, color='black')),
    ))

# Layout styling
fig.update_layout(
    title="Daily Traffic Volume Over Time (Weather Categories)",
    xaxis_title="Date",
    yaxis_title="Daily CRZ Entries",
    legend_title="Weather Category",
    height=600,
    margin=dict(r=30)
)

# Show in Streamlit
st.plotly_chart(fig, use_container_width=True)