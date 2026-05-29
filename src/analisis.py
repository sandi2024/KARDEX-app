import pandas as pd
import numpy as np

def procesar_kardex(df, umbral_reprobacion):
    # --- 1. PRE-PROCESAMIENTO DE CALIFICACIONES ---
    # Creamos una copia para no alterar el DataFrame original
    df_proc = df.copy()

    # Agrupamos por el ID único del alumno
    grupos = df_proc.groupby('id_estudiante')

    # --- 2. CÁLCULO DE MÉTRICAS ---
    resumen_alumnos = pd.DataFrame()

    # Promedio Final: mean() de pandas ignora los NaN (NP) por defecto, 
    # pero sí promedia los 0 (SD). Es el comportamiento académico estándar.
    resumen_alumnos['promedio_final'] = grupos['calificacion'].mean()

    # Créditos Logrados: Solo sumamos créditos si aprobó (calif >= umbral)
    # NP (NaN) y SD (0) fallarán la condición >= 70, por lo que no sumarán créditos.
    resumen_alumnos['total_creditos_logrados'] = grupos.apply(
        lambda x: x[x['calificacion'] >= umbral_reprobacion]['creditos_materia'].sum()
    )

    # Tasa de Extraordinarios
    resumen_alumnos['tasa_extraordinarios'] = grupos.apply(
        lambda x: (x['tipo_examen'] == 'Ext').mean()
    )

    # Conteo de Casos Especiales (NP y SD)
    # Usamos la columna original o la procesada para identificar los nulos
    resumen_alumnos['conteo_SD'] = grupos.apply(lambda x: (x['calificacion'] == 0).sum())
    resumen_alumnos['conteo_NP'] = grupos.apply(lambda x: x['calificacion'].isna().sum())

    # --- 3. MÉTRICAS DE TRAYECTORIA ---
    resumen_alumnos['periodos_cursados'] = grupos['periodo'].nunique()
    
    resumen_alumnos['eficiencia_creditos'] = (
        resumen_alumnos['total_creditos_logrados'] / resumen_alumnos['periodos_cursados']
    )

    return resumen_alumnos

def procesar_kardex_general(df, umbral_reprobacion, max_extraordinario):
    # --- 1. PRE-PROCESAMIENTO DE CALIFICACIONES ---
    # Creamos una copia para no alterar el DataFrame original
    df_proc = df.copy()

    # Agrupamos por el ID único del alumno
    grupos = df_proc.groupby('id_estudiante')

    # --- 2. CÁLCULO DE MÉTRICAS ---
    resumen_alumnos = pd.DataFrame()

    # Promedio Final: mean() de pandas ignora los NaN (NP) por defecto, 
    # pero sí promedia los 0 (SD). Es el comportamiento académico estándar.
    resumen_alumnos['carrera'] = grupos['carrera'].first()
    resumen_alumnos['id_plan_estudio'] = grupos['id_plan_estudio'].first()
    resumen_alumnos['plan_estudio'] = grupos['nombre_plan'].first()
    resumen_alumnos['promedio_final'] = grupos['calificacion'].mean()
    # Créditos Logrados: Solo sumamos créditos si aprobó (calif >= umbral)
    # NP (NaN) y SD (0) fallarán la condición >= 70, por lo que no sumarán créditos.
    
    resumen_alumnos['total_creditos_logrados'] = grupos.apply(
        lambda x: x[x['calificacion'] >= umbral_reprobacion]['creditos_materia'].sum()
    )
   
    resumen_alumnos['creditos_total'] = grupos['creditos_totales_plan'].first()
   
    resumen_alumnos['conteo_extraordinarios'] = grupos.apply(
        lambda x: (x['tipo_examen'] == 'Ext').sum()
    )

    # Tasa de Extraordinarios
    resumen_alumnos['tasa_extraordinarios'] = grupos.apply(
        lambda x: (x['tipo_examen'] == 'Ext').mean()
    )

    # Conteo de Casos Especiales (NP y SD)
    # Usamos la columna original o la procesada para identificar los nulos
    resumen_alumnos['conteo_SD'] = grupos.apply(lambda x: (x['calificacion'] == 0).sum())
    resumen_alumnos['conteo_NP'] = grupos.apply(lambda x: x['calificacion'].isna().sum())

    def asignar_estatus(row):
        if row['promedio_final'] < umbral_reprobacion:
            return 'RIESGO'
        if row['conteo_extraordinarios'] >= max_extraordinario:
            return 'REZAGADO'
        if row['promedio_final'] >= 90:
            return 'EXCELENTE'
        return 'REGULAR'
    
    def avance_credito(row):
        return row['total_creditos_logrados']/row['creditos_total']*100

    resumen_alumnos['estatus'] = resumen_alumnos.apply(asignar_estatus, axis=1)
    resumen_alumnos['avance_porcentaje'] = resumen_alumnos.apply(avance_credito, axis=1)

    return resumen_alumnos


def calcular_metricas_generales(df_kardex):
    total_alumnos = len(df_kardex)
    promedio_general = df_kardex['promedio_final'].mean()
    promedio_ext = df_kardex['conteo_extraordinarios'].mean()
    sobresalientes = len(df_kardex[df_kardex['promedio_final'] >= 90])
    en_riesgo = len(df_kardex[df_kardex['estatus'] == 'RIESGO'])
    porcetaje_en_riesgo = (en_riesgo/total_alumnos)*100
    avance_porcentaje = df_kardex['avance_porcentaje'].mean()
   

    return {
        "total_alumno": total_alumnos,
        "promedio_general": promedio_general,
        "avance_porcentaje": avance_porcentaje,
        "porcentaje_riesgo": porcetaje_en_riesgo,
        "promedio_ext": promedio_ext,
        "sobresalientes": sobresalientes,
        "en_riesgo": en_riesgo
    }


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
  #  df['calificacion'] = df['calificacion'].fillna(0)   # esto 
    df['calificacion'] = pd.to_numeric(df['calificacion'], errors='coerce')
    
    # 2. Creación de llave única: Matricula + Carrera
    df['id_estudiante'] = df['matricula'].astype(str) + "_" + df['carrera']
    df = df.sort_values(['id_estudiante', 'orden_prioritario'], ascending=True)

    return df



def calcular_metricas_academicas(df_normalizado, umbral_reprobacion):
    """Agrupa por estudiante y calcula indicadores de desempeño."""
    if df_normalizado.empty:
        return df_normalizado
    
    df_ordenado = df_normalizado.sort_values(['id_estudiante', 'orden_prioritario'], ascending=True)
    
    # 1. Agrupación y Agregación
    analisis = df_ordenado.groupby('id_estudiante').agg({
        'calificacion': 'mean',
        'creditos_materia': 'sum',
        'creditos_totales_plan': 'first',
        'tipo_examen': lambda x: (x.str.contains('Ext', case=False, na=False)).sum(),
        'carrera': 'first',
        'id_plan_estudio': 'first',
        'nombre_plan': 'first'
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
            return 'EXCELENTE'
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