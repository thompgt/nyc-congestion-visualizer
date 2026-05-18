import streamlit as st
import plotly.express as px
from utils.data import load_data
import folium
import polars as pl
import json
import pandas as pd
from streamlit_folium import st_folium, folium_static
import base64
from io import BytesIO
import matplotlib.pyplot as plt
def generate_timeseries_plot(detection_group: str, df: pl.DataFrame) -> str:
    """Generate a base64-encoded time series plot for a given detection group."""
    try:
        # Filter and group data by date
        df_filtered = df.filter(pl.col("Detection Group") == detection_group)
        df_grouped = (
            df_filtered
            .group_by("Toll Date")
            .agg(pl.sum("CRZ Entries").alias("Total Entries"))
            .sort("Toll Date")
        )

        # Convert to pandas for plotting
        df_pd = df_grouped.to_pandas()
        df_pd["Toll Date"] = pd.to_datetime(df_pd["Toll Date"])

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.plot(df_pd["Toll Date"], df_pd["Total Entries"], color="#2980b9", marker='o', linewidth=1)
        ax.set_title(f"{detection_group}", fontsize=10)
        ax.tick_params(axis='x', labelrotation=45)
        ax.set_ylabel("Entries")
        ax.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()

        # Convert plot to base64 image
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{image_base64}" width="750">'
    except Exception as e:
        return f"<p>Error generating plot: {e}</p>"

@st.cache_data
def load_location_coords():
    """Load location coordinates from detection_groups.json."""
    try:
        with open("data/detection_groups.json", "r") as f:
            location_coords = json.load(f)

        location_df = pl.DataFrame(
            {
                "Detection Group": list(location_coords.keys()),
                "Latitude": [v[0] for v in location_coords.values()],
                "Longitude": [v[1] for v in location_coords.values()],
            }
        )
        return location_df
    except Exception as e:
        st.error(f"Error loading location coordinates: {e}")
        return None


@st.cache_data
def preprocess_map_data(df, location_df):
    """Merge data with location coordinates and filter valid entries."""
    try:
        if not isinstance(df, pl.DataFrame):
            df = pl.from_pandas(df)

        df_merged = df.join(location_df, on="Detection Group", how="left")
        df_map = df_merged.filter(
            df_merged["Latitude"].is_not_null() & df_merged["Longitude"].is_not_null()
        )
        return df_map
    except Exception as e:
        st.error(f"Error preprocessing map data: {e}")
        return None

def generate_interactive_map(aggregated_data, style='Light'):
    """Render a folium map with CRZ markers and customizable tile style."""

    tile_styles = {
        'Satellite': {
            'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'attr': 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, etc.'
        },
        'Light': {
            'tiles': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            'attr': '&copy; <a href="https://carto.com/">CARTO</a>'
        },
        "Dark": {
            "tiles": "https://cartodb-basemaps-a.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
            "attr": "© OpenStreetMap contributors © CARTO"
        },
        'Standard': {
            'tiles': 'OpenStreetMap',
            'attr': None
        }
    }

    if style not in tile_styles:
        raise ValueError(f"Invalid map style: {style}. Choose from 'satellite', 'white', or 'regular'.")

    selected_style = tile_styles[style]

    m = folium.Map(
        location=[40.7385, -73.9422],
        zoom_start=13.2,
        tiles=selected_style['tiles'],
        attr=selected_style['attr'],
        width='100%',        # or a fixed size like '1200px'
        height='1000px',       # increase this for taller map
        radius=10,
    )


    for _, row in aggregated_data.iterrows():
        if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
            group_name = row["Detection Group"]
            time_series_img = generate_timeseries_plot(group_name, df_map)
            popup_html = f"""
            <div style="width: 770px; font-family: 'Helvetica Neue', sans-serif; font-size: 14px;">
                <b style="color: #2c3e50;">{group_name}</b><br>
                <span style="color: #2c3e50;">Total CRZ Entries:</span> <b>{row['CRZ Entries']}</b><br><br>
                {time_series_img}
            </div>
            """
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=folium.Popup(popup_html, max_width=770),
                icon=folium.Icon(color="blue", icon="car", prefix="fa")
            ).add_to(m)

    return m

st.write("### Interactive Map")
df = st.session_state.df.copy()

with st.container():
    location_df = load_location_coords()
    if location_df is None:
        st.error("Failed to load location coordinates.")
    else:
        with st.container():
            location_df = load_location_coords()
            if location_df is None:
                st.error("Failed to load location coordinates.")
            else:
                df_map = preprocess_map_data(df, location_df)
                if df_map is None or df_map.is_empty():
                    st.error("No valid data available for the map.")
                else:
                    df_map_pandas = df_map.to_pandas()

                    aggregated_data = (
                        df_map_pandas.groupby(["Latitude", "Longitude", "Detection Group"])["CRZ Entries"]
                        .sum()
                        .reset_index()
                    )

                    # Layout: selectbox and centered map
                    style_choice = st.selectbox(
                        "Choose map style:",
                        ["Light", "Dark","Satellite", "Standard"],
                        key="map_style_selector"
                    )

                    m = generate_interactive_map(aggregated_data, style=style_choice)

                    # Center the layout and show the map
                    col1, col2, col3 = st.columns([0.1, 1.8, 0.1])
                    with col2:
                        st_folium(m, width=1500, height=850)
