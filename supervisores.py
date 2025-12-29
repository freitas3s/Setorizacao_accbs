import streamlit as st
from setorizacao import regioes,setores
import sqlite3

def get_conn():
    return sqlite3.connect("setorizacao.db", check_same_thread=False)

def salvar_setorizacao(regiao, configuracao):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM setorizacao WHERE regiao = ?",
        (regiao,)
    )

    for ctr, setores in configuracao.items():
        for setor in setores:
            cur.execute("""
                INSERT INTO setorizacao (regiao, ctr, setor)
                VALUES (?, ?, ?)
            """, (regiao, ctr, setor))

    conn.commit()
    conn.close()


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
    if not st.session_state.configuracao:
        st.warning("Nenhuma alteração feita!")
    else:
        salvar_setorizacao(
            st.session_state.regiao,
            st.session_state.configuracao
        )
        st.success("Configuração salva com sucesso!")
