import streamlit as st
from setorizacao import regioes

if  "console" not in st.session_state:
    st.session_state.console = None
if  "setores" not in st.session_state:
    st.session_state.setores = None
if  "regiao" not in st.session_state:
    st.session_state.regiao = None
if "confirmado" not in st.session_state:
    st.session_state.confirmado = False

if not st.session_state.confirmado:
    regiao_selecionada = st.selectbox("Selecione a Regiao:", options=["RRJ", "RSP", "RBR", "FIS"])
    st.session_state.regiao = regiao_selecionada

    console_selecionado = st.selectbox("Selecione o Console:", options=regioes[regiao_selecionada])
    st.session_state.console = console_selecionado


    if st.button("Confirmar"):
        st.session_state.confirmado = True
        st.rerun()

else:
        st.markdown(
        f"""
        <h1 style='text-align: center; font-size: 300px;'>
            CTR {st.session_state.console}
        </h1>
        """,
        unsafe_allow_html=True
    )