import pandas as pd

def calcular_indice_riesgo(df_alumno_materias):
    """
    Recibe el historial de un alumno y devuelve un puntaje de riesgo.
    """
    # 1. Factor Reprobación (Materias con calificación < 60)
    reprobadas = len(df_alumno_materias[df_alumno_materias['calificacion'] < 60])
    
    # 2. Factor Persistencia (Tipos de examen: 'Extraordinario' o 'Regularización')
    # Según tu diagrama, esto viene de alumno_asignatura.tipo_examen
    extraordinarios = len(df_alumno_materias[df_alumno_materias['tipo_examen'].str.contains('EXT', na=False)])
    
    # 3. Cálculo de Score (Ejemplo)
    # Cada reprobada vale 2 puntos, cada extraordinario vale 1 punto
    score = (reprobadas * 2) + (extraordinarios * 1)
    
    # Clasificación
    if score >= 6: nivel = "Crítico (🔴)"
    elif score >= 3: nivel = "Alerta (🟡)"
    else: nivel = "Estable (🟢)"
    
    return {
        "score": score,
        "nivel": nivel,
        "total_reprobadas": reprobadas,
        "total_extras": extraordinarios
    }

def calcular_metricas_alumno(df_kardex):
    total_materias = len(df_kardex)
    aprobadas = len(df_kardex[df_kardex['calificacion'] >= 60])
    promedio = df_kardex['calificacion'].mean()
    
    # Análisis de riesgo
    reprobadas = total_materias - aprobadas
    nivel_riesgo = "Bajo"
    if reprobadas >= 2: nivel_riesgo = "Moderado"
    if reprobadas >= 4 or promedio < 60: nivel_riesgo = "Alto"
    
    return {
        "promedio": promedio,
        "avance": (aprobadas / total_materias) * 100,
        "riesgo": nivel_riesgo
    }



def procesar_academicos(df, umbral_reprobacion):
    if df.empty: return df

    # 1. Limpieza de calificaciones (null = 0 por falta de derecho, 0 = no presentó)
    df['calificacion'] = df['calificacion'].fillna(0)

    # 2. Creamos llave única: Matricula + Carrera
    # Esto asegura que el alumno en dos carreras se calcule por separado
    df['id_estudiante'] = df['matricula'].astype(str) + "_" + df['carrera']

    # 3. Agrupación por estudiante/carrera
    analisis = df.groupby('id_estudiante').agg({
        'calificacion': 'mean',
        'creditos_materia': 'sum',
        'creditos_totales_plan': 'first',
        'tipo_examen': lambda x: (x.str.contains('Ext', case=False, na=False)).sum(),
        'carrera': 'first',
        'id_plan_estudio': 'first'
    }).rename(columns={
        'calificacion': 'promedio_general',
        'creditos_materia': 'creditos_cursados',
        'tipo_examen': 'conteo_extraordinarios'
    })

    # 4. Cálculo de Avance
    analisis['avance_porcentaje'] = (analisis['creditos_cursados'] / analisis['creditos_totales_plan']) * 100

    # 5. Lógica de Estatus Dinámica
    def asignar_estatus(row):
        if row['promedio_general'] < umbral_reprobacion:
            return 'RIESGO'
        elif row['conteo_extraordinarios'] >= 3: # Ejemplo: más de 3 extras es crítico
            return 'REZAGADO'
        elif row['promedio_general'] >= 90:
            return 'ACTIVO' # Sobresaliente
        else:
            return 'REGULAR'

    analisis['estatus'] = analisis.apply(asignar_estatus, axis=1)
    return analisis.reset_index()

def calcular_metricas_extraordinarios(df):
    """
    df: DataFrame que viene de la base de datos (una fila por materia)
    """
    # 1. Identificamos qué registros son exámenes extraordinarios
    # Usamos .str.contains por si el texto varía (ej: 'EXTRAORDINARIO 1', 'EXTRAORDINARIO 2')
    df['es_extraordinario'] = df['tipo_examen'].str.contains('EXTRAORDINARIO', case=False, na=False).astype(int)

    # 2. Agrupamos por alumno (y carrera) para contar sus extras totales
    # Recordamos usar la llave única 'id_estudiante' (matricula + carrera)
    extras_por_alumno = df.groupby('id_estudiante')['es_extraordinario'].sum().reset_index()

    # 3. Calculamos el promedio global de esos conteos
    # Esto responde: "¿En promedio, cuántos extras presenta un alumno de esta carrera?"
    promedio_extras = extras_por_alumno['es_extraordinario'].mean()

    return promedio_extras, extras_por_alumno