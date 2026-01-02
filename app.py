import streamlit as st
import sqlite3

def get_conn():
    return sqlite3.connect("setorizacao.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS setorizacao (
            regiao TEXT,
            ctr TEXT,
            setor INTEGER,
            PRIMARY KEY (regiao, ctr, setor)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS setorizacao_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regiao TEXT NOT NULL,
            horario TEXT NOT NULL,
            grupos TEXT NOT NULL,
            qtd_consoles INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

setores = st.Page("consoles.py" , title="Setorização ACC-BS")
supervisores = st.Page("supervisores.py" , title="Supervisores ACC-BS")
fmc = st.Page("fmc.py" , title="Controle FMC")

pg = st.navigation([setores, supervisores, fmc], position= "top")

st.set_page_config(page_title="Setorização ACC-BS", layout="wide")
pg.run()