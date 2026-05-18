import streamlit as st
import plotly.express as px
from utils.data import load_data
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
import requests

df = st.session_state.df.copy()

# Ensure 'Toll Date' is datetime
df['Toll Date'] = pd.to_datetime(df['Toll Date'], format='%m/%d/%Y')

# Create enhanced features (traffic, calendar, weather) and run clustering (as before)
daily_volume = df.groupby('Toll Date')['CRZ Entries'].sum().rename('total_volume')
hourly_pivot = df.groupby(['Toll Date', 'Hour of Day'])['CRZ Entries'].sum().unstack(fill_value=0)

peak_hours = [7, 8, 9, 17, 18, 19]
peak_volume = hourly_pivot[peak_hours].sum(axis=1)
peak_ratio = peak_volume / daily_volume
hourly_std = hourly_pivot.std(axis=1)
growth_rate = daily_volume.pct_change().fillna(0)
is_weekend = (daily_volume.index.weekday >= 5).astype(int)

# Create features DataFrame
features_df = pd.DataFrame({
	'total_volume': daily_volume,
	'peak_ratio': peak_ratio,
	'hourly_std': hourly_std,
	'growth_rate': growth_rate,
	'is_weekend': is_weekend
})

# Perform clustering (as before)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features_df)

pca = PCA(n_components=0.95, random_state=42)
X_pca = pca.fit_transform(X_scaled)

kmeans = KMeans(n_clusters=2, random_state=42)
cluster_labels = kmeans.fit_predict(X_pca)
features_df['Cluster'] = cluster_labels

descriptive_labels = {0: "Weekday", 1: "Weekend/Low Demand"}
features_df['Pattern Type'] = features_df['Cluster'].map(descriptive_labels)

# Merge cluster labels with hourly traffic data
daily_pattern = df.groupby(['Toll Date', 'Hour of Day'])['CRZ Entries'].sum().unstack(fill_value=0)
daily_pattern_reset = daily_pattern.reset_index()
features_reset = features_df.reset_index()
merged_pattern = pd.merge(daily_pattern_reset, features_reset[['Toll Date', 'Cluster']], on='Toll Date', how='left')
merged_pattern.set_index('Toll Date', inplace=True)

# Group by cluster and calculate the average hourly traffic pattern
# Ensure hour columns are valid 0–23 and sorted
hour_cols = [col for col in merged_pattern.columns if isinstance(col, (int, float)) and 0 <= col <= 23]
hour_cols = sorted(hour_cols)
cluster_profiles_line = merged_pattern.groupby('Cluster')[hour_cols].mean()

# Convert to long format for Plotly
cluster_profiles_long = cluster_profiles_line.reset_index().melt(
	id_vars='Cluster', var_name='Hour of Day', value_name='Average CRZ Entries'
)
cluster_profiles_long['Pattern Type'] = cluster_profiles_long['Cluster'].map(descriptive_labels)
# Sanitize Hour of Day values (sometimes gets cast to float during melt)
cluster_profiles_long = cluster_profiles_long[
    cluster_profiles_long['Hour of Day'].between(0, 23)
]
cluster_profiles_long['Hour of Day'] = cluster_profiles_long['Hour of Day'].astype(int)

# Create an interactive Plotly line chart
fig = px.line(
	cluster_profiles_long,
	x='Hour of Day',
	y='Average CRZ Entries',
	color='Pattern Type',
	markers=True,
	labels={'Hour of Day': 'Hour of Day', 'Average CRZ Entries': 'Average CRZ Entries'},
	title='Average Daily Traffic Pattern by Enhanced Clusters',
)

# Customize hover information
fig.update_traces(hovertemplate='Hour: %{x}<br>CRZ Entries: %{y}<br>Pattern: %{text}',
					text=cluster_profiles_long['Pattern Type'])

# Update layout for better readability
fig.update_layout(
    xaxis=dict(
        tickmode='linear',
        tick0=0,
        dtick=1,
        range=[0, 23],  # 👈 Explicit x-axis bounds
        title='Hour of Day'
    ),
    yaxis_title='Average CRZ Entries',
    legend_title_text='Pattern Type',
    template='plotly_white',
	height = 600
)

# Display the interactive chart in Streamlit
st.plotly_chart(fig, use_container_width=True)