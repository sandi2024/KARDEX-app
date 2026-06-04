import streamlit as st
from src.database import get_neon_connection, run_query
import pandas as pd

# Aquí definimos las funciones de consulta específicas para cada página, utilizando run_query para ejecutar las consultas SQL.
@st.cache_data(ttl=3600) # El caché dura 1 hora (3600 seg)
def get_kardex_alumno(matricula):
    query = """
    SELECT 
        a.nombre AS Materia,
        aa.calificacion,
        aa.fecha_examen,
        aa.tipo_examen,
        p.anio_periodo AS Periodo
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura a ON ap.id_asignatura = a.id_asignatura
    JOIN Periodo p ON aa.id_periodo = p.id_periodo
    WHERE aa.matricula = %s
    ORDER BY p.anio_periodo ASC;
    """
    return run_query(query, (matricula,))  

def get_kardex_alumno(matricula):
    conn = get_neon_connection()
    
    # NOTA: Se cambiaron los nombres de las tablas y columnas a MINÚSCULAS 
    # debido a la migración estándar hacia PostgreSQL (Neon)
    query = """
    SELECT 
        a.nombre AS Materia,
        aa.calificacion,
        aa.fecha_examen,
        aa.tipo_examen,
        p.anio_periodo AS Periodo
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura a ON ap.id_asignatura = a.id_asignatura
    JOIN Periodo p ON aa.id_periodo = p.id_periodo
    WHERE aa.matricula = %s
    ORDER BY p.anio_periodo ASC;
    """
    try:
        # Ejecuta la consulta y gestiona el caché (1 hora = 3600 segundos) de forma nativa
        df = conn.query(query,(matricula,), ttl=3600)
        return df
    except Exception as e:
        st.error(f"Error al consultar Neon: {e}")
        return pd.DataFrame()



def get_data_analisis_completo():
    conn = get_neon_connection()
    
    query = """
    SELECT 
        aa.matricula,
        pe.nombre AS carrera,
        p.id_periodo AS periodo,    # Esto es para poder filtrar por periodo en el análisis de riesgo, anio_periodo
        a.nombre AS asignatura,
        a.creditos AS creditos_materia,
        aa.calificacion,
        aa.tipo_examen,
        pl.creditos_obligatorios + pl.creditos_optativos + pl.creditos_PP AS creditos_totales_plan,
        pl.id_plan_estudio
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura a ON ap.id_asignatura = a.id_asignatura
    JOIN Periodo p ON aa.id_periodo = p.id_periodo
    JOIN plan_estudio pl ON ap.id_plan_estudio = pl.id_plan_estudio
    JOIN programaEducativo pe ON pl.id_programa = pe.id_programa
    """
    
    try:
        # Ejecuta la consulta y gestiona el caché (1 hora = 3600 segundos) de forma nativa
        df = conn.query(query, ttl=3600)
        return df
    except Exception as e:
        st.error(f"Error al consultar Neon: {e}")
        return pd.DataFrame()
