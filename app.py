import streamlit as st
from components.dataframe_viewer import render_dataframe_viewer
from components.main_component import render_main_component
from utils.data import load_data

# App title
st.set_page_config(layout="wide")
st.title("MTA Congestion Relief Zone (CRZ) Data Explorer")

# Load and cache dataset
if "filtered_df" not in st.session_state:
    df = load_data()
    st.session_state.df = df
    st.session_state.filtered_df = df
    st.session_state.df_history = []

# Define pages in our application
pg = st.navigation([
    st.Page("pages/1_Data_Explorer.py"),
    st.Page("pages/2_Top_Entries_Analytics.py"),
    st.Page("pages/3_Interactive_Map.py"),
    st.Page("pages/4_Vehicle_Timeseries.py"),
    st.Page("pages/5_Vehicle_Class_Breakdown.py"),
    st.Page("pages/8_Clustering_Labels.py"),
    st.Page("pages/7_Traffic_vs_Temperature.py"),
    st.Page("pages/6_Traffic_TS_Analysis.py")
])

# Add descriptions for each page
page_descriptions = {
    "pages/2_Top_Entries_Analytics.py": "View analytics for the top entries in the dataset.",
    "pages/3_Interactive_Map.py": "Visualize congestion data on an interactive map.",
    "pages/4_Vehicle_Timeseries.py": "Analyze vehicle trends over time using time series data.",
    "pages/5_Vehicle_Class_Breakdown.py": "Analyze vehicle data by class, comparing peak hours to overnight trends.",
    "pages/8_Clustering_Labels.py": "Explore clustering labels applied to the dataset to analyze changes in CRZ during peak and low-demand periods, comparing weekdays and weekends.",
    "pages/7_Traffic_vs_Temperature.py": "Analyze the relationship of CRZ, temperature, and precipitation in 3 dimensions.",
    "pages/6_Traffic_TS_Analysis.py": "Perform daily CRZ entries over time, categorized by weather conditions (Favorable, Unfavorable, Neutral), highlighting traffic volume trends and fluctuations.",
}

pg.run()