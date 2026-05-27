import pandas as pd

def calcular_indice_riesgo(df_alumno_materias):
    """
    Recibe el historial de un alumno y devuelve un puntaje de riesgo.
    """
    # 1. Factor Reprobación (Materias con calificación < 60)
    reprobadas = len(df_alumno_materias[df_alumno_materias['calificacion'] < 60])
    
    # 2. Factor Persistencia (Tipos de examen: 'Extraordinario' o 'Regularización')
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

def normalizar_datos_academicos(df):
    """Limpia nulos y genera llaves únicas para el análisis."""
    if df.empty:
        return df
    
    df = df.copy() # Evitamos modificar el dataframe original (SettingWithCopyWarning)
    
    # 1. Limpieza de calificaciones
    df['calificacion'] = df['calificacion'].fillna(0)
    
    # 2. Creación de llave única: Matricula + Carrera
    df['id_estudiante'] = df['matricula'].astype(str) + "_" + df['carrera']
    
    return df


def calcular_metricas_academicas(df_normalizado, umbral_reprobacion):
    """Agrupa por estudiante y calcula indicadores de desempeño."""
    if df_normalizado.empty:
        return df_normalizado

    # 1. Agrupación y Agregación
    analisis = df_normalizado.groupby('id_estudiante').agg({
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

    # 2. Cálculo de Avance en porcentaje del plan de estudios, creditos_cursados / creditos_totales_plan
    analisis['avance_porcentaje'] = (analisis['creditos_cursados'] / analisis['creditos_totales_plan']) * 100

    # 3. Lógica de Estatus
    def asignar_estatus(row):
        if row['promedio_general'] < umbral_reprobacion:
            return 'RIESGO'
        if row['conteo_extraordinarios'] >= 3:
            return 'REZAGADO'
        if row['promedio_general'] >= 90:
            return 'ACTIVO'
        return 'REGULAR'

    analisis['estatus'] = analisis.apply(asignar_estatus, axis=1)
    
    return analisis.reset_index()


# Suponiendo que carrera_sel y periodo_sel vienen de un selectbox de Streamlit
def filtrar_datos(df, periodo_sel):
    df_filtrado = df.copy()
    
    # Filtro por Periodo
    if periodo_sel != "Todos los periodos":
        df_filtrado = df_filtrado[df_filtrado['periodo'] == periodo_sel]
    
    return df_filtrado


def calcular_metricas_reprobacion(df_normalizado, calificacion_minima):
    """
    Filtra las materias reprobadas y cuenta la frecuencia por materia.
    Retorna una Serie de pandas con el Top 10 para la gráfica.
    """
    if df_normalizado.empty:
        return pd.Series(dtype=int)

    # 1. Identificar registros reprobados
    reprobados = df_normalizado[df_normalizado['calificacion'] < calificacion_minima]

    # 2. Contar alumnos por materia
    conteo_reprobadas = reprobados['asignatura'].value_counts()

    # 3. Retornar el Top 10 (o las que gustes) de forma descendente
    return conteo_reprobadas.head(10).sort_values(ascending=True)


def calcular_evolucion_academica(df_limpio, umbral):
    """Calcula reprobación y promedio por periodo."""
    if df_limpio.empty: return pd.DataFrame()

    df_limpio = df_limpio.copy()
    df_limpio['es_reprobado'] = df_limpio['calificacion'] < umbral
    
    # Agrupamos para obtener ambos datos
    evolucion = df_limpio.groupby('periodo').agg(
        total_alumnos=('id_estudiante', 'nunique'),
        reprobados=('es_reprobado', 'sum'),
        promedio_periodo=('calificacion', 'mean') # Nueva métrica
    ).reset_index()
    
    evolucion['porcentaje_reprobacion'] = (evolucion['reprobados'] / evolucion['total_alumnos']) * 100
    evolucion['periodo'] = evolucion['periodo'].astype(str)
    
    return evolucion.sort_values('periodo')



def distribucion_calificaciones(df_limpio):
    """Prepara los datos para un histograma de frecuencias."""
    if df_limpio.empty: return df_limpio
    return df_limpio[['calificacion']]    


def predecir_riesgo(df_alumno, umbral_aprobacion=70):
    if df_alumno.empty:
        return 0, "SIN DATOS"

    # --- INDICADOR 1: PROMEDIO ---
    promedio = df_alumno['calificacion'].mean()
    
    # --- INDICADOR 2: TASA DE REPROBACIÓN ---
    total_materias = len(df_alumno)
    reprobadas = len(df_alumno[df_alumno['calificacion'] < umbral_aprobacion])
    tasa_reprobacion = (reprobadas / total_materias) * 100

    # --- INDICADOR 3: EXÁMENES EXTRAORDINARIOS ---
    # Asumiendo que tienes una columna 'tipo_examen' o similar
    extraordinarios = 0
    if 'tipo_examen' in df_alumno.columns:
        extraordinarios = len(df_alumno[df_alumno['tipo_examen'] == 'EXTRAORDINARIO'])

    # --- CÁLCULO DEL SCORE (0 a 100) ---
    # Lógica: Más puntos = Más riesgo
    score = 0
    if promedio < umbral_aprobacion + 5: score += 30  # Cerca del límite
    if promedio < umbral_aprobacion: score += 20      # Ya está reprobado
    if tasa_reprobacion > 20: score += 20             # Ha reprobado 1 de cada 5
    if extraordinarios > 2: score += 30               # Muchos intentos extra

    # Determinar Estatus
    if score >= 70: estatus = "RIESGO CRÍTICO"
    elif score >= 40: estatus = "RIESGO MODERADO"
    else: estatus = "ESTABLE"

    return min(score, 100), estatus