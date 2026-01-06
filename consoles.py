import streamlit as st
from setorizacao import regioes,fronteiras,setores,setores_chegadas,nref
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

def calcular_nref(regiao, setores_console, nref):

    if not setores_console:
        return None

    tabela_regiao = nref.get(regiao)
    if not tabela_regiao:
        return None

    if f"{regiao} AGRUPADO" in setores_console:
        return tabela_regiao.get(f"{regiao} AGRUPADO")
    setores_norm = sorted(setores_console)
    chave = "/".join(setores_norm)
    if chave in tabela_regiao:
        return tabela_regiao[chave]
    return tabela_regiao.get("DEMAIS")


def setores_app(setor, regiao):

    setor = str(setor)

    if regiao == "RBR":
        return setores_app.get(setor, setor)

    return setor

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
    regiao_selecionada = st.selectbox("Selecione a Regiao:", options=["RRJ", "RSP", "RBR","APP"])
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
    st.write(setores_ctr)
    nref_valor = calcular_nref(
    st.session_state.regiao,
    setores_ctr,
    nref)

    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: -30px; margin-top: -100px">
            <h1 style="font-size: 200px; margin-bottom: -50px;">
                CTR {st.session_state.console}
            </h1>
            <p style="font-size: 200px;">
                {' · '.join(map(str, sorted(setores_ctr)))} 
            </p>
        </div>
        """,

        unsafe_allow_html=True
    )
    if nref_valor:
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: -50px;">
                <p style="font-size: 48px; color: #ffffff;">
                    Nref/Pico {nref_valor}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    def carregar_todas_regioes():
        mapa_global = {}    

        for regiao in ["RRJ", "RSP", "RBR"]:
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
                    if fronteira in mapa_global:
                        resultado[fronteira] = mapa_global[fronteira]

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
#bloco app
    if st.session_state.regiao == "APP":
            def nome_setor_app_br(setor):
                setor = str(setor)
                nome = setores_chegadas.get(setor)
                if nome:
                    return f"{nome}"
                return setor
            fronteiras_ctr = checar_fronteiras(
            setorizacao_atual,
            fronteiras,
            st.session_state.console
            )
            cols = st.columns(len(fronteiras_agrupadas))

            for col, (ctr, setores) in zip(cols, fronteiras_agrupadas.items()):
                with col:
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid #7B1FA2;
                            border-radius: 18px;
                            padding: 20px;
                            text-align: center;
                            min-height: 100px;
                        ">
                            <h2>{ctr}</h2>
                            <p style="font-size: 38px; font-weight: 600;">
                                {' · '.join(nome_setor_app_br(s) for s in setores)}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    else:    
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
