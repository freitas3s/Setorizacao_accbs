import streamlit as st
from setorizacao import regioes,fronteiras,setores
import sqlite3
from collections import defaultdict
from streamlit_autorefresh import st_autorefresh

def get_conn():
    return sqlite3.connect("setorizacao.db", check_same_thread=False)

def carregar_setorizacao(regiao):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT ctr, setor FROM setorizacao
        WHERE regiao = ?
    """, (regiao,))

    resultado = {}
    for ctr, setor in cur.fetchall():
        resultado.setdefault(ctr, []).append(str(setor))

    conn.close()
    return resultado



if  "console" not in st.session_state:
    st.session_state.console = None
if  "setores" not in st.session_state:
    st.session_state.setores = None
if  "regiao" not in st.session_state:
    st.session_state.regiao = None
if "confirmado" not in st.session_state:
    st.session_state.confirmado = False

if not st.session_state.confirmado:
    st.title("Setorização ACC-BS")
    regiao_selecionada = st.selectbox("Selecione a Regiao:", options=["RRJ", "RSP", "RBR", "FIS"])
    st.session_state.regiao = regiao_selecionada

    console_selecionado = st.selectbox("Selecione o Console:", options=regioes[regiao_selecionada],)
    st.session_state.console = console_selecionado
    ctr_selecionado = f"CTR {console_selecionado}"

    if st.button("Confirmar"):
        st.session_state.confirmado = True
        st.rerun()

else:
    setorizacao_atual = carregar_setorizacao(st.session_state.regiao)
    setores_ctr = setorizacao_atual[f"CTR {st.session_state.console}"] if f"CTR {st.session_state.console}" in setorizacao_atual else []

    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 150px; margin-bottom: 10px;">
                CTR {st.session_state.console}
            </h1>
            <p style="font-size: 72px;">
                {' · '.join(map(str, sorted(setores_ctr)))}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    def checar_fronteiras(setorizacao_atual, fronteiras, console_atual):
        ctr_atual = f"CTR {console_atual}"
        setores_console = setorizacao_atual.get(ctr_atual, [])

        setor_para_ctr = {
            setor: ctr
            for ctr, setores in setorizacao_atual.items()
            for setor in setores
        }

        resultado = {}

        for setor in setores_console:
            for fronteira in fronteiras.get(setor, []):
                if fronteira not in setores_console:
                    resultado[fronteira] = setor_para_ctr.get(fronteira, "Fechado")

        return dict(sorted(resultado.items()))


    fronteiras_ctr = checar_fronteiras(
        setorizacao_atual,
        fronteiras,
        st.session_state.console
    )


ctr_atual = f"CTR {st.session_state.console}"

fronteiras_agrupadas = defaultdict(list)

for setor, ctr in fronteiras_ctr.items():
    if ctr != ctr_atual:
        fronteiras_agrupadas[ctr].append(setor)

fronteiras_agrupadas = {
    ctr: sorted(setores)
    for ctr, setores in sorted(fronteiras_agrupadas.items())
    }


if not fronteiras_agrupadas:
    st.success("Nenhuma fronteira externa no momento.")
else:
    cols = st.columns(len(fronteiras_agrupadas))

    for col, (ctr, setores) in zip(cols, fronteiras_agrupadas.items()):
        with col:
            st.markdown(
                f"""
                <div style="
                    border: 2px solid #4F8BF9;
                    border-radius: 14px;
                    padding: 16px;
                    text-align: center;
                    min-height: 140px;
                ">
                    <h1 style="margin-bottom: 10px;">{ctr}</h1>
                    <p style="font-size: 40px;">
                                {' · '.join(map(str, setores))}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

st_autorefresh(interval=5000, key="refresh_console")
