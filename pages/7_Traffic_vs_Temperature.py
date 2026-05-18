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

"""
Generates an interactive scatter plot of daily traffic volume vs. average temperature,
color-coded by weather categories, with an interactive trendline.
"""
API_KEY = "b1b230ed8664410080803403250504"
BASE_URL = "http://api.weatherapi.com/v1/history.json"

def fetch_weather(date_str, api_key=API_KEY, location="New York"):
	params = {
		"key": api_key,
		"q": location,
		"dt": date_str
	}
	response = requests.get(BASE_URL, params=params)
	if response.status_code == 200:
		data = response.json()
		forecast_day = data["forecast"]["forecastday"][0]["day"]
		return {
			"date": date_str,
			"avgtemp_c": forecast_day["avgtemp_c"],
			"avghumidity": forecast_day["avghumidity"],
			"totalprecip_mm": forecast_day["totalprecip_mm"],
			"condition": forecast_day["condition"]["text"]
		}
	else:
		return None

# Group traffic data by date
traffic_daily = df.groupby("Toll Date")["CRZ Entries"].sum().reset_index()
traffic_daily.rename(columns={"CRZ Entries": "daily_crz_entries"}, inplace=True)

# # Fetch weather data for unique dates
# unique_dates = traffic_daily["Toll Date"].unique()
# weather_records = []
# for date in unique_dates:
# 	weather_data = fetch_weather(date)
# 	if weather_data:
# 		weather_records.append(weather_data)

# # Create weather DataFrame
# weather_df = pd.DataFrame(weather_records)
# Cache weather data
weather_df = pd.read_csv("data/weather.csv")

# Merge traffic and weather data
merged_df = pd.merge(traffic_daily, weather_df, left_on="Toll Date", right_on="date", how="inner")

# Map weather conditions to categories
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

# Convert date column to datetime (if needed elsewhere)
merged_df['Toll Date'] = pd.to_datetime(merged_df['Toll Date'], format='%m/%d/%Y')
features = ["avgtemp_c", "totalprecip_mm", "condition"]

# Create interactive 3D scatter plot with a trendline
fig = px.scatter_3d(
	merged_df,
	x='avgtemp_c',
	y='totalprecip_mm',
	z='daily_crz_entries',
	color='weather_category',
	labels={
		"avgtemp_c": "Average Temperature (°C)",
		"totalprecip_mm": "Total Precipitation (mm)",
		"daily_crz_entries": "Daily CRZ Entries"
	},
	title="Daily Traffic Volume vs. Weather Conditions (3D)",
	template="plotly_white"
)

# Update marker style for better visualization
fig.update_traces(marker=dict(size=5, line=dict(width=0.5, color="black")))
fig.update_layout(height=800, legend_title_text="Weather Category", margin=dict(l=0, r=0, t=50, b=0))

# Display the plot in Streamlit
st.plotly_chart(fig)
