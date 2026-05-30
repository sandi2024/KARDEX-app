import streamlit as st
from src.database import run_query
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


@st.cache_data(ttl=3600) # El caché dura 1 hora (3600 seg)



#@st.cache_data(ttl=3600) # El caché dura 1 hora (3600 seg)
@st.cache_data(persist="disk") # <--- ESTO ES LA CLAVE
def detalle_por_periodo(matricula, id_carrera):
    """
    Obtiene el historial académico detallado de un alumno filtrado por carrera,
    ordenado cronológicamente por periodo usando run_query.
    """
    # La consulta SQL une el historial con el Plan de Estudios y Asignaturas
    query = """
    SELECT 
        aa.id_periodo,
        asig.nombre AS materia,
        aa.calificacion,
        aa.tipo_examen,
        aa.etapa,
        asig.creditos  -- Nota: En tu diagrama 'creditos' está en 'Asignatura'
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura asig ON ap.id_asignatura = asig.id_asignatura
    JOIN plan_estudio ple ON ap.id_plan_estudio = ple.id_plan_estudio
    WHERE aa.matricula = %s 
      AND ple.id_programa = %s
    ORDER BY aa.id_periodo ASC, asig.nombre ASC
    """
    
    # Ejecutamos la consulta pasando los parámetros como una tupla
    return run_query(query, (matricula, id_carrera))


@st.cache_data(ttl=3600) # El caché dura 1 hora (3600 seg)
def get_data_analisis_completo():
    # Unimos alumno_asignatura -> Asignatura_Plan -> plan_estudio -> programaEducativo
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
    return run_query(query)


@st.cache_data(ttl=3600) # El caché dura 1 hora (3600 seg)
def get_data_completo():
    # Unimos alumno_asignatura -> Asignatura_Plan -> plan_estudio -> programaEducativo
    # Y agregamos alumno_plan_estudio para obtener el orden_prioritario
    query = """
    SELECT 
        aa.matricula,
        pe.nombre AS carrera,
        p.id_periodo AS periodo,
        a.nombre AS asignatura,
        a.creditos AS creditos_materia,
        aa.calificacion,
        aa.tipo_examen,
        pl.creditos_obligatorios + pl.creditos_optativos + pl.creditos_PP AS creditos_totales_plan,
        pl.id_plan_estudio,
        pl.descripcion AS nombre_plan,
        ape.orden_prioritario
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura a ON ap.id_asignatura = a.id_asignatura
    JOIN Periodo p ON aa.id_periodo = p.id_periodo
    JOIN plan_estudio pl ON ap.id_plan_estudio = pl.id_plan_estudio
    JOIN programaEducativo pe ON pl.id_programa = pe.id_programa
    -- Unión para obtener la prioridad del plan para ese alumno específico
    LEFT JOIN alumno_plan_estudio ape ON aa.matricula = ape.matricula 
                                     AND pl.id_plan_estudio = ape.id_plan_estudio
    """
    return run_query(query)
