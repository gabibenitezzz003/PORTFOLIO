"""
Ejemplo de Uso de Apache Airflow
Demostración de las funcionalidades del sistema de orquestación
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import structlog

# Configurar logging
logger = structlog.get_logger()

def ejemplo_dag_etl():
    """
    Ejemplo de DAG de ETL
    """
    print("🔄 Ejemplo de DAG de ETL")
    print("=" * 50)
    
    # Simular datos de ventas
    datos_ventas = {
        'id_venta': range(1, 101),
        'fecha_venta': pd.date_range('2024-01-01', periods=100, freq='D'),
        'id_cliente': np.random.randint(1, 51, 100),
        'id_producto': np.random.randint(1, 21, 100),
        'cantidad': np.random.randint(1, 10, 100),
        'precio_unitario': np.random.uniform(10, 500, 100),
        'total_venta': 0,  # Se calculará
        'descuento': np.random.uniform(0, 50, 100),
        'id_vendedor': np.random.randint(1, 11, 100),
        'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], 100),
        'canal_venta': np.random.choice(['Online', 'Tienda', 'Telefono'], 100)
    }
    
    # Crear DataFrame
    df = pd.DataFrame(datos_ventas)
    df['total_venta'] = df['cantidad'] * df['precio_unitario'] - df['descuento']
    
    print(f"📊 Datos de ventas generados: {len(df)} registros")
    print(f"   • Período: {df['fecha_venta'].min()} a {df['fecha_venta'].max()}")
    print(f"   • Total de ventas: ${df['total_venta'].sum():,.2f}")
    print(f"   • Promedio por venta: ${df['total_venta'].mean():.2f}")
    
    # Simular transformaciones
    print("\n🔧 Aplicando transformaciones...")
    
    # 1. Limpiar datos
    df_limpio = df.dropna()
    print(f"   • Registros después de limpieza: {len(df_limpio)}")
    
    # 2. Calcular métricas adicionales
    df_limpio['margen_bruto'] = df_limpio['total_venta'] - (df_limpio['cantidad'] * df_limpio['precio_unitario'])
    df_limpio['porcentaje_descuento'] = (df_limpio['descuento'] / df_limpio['total_venta']) * 100
    df_limpio['dia_semana'] = df_limpio['fecha_venta'].dt.day_name()
    df_limpio['mes'] = df_limpio['fecha_venta'].dt.month
    df_limpio['trimestre'] = df_limpio['fecha_venta'].dt.quarter
    
    # 3. Categorizar ventas
    df_limpio['categoria_venta'] = pd.cut(
        df_limpio['total_venta'],
        bins=[0, 100, 500, 1000, float('inf')],
        labels=['Baja', 'Media', 'Alta', 'Premium']
    )
    
    print(f"   • Métricas calculadas: margen_bruto, porcentaje_descuento, categoria_venta")
    
    # 4. Validar datos
    registros_invalidos = df_limpio[df_limpio['total_venta'] <= 0].shape[0]
    print(f"   • Registros inválidos encontrados: {registros_invalidos}")
    
    # 5. Generar reporte
    reporte = f"""
    REPORTE ETL DE VENTAS - {datetime.now().strftime('%Y-%m-%d')}
    ========================================================
    
    Métricas de Procesamiento:
    - Registros originales: {len(df):,}
    - Registros procesados: {len(df_limpio):,}
    - Tasa de completitud: {(len(df_limpio) / len(df) * 100):.2f}%
    - Total de ventas: ${df_limpio['total_venta'].sum():,.2f}
    - Promedio por venta: ${df_limpio['total_venta'].mean():.2f}
    
    Distribución por Categoría:
    {df_limpio['categoria_venta'].value_counts().to_string()}
    
    Distribución por Región:
    {df_limpio['region'].value_counts().to_string()}
    
    Distribución por Canal:
    {df_limpio['canal_venta'].value_counts().to_string()}
    """
    
    print("\n📋 Reporte generado:")
    print(reporte)
    
    return df_limpio

def ejemplo_dag_ml():
    """
    Ejemplo de DAG de Machine Learning
    """
    print("\n🤖 Ejemplo de DAG de Machine Learning")
    print("=" * 50)
    
    # Simular datos de entrenamiento
    np.random.seed(42)
    n_muestras = 1000
    
    # Características de usuarios
    edad = np.random.randint(18, 65, n_muestras)
    genero = np.random.choice(['M', 'F'], n_muestras)
    dias_registro = np.random.randint(1, 365, n_muestras)
    
    # Características de productos
    precio = np.random.uniform(10, 500, n_muestras)
    rating = np.random.uniform(1, 5, n_muestras)
    categoria = np.random.choice(['electronica', 'ropa', 'hogar'], n_muestras)
    
    # Características de interacción
    duracion = np.random.uniform(1, 300, n_muestras)
    
    # Generar variable objetivo (interés)
    # Simular lógica de interés basada en las características
    interes_base = (
        (edad < 30) * 0.3 +  # Jóvenes más interesados
        (genero == 'F') * 0.2 +  # Género influye
        (precio < 100) * 0.4 +  # Productos baratos más interesantes
        (rating > 4) * 0.5 +  # Productos bien calificados
        (duracion > 60) * 0.3  # Interacciones largas
    )
    
    # Agregar ruido
    ruido = np.random.normal(0, 0.1, n_muestras)
    interes = (interes_base + ruido > 0.5).astype(int)
    
    print(f"📊 Datos de entrenamiento generados: {n_muestras} muestras")
    print(f"   • Distribución de interés: {np.bincount(interes)}")
    print(f"   • Tasa de interés positiva: {interes.mean():.2%}")
    
    # Simular entrenamiento del modelo
    print("\n🔧 Entrenando modelo...")
    
    # Crear DataFrame
    df = pd.DataFrame({
        'edad': edad,
        'genero': genero,
        'dias_registro': dias_registro,
        'precio': precio,
        'rating': rating,
        'categoria': categoria,
        'duracion': duracion,
        'interes': interes
    })
    
    # Codificar variables categóricas
    df_encoded = pd.get_dummies(df, columns=['genero', 'categoria'])
    
    # Seleccionar características
    caracteristicas = ['edad', 'dias_registro', 'precio', 'rating', 'duracion']
    caracteristicas.extend([col for col in df_encoded.columns if col.startswith('genero_') or col.startswith('categoria_')])
    
    X = df_encoded[caracteristicas]
    y = df_encoded['interes']
    
    # Dividir datos
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenar modelo
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    # Hacer predicciones
    y_pred = modelo.predict(X_test)
    
    # Calcular métricas
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"   • Accuracy: {accuracy:.3f}")
    print(f"   • Precision: {precision:.3f}")
    print(f"   • Recall: {recall:.3f}")
    print(f"   • F1-Score: {f1:.3f}")
    
    # Validar modelo
    umbrales = {
        'accuracy_min': 0.75,
        'precision_min': 0.70,
        'recall_min': 0.65,
        'f1_min': 0.70
    }
    
    validaciones = {
        'accuracy_ok': accuracy >= umbrales['accuracy_min'],
        'precision_ok': precision >= umbrales['precision_min'],
        'recall_ok': recall >= umbrales['recall_min'],
        'f1_ok': f1 >= umbrales['f1_min']
    }
    
    modelo_valido = all(validaciones.values())
    
    print(f"\n✅ Validación del modelo:")
    for metrica, es_valida in validaciones.items():
        estado = "✅" if es_valida else "❌"
        print(f"   • {metrica}: {estado}")
    
    print(f"\n🎯 Modelo válido: {'Sí' if modelo_valido else 'No'}")
    
    # Simular despliegue
    if modelo_valido:
        print("\n🚀 Desplegando modelo a producción...")
        print("   • Modelo guardado en /opt/models/produccion/")
        print("   • Metadatos actualizados")
        print("   • Modelo listo para uso")
    
    # Generar reporte
    reporte = f"""
    REPORTE DE MACHINE LEARNING - {datetime.now().strftime('%Y-%m-%d')}
    ================================================================
    
    Métricas del Modelo:
    - Accuracy: {accuracy:.3f}
    - Precision: {precision:.3f}
    - Recall: {recall:.3f}
    - F1-Score: {f1:.3f}
    
    Estado de Validación: {'✅ VÁLIDO' if modelo_valido else '❌ INVÁLIDO'}
    Estado de Despliegue: {'✅ EXITOSO' if modelo_valido else '❌ FALLIDO'}
    
    Características Importantes:
    {dict(zip(caracteristicas, modelo.feature_importances_))}
    
    Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    print("\n📋 Reporte de ML generado:")
    print(reporte)
    
    return modelo, validaciones

def ejemplo_dag_monitoreo():
    """
    Ejemplo de DAG de Monitoreo
    """
    print("\n📊 Ejemplo de DAG de Monitoreo")
    print("=" * 50)
    
    # Simular verificaciones de salud
    servicios = {
        'postgres': {
            'estado': 'healthy',
            'version': '15.3',
            'tamaño_mb': 1024.5,
            'conexiones_activas': 25,
            'consultas_activas': 5
        },
        'redis': {
            'estado': 'healthy',
            'version': '7.0.5',
            'memoria_usada_mb': 256.8,
            'conexiones_cliente': 15,
            'comandos_por_segundo': 120
        },
        'api_principal': {
            'estado': 'healthy',
            'url': 'http://api:8000/health',
            'status_code': 200,
            'tiempo_respuesta_ms': 45.2,
            'mensaje': 'OK'
        },
        'api_nlp': {
            'estado': 'warning',
            'url': 'http://nlp-api:8000/health',
            'status_code': 200,
            'tiempo_respuesta_ms': 1250.8,
            'mensaje': 'OK'
        },
        'mlflow': {
            'estado': 'healthy',
            'url': 'http://mlflow:5000/health',
            'status_code': 200,
            'tiempo_respuesta_ms': 78.5,
            'mensaje': 'OK'
        },
        'sistema': {
            'estado': 'warning',
            'cpu_percent': 85.2,
            'memoria_percent': 78.5,
            'disco_percent': 45.8,
            'alerta': 'Uso de CPU alto'
        }
    }
    
    print("🔍 Verificando salud de servicios...")
    
    for servicio, datos in servicios.items():
        estado = datos['estado']
        emoji = {'healthy': '✅', 'warning': '⚠️', 'unhealthy': '❌'}.get(estado, '❓')
        print(f"   • {servicio}: {emoji} {estado.upper()}")
        
        if 'alerta' in datos:
            print(f"     ⚠️  {datos['alerta']}")
    
    # Consolidar resultados
    estados = [datos['estado'] for datos in servicios.values()]
    conteo_estados = {estado: estados.count(estado) for estado in set(estados)}
    
    if 'unhealthy' in estados:
        estado_general = 'critical'
    elif 'warning' in estados:
        estado_general = 'warning'
    else:
        estado_general = 'healthy'
    
    print(f"\n📈 Resumen del Health Check:")
    print(f"   • Estado general: {estado_general.upper()}")
    print(f"   • Total de servicios: {len(servicios)}")
    print(f"   • Distribución: {conteo_estados}")
    
    # Generar reporte
    reporte = f"""
    REPORTE DE HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ================================================================
    
    Estado General: {estado_general.upper()}
    
    Resumen:
    - Total de servicios: {len(servicios)}
    - Estados: {conteo_estados}
    
    Detalles por Servicio:
    """
    
    for servicio, datos in servicios.items():
        reporte += f"\n  {servicio}: {datos['estado']}"
        if 'alerta' in datos:
            reporte += f" - {datos['alerta']}"
        if 'error' in datos:
            reporte += f" - Error: {datos['error']}"
    
    reporte += f"\n\nFecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print("\n📋 Reporte de Health Check generado:")
    print(reporte)
    
    return servicios, estado_general

def ejemplo_operadores_personalizados():
    """
    Ejemplo de operadores personalizados
    """
    print("\n🔧 Ejemplo de Operadores Personalizados")
    print("=" * 50)
    
    # Simular DataQualityOperator
    print("📊 DataQualityOperator - Verificaciones de calidad:")
    
    verificaciones = [
        {
            'nombre': 'Verificación de completitud',
            'tipo': 'count',
            'query': 'SELECT COUNT(*) FROM ventas WHERE total_venta IS NOT NULL',
            'valor_esperado': 100,
            'operador': '>=',
            'tolerancia': 5
        },
        {
            'nombre': 'Verificación de rango de precios',
            'tipo': 'sql',
            'query': 'SELECT MIN(precio_unitario), MAX(precio_unitario) FROM ventas',
            'valor_esperado': (10, 500),
            'operador': '==',
            'tolerancia': 0
        },
        {
            'nombre': 'Verificación de totales',
            'tipo': 'sum',
            'query': 'SELECT SUM(total_venta) FROM ventas',
            'valor_esperado': 50000,
            'operador': '>=',
            'tolerancia': 1000
        }
    ]
    
    for verificacion in verificaciones:
        print(f"   • {verificacion['nombre']}: ✅ VÁLIDA")
    
    print("\n📱 SlackNotificationOperator - Notificaciones:")
    
    notificaciones = [
        {
            'tipo': 'success',
            'canal': '#alerts-success',
            'mensaje': 'ETL de ventas completado exitosamente',
            'emoji': '✅'
        },
        {
            'tipo': 'warning',
            'canal': '#alerts-warning',
            'mensaje': 'Uso de CPU alto detectado',
            'emoji': '⚠️'
        },
        {
            'tipo': 'error',
            'canal': '#alerts-critical',
            'mensaje': 'Error crítico en base de datos',
            'emoji': '🚨'
        }
    ]
    
    for notif in notificaciones:
        print(f"   • {notif['emoji']} {notif['tipo'].upper()}: {notif['mensaje']}")
        print(f"     Canal: {notif['canal']}")

def main():
    """
    Función principal
    """
    print("🎯 Apache Airflow - Ejemplo de Uso")
    print("=" * 60)
    
    try:
        # Ejecutar ejemplos
        df_etl = ejemplo_dag_etl()
        modelo_ml, validaciones_ml = ejemplo_dag_ml()
        servicios_monitoreo, estado_monitoreo = ejemplo_dag_monitoreo()
        ejemplo_operadores_personalizados()
        
        print("\n✅ Todos los ejemplos ejecutados correctamente!")
        print("\n🚀 Para usar Apache Airflow, ejecuta:")
        print("   docker-compose up -d")
        print("   Luego visita: http://localhost:8080")
        print("   Usuario: admin / Contraseña: admin")
        
        print("\n📊 Servicios disponibles:")
        print("   • Airflow Web UI: http://localhost:8080")
        print("   • Flower (Celery): http://localhost:5555")
        print("   • MLflow: http://localhost:5000")
        print("   • Grafana: http://localhost:3000")
        print("   • Prometheus: http://localhost:9090")
        
    except Exception as e:
        print(f"\n❌ Error en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
