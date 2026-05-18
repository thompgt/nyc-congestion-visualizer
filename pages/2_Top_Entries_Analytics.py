import streamlit as st
import plotly.express as px
from utils.data import load_data

df = st.session_state.df.copy()

top_groups = df.groupby("Detection Group")["CRZ Entries"].sum().sort_values(ascending=False).head(10).reset_index()

fig = px.bar(
    top_groups,
    x="CRZ Entries",
    y="Detection Group",
    orientation="h",
    title="Top 10 Detection Groups by Total CRZ Entries",
    height=600
)

st.plotly_chart(fig, use_container_width=True)