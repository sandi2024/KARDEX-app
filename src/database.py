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


@st.cache_data(ttl=600) # Optimiza la carga guardando datos en memoria
def fetch_kardex_alumno(matricula):
    conn = get_connection()
    query = """
    SELECT aa.id_asignatura_plan, a.nombre, aa.calificacion, aa.id_periodo, aa.tipo_examen
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura a ON ap.id_asignatura = a.id_asignatura
    WHERE aa.matricula = %s
    """
    df = pd.read_sql(query, conn, params=(matricula,))
    conn.close()
    return df


def fetch_carreras_alumno(matricula):
    """Identifica qué carreras ha cursado una matrícula"""
    conn = get_connection()
    query = """
        SELECT DISTINCT pe.id_programa, pe.nombre AS nombre_carrera
        FROM alumno_asignatura aa
        JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
        JOIN programaEducativo pe ON ap.id_carrera = pe.id_programa
        WHERE aa.matricula = %s
    """
    df = pd.read_sql(query, conn, params=(matricula,))
    conn.close()
    return df

def fetch_detalle_por_periodo(matricula, id_carrera):
    """
    Obtiene el historial académico detallado de un alumno filtrado por carrera,
    ordenado cronológicamente por periodo.
    """
    conn = get_connection()
    
    # La consulta SQL debe unir el historial con el Plan de Estudios 
    # para asegurar que las materias pertenezcan a la carrera seleccionada.
    query = """
    SELECT 
        aa.id_periodo,
        asig.nombre AS materia,
        aa.calificacion,
        aa.tipo_examen,
        aa.etapa,
        ap.creditos
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura asig ON ap.id_asignatura = asig.id_asignatura
    WHERE aa.matricula = %s 
      AND ap.id_programa = %s
    ORDER BY aa.id_periodo ASC, asig.nombre ASC
    """
    
    try:
        # Usamos pandas para leer directamente la consulta
        df = pd.read_sql(query, conn, params=(matricula, id_carrera))
    finally:
        conn.close()
        
    return df