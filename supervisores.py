import streamlit as st
import json
from setorizacao import regioes,setores

if "console_selecionado" not in st.session_state:
    st.session_state.console_selecionado = None
if "agrupamento_selecionado" not in st.session_state:
    st.session_state.agrupamento_selecionado = []
if "supervisor" not in st.session_state:
    st.session_state.supervisor = False
if "regiao" not in st.session_state:
    st.session_state.regiao = None



def salvar_estado(estado= st.session_state.regiao):

    with open("estado.json", "w") as f:
        json.dump(estado, f)

def carregar_estado():
    try:
        with open("estado.json", "r") as f:
            estado = json.load(f)
    except FileNotFoundError:
        estado = {}
    return estado


if not st.session_state.supervisor:
    st.title("Supervisores ACC-BS")
    regiao_selecionada = st.selectbox("Selecione a Regiao:", options=["RRJ", "RSP", "RBR", "FIS"])
    st.session_state.regiao = regiao_selecionada

    if st.button("Confirmar"):
        st.session_state.supervisor = True
        
        st.rerun()
else:
    st.markdown(
        f"""
        <h1 style='text-align: center; font-size: 100px;'>
            Supervisor {st.session_state.regiao}
        </h1>
        """,
        unsafe_allow_html=True
    )


