"""
Ejemplo de Uso del Pipeline de Procesamiento de Datos
Demostración de las funcionalidades del pipeline
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

from pipeline.ejecutor import EjecutorPipeline, ConfiguracionPipeline
from pipeline.extractores.extractor_csv import ExtractorCSV
from pipeline.extractores.extractor_api import ExtractorAPI
from pipeline.transformadores.transformador_limpieza import TransformadorLimpieza
from pipeline.transformadores.transformador_analisis import TransformadorAnalisis
from analisis.estadistico.analizador_estadistico import AnalizadorEstadistico
from analisis.visualizaciones.generador_graficos import GeneradorGraficos


async def crear_datos_ejemplo():
    """Crear datos de ejemplo para demostración"""
    print("📊 Creando datos de ejemplo...")
    
    # Crear directorio de datos si no existe
    os.makedirs("datos/entrada", exist_ok=True)
    os.makedirs("datos/procesados", exist_ok=True)
    os.makedirs("graficos", exist_ok=True)
    
    # Generar datos de ventas
    np.random.seed(42)
    fechas = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    datos_ventas = []
    for fecha in fechas:
        # Simular ventas con estacionalidad
        base_ventas = 1000
        estacionalidad = 200 * np.sin(2 * np.pi * fecha.dayofyear / 365)
        tendencia = 50 * (fecha - fechas[0]).days / 365
        ruido = np.random.normal(0, 100)
        
        ventas = max(0, base_ventas + estacionalidad + tendencia + ruido)
        
        datos_ventas.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'ventas': round(ventas, 2),
            'producto': np.random.choice(['A', 'B', 'C', 'D']),
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste']),
            'vendedor': f"Vendedor_{np.random.randint(1, 11)}",
            'cliente_id': np.random.randint(1000, 9999),
            'descuento': np.random.choice([0, 5, 10, 15, 20]),
            'categoria': np.random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes'])
        })
    
    # Guardar datos de ventas
    df_ventas = pd.DataFrame(datos_ventas)
    df_ventas.to_csv('datos/entrada/ventas_2024.csv', index=False)
    print(f"✅ Datos de ventas creados: {len(df_ventas)} registros")
    
    # Generar datos de clientes
    datos_clientes = []
    for i in range(1000):
        datos_clientes.append({
            'cliente_id': 1000 + i,
            'nombre': f"Cliente_{i+1}",
            'email': f"cliente{i+1}@ejemplo.com",
            'edad': np.random.randint(18, 80),
            'ciudad': np.random.choice(['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao']),
            'fecha_registro': (datetime.now() - timedelta(days=np.random.randint(0, 1000))).strftime('%Y-%m-%d'),
            'segmento': np.random.choice(['Bronce', 'Plata', 'Oro', 'Platino']),
            'activo': np.random.choice([True, False], p=[0.8, 0.2])
        })
    
    # Guardar datos de clientes
    df_clientes = pd.DataFrame(datos_clientes)
    df_clientes.to_csv('datos/entrada/clientes.csv', index=False)
    print(f"✅ Datos de clientes creados: {len(df_clientes)} registros")
    
    return len(datos_ventas) + len(datos_clientes)


async def ejecutar_pipeline_completo():
    """Ejecutar pipeline completo de procesamiento de datos"""
    print("🚀 Iniciando Pipeline de Procesamiento de Datos")
    print("=" * 60)
    
    # 1. Crear datos de ejemplo
    total_registros = await crear_datos_ejemplo()
    
    # 2. Configurar pipeline
    configuracion = ConfiguracionPipeline(
        nombre_pipeline="Pipeline Análisis Ventas 2024",
        version="1.0.0",
        descripcion="Análisis completo de datos de ventas y clientes",
        tamano_lote=5000,
        max_workers=2,
        incluir_metricas=True
    )
    
    ejecutor = EjecutorPipeline(configuracion)
    
    # 3. Agregar extractores
    print("\n📥 Configurando extractores...")
    
    # Extractor CSV para ventas
    extractor_ventas = ExtractorCSV(
        nombre="ExtractorVentas",
        ruta_archivo="datos/entrada/ventas_2024.csv",
        configuracion={
            "separador": ",",
            "encoding": "utf-8",
            "parse_dates": ["fecha"]
        }
    )
    ejecutor.agregar_extractor(extractor_ventas)
    
    # Extractor CSV para clientes
    extractor_clientes = ExtractorCSV(
        nombre="ExtractorClientes",
        ruta_archivo="datos/entrada/clientes.csv",
        configuracion={
            "separador": ",",
            "encoding": "utf-8"
        }
    )
    ejecutor.agregar_extractor(extractor_clientes)
    
    # 4. Agregar transformadores
    print("🔄 Configurando transformadores...")
    
    # Transformador de limpieza
    transformador_limpieza = TransformadorLimpieza(
        nombre="LimpiezaDatos",
        configuracion={
            "manejo_nulos": {
                "estrategia": "imputar",
                "imputacion": "media"
            },
            "manejo_outliers": {
                "habilitado": True,
                "metodo": "iqr",
                "factor": 1.5
            },
            "normalizacion_texto": {
                "habilitada": True,
                "minusculas": True
            }
        }
    )
    ejecutor.agregar_transformador(transformador_limpieza)
    
    # Transformador de análisis
    transformador_analisis = TransformadorAnalisis(
        nombre="AnalisisDatos",
        configuracion={
            "feature_engineering": {
                "habilitado": True,
                "crear_agregaciones": True
            },
            "normalizacion": {
                "habilitada": True,
                "metodo": "standard"
            }
        }
    )
    ejecutor.agregar_transformador(transformador_analisis)
    
    # 5. Ejecutar pipeline
    print("\n⚙️ Ejecutando pipeline...")
    resultado = await ejecutor.ejecutar()
    
    # 6. Mostrar resultados
    print("\n📊 Resultados del Pipeline:")
    print(f"   • Registros procesados: {resultado.registros_procesados}")
    print(f"   • Registros exitosos: {resultado.registros_exitosos}")
    print(f"   • Tasa de éxito: {resultado.tasa_exito:.2%}")
    print(f"   • Duración: {resultado.duracion_segundos:.2f} segundos")
    print(f"   • Completitud: {resultado.completitud_datos:.2f}%")
    print(f"   • Consistencia: {resultado.consistencia_datos:.2f}%")
    print(f"   • Precisión: {resultado.precision_datos:.2f}%")
    
    return resultado


async def ejecutar_analisis_estadistico():
    """Ejecutar análisis estadístico avanzado"""
    print("\n📈 Ejecutando Análisis Estadístico")
    print("=" * 40)
    
    # Cargar datos procesados
    df_ventas = pd.read_csv('datos/entrada/ventas_2024.csv')
    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
    
    # Crear analizador
    analizador = AnalizadorEstadistico()
    
    # Análisis de estadísticas descriptivas
    print("📊 Calculando estadísticas descriptivas...")
    estadisticas = await analizador.analizar_estadisticas_descriptivas(df_ventas, ['ventas'])
    
    for columna, stats in estadisticas.items():
        print(f"\n   {columna}:")
        print(f"     • Media: {stats.media:.2f}")
        print(f"     • Mediana: {stats.mediana:.2f}")
        print(f"     • Desv. Estándar: {stats.desviacion_estandar:.2f}")
        print(f"     • Mínimo: {stats.minimo:.2f}")
        print(f"     • Máximo: {stats.maximo:.2f}")
        print(f"     • Asimetría: {stats.asimetria:.2f}")
    
    # Análisis de correlaciones
    print("\n🔗 Analizando correlaciones...")
    correlaciones = await analizador.analizar_correlaciones(df_ventas, ['ventas', 'descuento'])
    
    print(f"   • Correlaciones fuertes: {len(correlaciones.correlaciones_fuertes)}")
    print(f"   • Correlaciones significativas: {len(correlaciones.correlaciones_significativas)}")
    
    # Análisis de tendencias
    print("\n📈 Analizando tendencias temporales...")
    tendencias = await analizador.analizar_tendencias(
        df_ventas, 'fecha', 'ventas', ventana_prediccion=30
    )
    
    if tendencias.tendencia_lineal:
        print(f"   • Pendiente: {tendencias.tendencia_lineal['pendiente']:.4f}")
        print(f"   • R²: {tendencias.tendencia_lineal['r2']:.4f}")
        print(f"   • RMSE: {tendencias.tendencia_lineal['rmse']:.2f}")
    
    # Generar resumen estadístico
    print("\n📋 Generando resumen estadístico...")
    resumen = await analizador.generar_resumen_estadistico(df_ventas)
    
    print(f"   • Total registros: {resumen['informacion_general']['total_registros']}")
    print(f"   • Total columnas: {resumen['informacion_general']['total_columnas']}")
    print(f"   • Uso memoria: {resumen['informacion_general']['memoria_uso_mb']:.2f} MB")


async def ejecutar_visualizaciones():
    """Generar visualizaciones de los datos"""
    print("\n🎨 Generando Visualizaciones")
    print("=" * 40)
    
    # Cargar datos
    df_ventas = pd.read_csv('datos/entrada/ventas_2024.csv')
    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
    
    # Crear generador de gráficos
    generador = GeneradorGraficos({
        'directorio_salida': 'graficos',
        'tamaño_figura': (10, 6)
    })
    
    # Generar gráficos automáticos
    print("📊 Generando gráficos automáticos...")
    archivos_generados = await generador.generar_graficos_automaticos(df_ventas)
    
    print(f"   • Gráficos generados: {len(archivos_generados)}")
    for archivo in archivos_generados:
        print(f"     - {archivo}")
    
    # Generar gráfico específico de ventas por mes
    print("\n📈 Generando gráfico de ventas por mes...")
    df_mensual = df_ventas.groupby(df_ventas['fecha'].dt.to_period('M'))['ventas'].sum().reset_index()
    df_mensual['fecha'] = df_mensual['fecha'].astype(str)
    
    archivo_ventas = await generador.generar_grafico_lineas(
        df_mensual, 'fecha', 'ventas', 'Ventas Mensuales 2024'
    )
    print(f"   • Gráfico de ventas: {archivo_ventas}")
    
    # Generar heatmap de correlaciones
    print("\n🔥 Generando heatmap de correlaciones...")
    columnas_numericas = df_ventas.select_dtypes(include=[np.number]).columns.tolist()
    archivo_heatmap = await generador.generar_heatmap_correlacion(
        df_ventas, columnas_numericas, 'Correlaciones entre Variables'
    )
    print(f"   • Heatmap: {archivo_heatmap}")


async def main():
    """Función principal"""
    print("🎯 Pipeline de Procesamiento de Datos - Ejemplo de Uso")
    print("=" * 60)
    
    try:
        # Ejecutar pipeline completo
        resultado_pipeline = await ejecutar_pipeline_completo()
        
        # Ejecutar análisis estadístico
        await ejecutar_analisis_estadistico()
        
        # Generar visualizaciones
        await ejecutar_visualizaciones()
        
        print("\n✅ Pipeline ejecutado exitosamente!")
        print(f"📁 Archivos generados en: ./graficos/")
        print(f"📊 Datos procesados en: ./datos/procesados/")
        
    except Exception as e:
        print(f"\n❌ Error en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
