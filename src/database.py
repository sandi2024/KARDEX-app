import streamlit as st
import pandas as pd

# Reemplaza get_connection() y run_query() con el conector nativo de Streamlit
# st.connection lee automáticamente los datos del archivo secrets.toml
def get_neon_connection():
    return st.connection("postgresql", type="sql")

# El caché se maneja directamente con el argumento 'ttl' en conn.query()
def get_data_completo():
    conn = get_neon_connection()
    
    # NOTA: Se cambiaron los nombres de las tablas y columnas a MINÚSCULAS 
    # debido a la migración estándar hacia PostgreSQL (Neon)
    query = """
    SELECT 
        aa.matricula,
        pe.nombre AS carrera,
        p.id_periodo AS periodo,
        a.nombre AS asignatura,
        a.creditos AS creditos_materia,
        aa.calificacion,
        aa.tipo_examen,
        pl.creditos_obligatorios + pl.creditos_optativos + pl.creditos_pp AS creditos_totales_plan,
        pl.id_plan_estudio,
        pl.descripcion AS nombre_plan,
        ape.orden_prioritario
    FROM alumno_asignatura aa
    JOIN asignatura_plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN asignatura a ON ap.id_asignatura = a.id_asignatura
    JOIN periodo p ON aa.id_periodo = p.id_periodo
    JOIN plan_estudio pl ON ap.id_plan_estudio = pl.id_plan_estudio
    JOIN programaeducativo pe ON pl.id_programa = pe.id_programa
    LEFT JOIN alumno_plan_estudio ape ON aa.matricula = ape.matricula 
                                     AND pl.id_plan_estudio = ape.id_plan_estudio
    """
    
    try:
        # Ejecuta la consulta y gestiona el caché (1 hora = 3600 segundos) de forma nativa
        df = conn.query(query, ttl=3600)
        return df
    except Exception as e:
        st.error(f"Error al consultar Neon: {e}")
        return pd.DataFrame()
