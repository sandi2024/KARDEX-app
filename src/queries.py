from src.database import run_query
import pandas as pd

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


def fetch_analisis_reprobacion(id_carrera=None, id_periodo=None):
    """
    Obtiene los datos detallados para el análisis de reprobación.
    Usa la lógica de filtros dinámicos y delega la ejecución a run_query.
    """
    # Base de la consulta
    query = """
    SELECT 
        pe.nombre AS nombre_carrera,
        aa.id_periodo,
        asig.nombre AS materia,
        aa.calificacion,
        CASE WHEN aa.calificacion < 60 THEN 1 ELSE 0 END AS es_reprobado
    FROM alumno_asignatura aa
    JOIN Alumno al ON aa.matricula = al.matricula
    JOIN programaEducativo pe ON al.id_carrera = pe.id_programa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN Asignatura asig ON ap.id_asignatura = asig.id_asignatura
    WHERE 1=1
    """
    
    params = []
    
    # Filtros dinámicos
    if id_carrera:
        query += " AND pe.id_programa = %s"  # Se agregó el '='
        params.append(id_carrera)
        
    if id_periodo:
        query += " AND aa.id_periodo = %s"   # Corregido: id_periodo en lugar de id_programa
        params.append(id_periodo)
        
    # Ejecución delegada a run_query
    # Convertimos params a tupla si tiene elementos, sino pasamos None
    return run_query(query, tuple(params) if params else None)


def fetch_carreras_alumno(matricula):
    """
    Identifica qué carreras ha cursado una matrícula.
    Delegación directa a run_query.
    """
    query = """
        SELECT DISTINCT pe.id_programa, pe.nombre AS nombre_carrera
        FROM alumno_asignatura aa
        JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
        JOIN programaEducativo pe ON ap.id_carrera = pe.id_programa
        WHERE aa.matricula = %s
    """
    # Pasamos la matrícula como una tupla (matricula,) para seguridad
    return run_query(query, (matricula,))