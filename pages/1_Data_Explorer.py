import streamlit as st
from components.dataframe_viewer import render_dataframe_viewer
from components.main_component import render_main_component
from utils.data import load_data

# Home page layout
render_dataframe_viewer()
render_main_component()