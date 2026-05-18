import streamlit as st
import plotly.graph_objects as go
from utils.data import load_data

df = st.session_state.df.copy()

# Filter by vehicle class
cars = df[df['Vehicle Class'] == '1 - Cars, Pickups and Vans']
trucks = df[df['Vehicle Class'].isin(['2 - Single-Unit Trucks', '3 - Multi-Unit Trucks'])]
motorcycles = df[df['Vehicle Class'] == '5 - Motorcycles']
taxis = df[df['Vehicle Class'] == 'TLC Taxi/FHV']

# Create the Plotly histogram
fig = go.Figure()

# Helper to add each trace with outlines
def add_histogram_trace(name, data):
    fig.add_trace(go.Histogram(
        x=data['Hour of Day'],
        y=data['CRZ Entries'],
        histfunc="sum",
        name=name,
        opacity=0.5,
        marker=dict(
            line=dict(width=1, color='black')  # ⬅️ Outline here
        )
    ))

add_histogram_trace("Cars", cars)
add_histogram_trace("Trucks (Lorries)", trucks)
add_histogram_trace("Motorcycles", motorcycles)
add_histogram_trace("Taxis", taxis)

# Customize layout
fig.update_layout(
    barmode='overlay',
    title="Weighted Vehicle Entries by Hour of Day",
    xaxis_title="Hour of Day",
    yaxis_title="Number of Entries (Weighted by CRZ Entries)",
    xaxis=dict(tickmode='linear', dtick=1),
    height=600
)

# Show chart in Streamlit
st.plotly_chart(fig, use_container_width=True)
