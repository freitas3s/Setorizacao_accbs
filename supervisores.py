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
if "configuracao" not in st.session_state:
    st.session_state.configuracao = {}


if not st.session_state.supervisor:
    st.title("Supervisores ACC-BS")

    regiao_selecionada = st.selectbox(
        "Selecione a Região:",
        options=["RRJ", "RSP", "RBR", "FIS"]
    )
    st.session_state.regiao = regiao_selecionada

    if st.button("Confirmar"):
        st.session_state.supervisor = True
        st.session_state.configuracao = {}
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

def selecionar_setor(console):
    setores_disponiveis = setores[st.session_state.regiao]

    return st.multiselect(
        "Selecione os Setores:",
        options=setores_disponiveis,
        key=f"setores_{console}"
    )


def salvar_estado(configuracao):
    with open(
        f"setorizacao_{st.session_state.regiao}.json",
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(configuracao, arquivo, ensure_ascii=False, indent=4)

if st.session_state.supervisor:

    consoles = regioes[st.session_state.regiao]
    cols = st.columns(len(consoles))

    for col, console in zip(cols, consoles):
        with col:
            st.subheader(f"CTR {console}")

            setores_selecionados = selecionar_setor(console)

            st.session_state.configuracao[f"CTR {console}"] = setores_selecionados

st.divider()

if st.button("Confirmar agrupamento"):
    if st.session_state.configuracao == {}:
        st.warning("Nenhuma alteração feita!")
        salvar_estado(st.session_state.configuracao)
        st.success("Configuração salva com sucesso!")