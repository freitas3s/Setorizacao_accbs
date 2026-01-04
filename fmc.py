import streamlit as st
from collections import defaultdict
from streamlit_autorefresh import st_autorefresh
import sqlite3
from datetime import datetime
import pandas as pd

def get_conn():
    return sqlite3.connect("setorizacao.db", check_same_thread=False)

def carregar_logs():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT regiao, horario, grupos, qtd_consoles
        FROM setorizacao_log
        ORDER BY regiao, id ASC
    """)
    if datetime.now().hour == 7 or datetime.now().hour == 14 or datetime.now().hour == 23:
        cur.execute("""
            DELETE FROM setorizacao_log
        """)

    dados = cur.fetchall()
    conn.close()
    return dados

def logs_para_dataframe(logs):
    return pd.DataFrame(
        logs,
        columns=["Região", "Horário", "Grupos", "Qtd Consoles"]
    )

st.title("Controle FMC - Setorização ACC-BS")
logs = carregar_logs()
df = logs_para_dataframe(logs)
# pega apenas o mais recente de cada região
ultimo_por_regiao = {}

for regiao, horario, grupos, qtd in logs:
    if regiao not in ultimo_por_regiao:
        ultimo_por_regiao[regiao] = (horario, grupos, qtd)

cols = st.columns(len(ultimo_por_regiao))

for col, (regiao, (horario, grupos, qtd)) in zip(cols, ultimo_por_regiao.items()):
    with col:
        st.markdown(
            f"""
            <div style="
                border: 2px solid #4F8BF9;
                border-radius: 16px;
                padding: 22px;
                text-align: center;
                min-height: 220px;
            ">
                <h1>{regiao}</h1>
                <p style="font-size: 18px; color: #AAA;">
                    Última alteração
                </p>
                <p style="font-size: 36px;">
                    {horario}
                </p>
                <p style="font-size: 42px; color: #DDD; margin: 20px 0;">
                    {grupos if grupos else "Sem setores"}
                </p>
                <p style="font-size: 22px;">
                    Consoles ativas: <b>{qtd}</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---") 

if st.button("carregar agrupamentos anteriores", key="carregar_anteriores"):
    st.dataframe(
        df,
        column_order=["Região", "Horário", "Grupos", "Qtd Consoles"],
        hide_index=True,
        row_height=70,
        use_container_width=True

    )

st_autorefresh(interval=300000, key="refresh_panorama")