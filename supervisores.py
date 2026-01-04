import streamlit as st
from setorizacao import regioes,setores
import sqlite3
from datetime import datetime
import re
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

def chave_setor(setor):
    setor = setor.upper()

    match = re.match(r"^(\d+)([A-Z]?)$", setor)
    if match:
        return (0, int(match.group(1)), match.group(2))

    # FIS vem depois dos setores numéricos
    if setor == "FIS":
        return (1,)

    # Qualquer outro rótulo especial
    return (2, setor)


def formatar_grupos(setorizacao_regiao):
    grupos = []

    for setores in setorizacao_regiao.values():
        if not setores:
            continue

        setores_upper = [s.upper() for s in setores]

        # REGRA ESPECIAL: AGRUPADO
        if "AGRUPADO" in setores_upper:
            if "FIS" in setores_upper:
                grupos.append("AGRUPADO · FIS")
            else:
                grupos.append("AGRUPADO")
            continue  # ignora qualquer outro setor

        # Caso normal (sem AGRUPADO)
        setores_ordenados = sorted(setores_upper, key=chave_setor)
        grupos.append(" · ".join(setores_ordenados))

    return " | ".join(grupos)


def registrar_log(regiao, configuracao):
    conn = sqlite3.connect("setorizacao.db")
    cur = conn.cursor()

    grupos_formatados = formatar_grupos(configuracao)

    qtd_consoles = sum(
        1 for setores in configuracao.values() if setores
    )

    horario = datetime.utcnow().strftime("%H:%M:%S")

    cur.execute("""
        INSERT INTO setorizacao_log (regiao, horario, grupos, qtd_consoles)
        VALUES (?, ?, ?, ?)
    """, (
        regiao,
        horario,
        grupos_formatados,
        qtd_consoles
    ))
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
        options=["RRJ", "RSP", "RBR"]
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
        registrar_log(
            st.session_state.regiao,
            st.session_state.configuracao
        )
        salvar_setorizacao(
            st.session_state.regiao,
            st.session_state.configuracao
        )
        st.success("Configuração salva com sucesso!")
