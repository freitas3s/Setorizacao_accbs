import streamlit as st

setores = st.Page("consoles.py" , title="Setorização ACC-BS")
supervisores = st.Page("supervisores.py" , title="Supervisores ACC-BS")

pg = st.navigation([setores, supervisores], position= "sidebar")

st.set_page_config(page_title="Setorização ACC-BS", layout="wide")
pg.run()