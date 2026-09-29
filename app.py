import streamlit as st

from ui.drive import render


st.set_page_config(
    page_title="AI Drive",
    page_icon="📁",
    layout="wide",
)

render()