import streamlit as st
import plotly.express as px
from utils.data import load_data

df = st.session_state.df.copy()

# Group by Time Period and Vehicle Class
grouped = df.groupby(["Time Period", "Vehicle Class"])["CRZ Entries"].sum().reset_index()

# Rename vehicle classes
vehicle_class_map = {
    "TLC Taxi/FHV": "TLC Taxi/FHV",
    "5 - Motorcycles": "Motorcycles",
    "4 - Buses": "Buses",
    "3 - Multi-Unit Trucks": "Trucks (Multi)",
    "2 - Single-Unit Trucks": "Trucks (Single)",
    "1 - Cars, Pickups and Vans": "Cars, Pickups, Vans"
}
grouped["Vehicle Class"] = grouped["Vehicle Class"].map(vehicle_class_map)

# Pivot to get proportions
pivot = grouped.pivot(index="Vehicle Class", columns="Time Period", values="CRZ Entries").fillna(0)
pivot_prop = pivot.div(pivot.sum(axis=1), axis=0)  # Normalize across rows
pivot_prop = pivot_prop.reset_index()

# Melt to long form for Plotly
melted = pivot_prop.melt(id_vars="Vehicle Class", var_name="Time Period", value_name="Proportion")

# Plot as side-by-side bars
fig = px.bar(
    melted,
    x="Vehicle Class",
    y="Proportion",
    color="Time Period",
    barmode="group",  # 👈 side-by-side
    title="Proportion of CRZ Entries by Time Period for Each Vehicle Class",
    color_discrete_map={
        "Peak": "#FF5733",
        "Overnight": "#3498DB"
    },
    height=600
)

fig.update_layout(
    xaxis_title="Vehicle Class",
    yaxis_title="Proportion of Total CRZ Entries",
    legend_title="Time Period"
)

st.plotly_chart(fig, use_container_width=True)
