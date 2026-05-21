import mysql.connector
import streamlit as st
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=" ",
        database="kardex"
    )

@st.cache_data(ttl=600) # Optimiza la carga guardando datos en memoria
def fetch_kardex_alumno(matricula):
    conn = get_connection()
    query = """
    SELECT aa.id_asignatura_plan, a.descripcion, aa.calificacion, aa.id_periodo, aa.tipo_examen
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura a ON ap.id_asignatura = a.id_asignatura
    WHERE aa.matricula = %s
    """
    df = pd.read_sql(query, conn, params=(matricula,))
    conn.close()
    return df