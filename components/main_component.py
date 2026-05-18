import os
import streamlit as st
from components.pandas_component import render_pandas_component
from components.visualization_component import render_visualization_component
from components.qna_component import render_qna_component


def render_main_component():
    st.markdown("---")
    mode = st.radio("Choose what you want to do:", ["Pandas Filter Query", "Generate a Visualization", "Q&A"], key="mode_selector", horizontal=True)

    # Mode selection
    if mode == "Pandas Filter Query":
        render_pandas_component()
    elif mode == "Generate a Visualization":
        render_visualization_component()
    elif mode == "Q&A":
        render_qna_component()
