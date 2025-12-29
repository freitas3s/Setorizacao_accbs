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

def console_pronto():
    return (
        st.session_state.modo_operacional
        and st.session_state.regiao is not None
        and st.session_state.console is not None
    )

if  "console" not in st.session_state:
    st.session_state.console = None
if  "regiao" not in st.session_state:
    st.session_state.regiao = None
if "modo_operacional" not in st.session_state:
    st.session_state.modo_operacional = False

if not st.session_state.modo_operacional:
    st.title("Entrada Operacional ACC-BS")

    st.selectbox(
        "Selecione a Região:",
        ["RRJ", "RSP", "RBR", "FIS"],
        key="regiao"
    )

    st.selectbox(
        "Selecione o Console:",
        regioes.get(st.session_state.regiao, []),
        key="console"
    )

    if st.button("Entrar no modo operacional"):
        if st.session_state.regiao and st.session_state.console:
            st.session_state.modo_operacional = True
            st.rerun()
        else:
            st.warning("Selecione região e console")

if console_pronto():
    setorizacao_atual = carregar_setorizacao(st.session_state.regiao)
    for console in regioes[st.session_state.regiao]:
        setorizacao_atual.setdefault(f"CTR {console}", [])

    setores_ctr = setorizacao_atual[f"CTR {st.session_state.console}"] if f"CTR {st.session_state.console}" in setorizacao_atual else []
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 150px; margin-bottom: 10px;">
                CTR {st.session_state.console}
            </h1>
            <p style="font-size: 72px; color: #999;">
                { ' · '.join(sorted(setores_ctr)) if setores_ctr else "Sem setores alocados" }
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    @st.cache_data(ttl=5)
    def carregar_todas_regioes():
        mapa_global = {}    

        for regiao in ["RRJ", "RSP", "RBR", "FIS"]:
            setorizacao = carregar_setorizacao(regiao)

            for ctr, setores in setorizacao.items():
                for setor in setores:
                    mapa_global[setor] = f"{ctr} ({regiao})"

        return mapa_global

    def checar_fronteiras(setorizacao_atual, fronteiras, console_atual):
        ctr_atual = f"CTR {console_atual}"
        setores_console = setorizacao_atual.get(ctr_atual, [])

        mapa_global = carregar_todas_regioes()

        resultado = {}

        for setor in setores_console:
            for fronteira in fronteiras.get(setor, []):
                if fronteira not in setores_console:
                    # sempre usa o mapa global
                    resultado[fronteira] = mapa_global.get(
                        fronteira,
                        "Desconhecido"
                    )

        return dict(sorted(resultado.items()))

    fronteiras_ctr = checar_fronteiras(
        setorizacao_atual,
        fronteiras,
        st.session_state.console
    )


    ctr_atual = f"CTR {st.session_state.console}"

    fronteiras_agrupadas = defaultdict(list)

    for setor, ctr in fronteiras_ctr.items():
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
    

st_autorefresh(interval=10000, key="auto_refresh")  # Atualiza a cada 60 segundos

