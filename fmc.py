import streamlit as st
from collections import defaultdict
from streamlit_autorefresh import st_autorefresh
import sqlite3
import pandas as pd

def get_conn():
    return sqlite3.connect("setorizacao.db", check_same_thread=False)

def carregar_logs():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT regiao, horario, grupos, qtd_consoles
        FROM setorizacao_log
        ORDER BY regiao, id DESC
    """)

    dados = cur.fetchall()
    conn.close()
    return dados

def logs_para_dataframe():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT regiao, horario, grupos, qtd_consoles
        FROM setorizacao_log
        ORDER BY regiao, id ASC
    """)

    dados = cur.fetchall()
    conn.close()
    return pd.DataFrame(
        dados,
        columns=["Região", "Horário", "Setores", "Nº Consoles"]
    )


logs = carregar_logs()
df = logs_para_dataframe()
# estilização da tabela de logs
def estilizar_tabela(df):
    return (
        df.style
        .set_properties(**{
            "text-align": "center",
            "font-size": "16px",
            "padding": "8px"
        })
        .set_table_styles([
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "separate"),
                    ("border-spacing", "0 12px"),
                    ("width", "100%")
                ]
            },
            {
                "selector": "th",
                "props": [
                    # ("background-color", "#000000"),
                    ("color", "white"),
                    ("border-radius", "10px"),
                    ("padding", "10px"),
                    ("font-size", "18px")
                ]
            },
            {
                "selector": "td",
                "props": [
                    # ("background-color", "#000000"),
                    ("border-radius", "12px")
                ]
            }
        ])
    )

def cor_por_regiao(regiao):
    cores = {
        "RRJ": "#0095fe",
        "RSP": "#ff062b",
        "RBR": "#ff9d00",
        "FIS": "#fce4ec"
    }
    return f"background-color: {cores.get(regiao, "#090000")}"

df_estilizado = (
    estilizar_tabela(df)
    .applymap(cor_por_regiao, subset=["Região"])
)


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

st.title("Controle FMC - Setorização ACC-BS")
st.markdown("---") 
if st.button("carregar agrupamentos anteriores", key="carregar_anteriores"):
    st.markdown(
    df_estilizado.to_html(),
    unsafe_allow_html=True
)

st.markdown("---")
    
st.warning("Cuidado !!! Esta ação apagará todos os registros anteriores.")
if st.button("Apagar registros", key="apagar_logs"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""DELETE FROM setorizacao_log
                        WHERE id NOT IN (
                        SELECT MAX(id)
                        FROM setorizacao_log
                        GROUP BY regiao
                        )""")
        conn.commit()
        conn.close()
        st.success("Registros apagados com sucesso!")

conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM setorizacao_log")
st.write("Registros restantes:", cur.fetchone()[0])
conn.close()

st_autorefresh(interval=300000, key="refresh_panorama")