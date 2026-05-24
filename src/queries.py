from src.database import run_query

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
    # Base de la consulta
    query = """
    SELECT 
        pe.id_programa AS ID_Carrera,
        pe.nombre AS Carrera,
        p.id_periodo AS ID_Periodo,
        p.anio_periodo AS Periodo,
        COUNT(aa.matricula) AS Total_Reprobados,
        AVG(aa.calificacion) AS Promedio_General_Reprobados
    FROM alumno_asignatura aa
    JOIN Asignatura_Plan ap ON aa.id_asignatura_plan = ap.id_asignatura_plan
    JOIN plan_estudio ple ON ap.id_plan_estudio = ple.id_plan_estudio
    JOIN programaEducativo pe ON ple.id_programa = pe.id_programa
    JOIN Periodo p ON aa.id_periodo = p.id_periodo
    WHERE aa.calificacion < 6.0  -- Filtro de reprobación
    """
    
    params = []
    
    # Agregar filtros dinámicos según los argumentos
    if id_carrera:
        query += " AND pe.id_programa = %s"
        params.append(id_carrera)
    
    if id_periodo:
        query += " AND p.id_periodo = %s"
        params.append(id_periodo)
        
    # Agrupación y orden
    query += " GROUP BY pe.id_programa, p.id_periodo ORDER BY p.anio_periodo DESC"
    
    # Ejecutamos usando la función run_query que explicamos antes
    return run_query(query, tuple(params) if params else None)