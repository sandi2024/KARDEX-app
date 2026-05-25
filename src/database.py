import mysql.connector
import streamlit as st
import pandas as pd

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",    # El 'Hostname' de Workbench
            port=3306,           # El 'Port' de Workbench
            user="root",         # El 'Username'
            password="", # La clave que usas para entrar
            database="kardex" # El nombre que ves en 'Schemas'
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error de conexión: {err}")
        return None


def run_query(query, params=None):
    conn = get_connection()
    if conn:
        df = pd.read_sql(query, conn, params=params)   
        conn.close()
        return df
    return pd.DataFrame()   # Devuelve un DataFrame vacío en caso de error de conexión
