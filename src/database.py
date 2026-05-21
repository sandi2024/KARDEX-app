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

def fetch_analisis_reprobacion(id_carrera=None, id_periodo=None):
    conn = get_connection()
    
    # Base de la consulta: Unimos Alumno -> Alumno_Asignatura -> Asignatura_Plan -> Asignatura
    query = """
    SELECT 
        c.nombre_carrera,
        aa.id_periodo,
        asig.descripcion AS materia,
        aa.calificacion,
        CASE WHEN aa.calificacion < 60 THEN 1 ELSE 0 END AS es_reprobado
    FROM alumno_asignatura aa
    JOIN Alumno al ON aa.matricula = al.matricula
    JOIN Carrera c ON al.id_carrera = c.id_carrera
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura asig ON ap.id_asignatura = asig.id_asignatura
    WHERE 1=1
    """
    
    # Filtros dinámicos
    params = []
    if id_carrera:
        query += " AND c.id_carrera = %s"
        params.append(id_carrera)
    if id_periodo:
        query += " AND aa.id_periodo = %s"
        params.append(id_periodo)
        
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def fetch_carreras_alumno(matricula):
    """Identifica qué carreras ha cursado una matrícula"""
    conn = get_connection()
    query = """
        SELECT DISTINCT c.id_carrera, c.nombre_carrera 
        FROM alumno_asignatura aa
        JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
        JOIN Carrera c ON ap.id_carrera = c.id_carrera
        WHERE aa.matricula = %s
    """
    df = pd.read_sql(query, conn, params=(matricula,))
    conn.close()
    return df