"""
Ejemplo de Uso del Sistema de Recomendaciones ML
Demostración de las funcionalidades del sistema de recomendaciones
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import structlog

from aplicacion.servicios.servicio_recomendaciones import ServicioRecomendaciones
from infraestructura.algoritmos.algoritmo_colaborativo import AlgoritmoColaborativo
from dominio.entidades.recomendacion import TipoAlgoritmo, TipoRecomendacion
from dominio.entidades.usuario import Usuario, TipoUsuario, Genero
from dominio.entidades.item import Item, CategoriaItem, EstadoItem


# Configurar logging
logger = structlog.get_logger()

def generar_datos_ejemplo():
    """Generar datos de ejemplo para el sistema"""
    print("📊 Generando datos de ejemplo...")
    
    # Generar datos de usuarios
    usuarios_data = {
        'id_usuario': [f'user_{i:03d}' for i in range(1, 101)],
        'email': [f'usuario{i}@ejemplo.com' for i in range(1, 101)],
        'nombre': [f'Usuario{i}' for i in range(1, 101)],
        'edad': np.random.randint(18, 65, 100),
        'genero': np.random.choice(['masculino', 'femenino', 'otro'], 100),
        'pais': np.random.choice(['Argentina', 'México', 'Colombia', 'España'], 100),
        'fecha_registro': pd.date_range('2020-01-01', periods=100, freq='D')
    }
    
    usuarios_df = pd.DataFrame(usuarios_data)
    
    # Generar datos de items
    items_data = {
        'id_item': [f'item_{i:03d}' for i in range(1, 201)],
        'titulo': [f'Producto {i}' for i in range(1, 201)],
        'categoria': np.random.choice(['electronica', 'ropa', 'hogar', 'deportes', 'libros'], 200),
        'precio': np.random.uniform(10, 500, 200),
        'rating_promedio': np.random.uniform(1, 5, 200),
        'total_ratings': np.random.randint(0, 100, 200),
        'total_ventas': np.random.randint(0, 50, 200),
        'fecha_creacion': pd.date_range('2020-01-01', periods=200, freq='D')
    }
    
    items_df = pd.DataFrame(items_data)
    
    # Generar datos de ratings
    ratings_data = []
    for _ in range(1000):
        usuario_id = f'user_{np.random.randint(1, 101):03d}'
        item_id = f'item_{np.random.randint(1, 201):03d}'
        rating = np.random.randint(1, 6)
        fecha = pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 365))
        
        ratings_data.append({
            'usuario_id': usuario_id,
            'item_id': item_id,
            'rating': rating,
            'fecha': fecha
        })
    
    ratings_df = pd.DataFrame(ratings_data)
    
    print(f"   • Usuarios generados: {len(usuarios_df)}")
    print(f"   • Items generados: {len(items_df)}")
    print(f"   • Ratings generados: {len(ratings_df)}")
    
    return usuarios_df, items_df, ratings_df

async def configurar_servicios():
    """Configurar servicios de recomendaciones"""
    print("🔧 Configurando servicios de recomendaciones...")
    
    # Crear servicio
    servicio_recomendaciones = ServicioRecomendaciones()
    
    # Crear algoritmo colaborativo
    algoritmo_colaborativo = AlgoritmoColaborativo()
    
    # Registrar algoritmo
    servicio_recomendaciones.registrar_algoritmo("colaborativo", algoritmo_colaborativo)
    
    print("✅ Servicios configurados correctamente")
    
    return servicio_recomendaciones, algoritmo_colaborativo

async def ejemplo_entrenamiento(servicio_recomendaciones, algoritmo_colaborativo, ratings_df):
    """Ejemplo de entrenamiento del modelo"""
    print("\n🤖 Ejemplo de Entrenamiento del Modelo")
    print("=" * 50)
    
    try:
        # Preparar datos de entrenamiento
        datos_entrenamiento = {
            'ratings': ratings_df
        }
        
        print("📊 Entrenando modelo colaborativo...")
        
        # Entrenar modelo
        metricas = await servicio_recomendaciones.entrenar_algoritmo(
            algoritmo="colaborativo",
            datos_entrenamiento=datos_entrenamiento
        )
        
        print("✅ Modelo entrenado exitosamente")
        print(f"   • Varianza explicada: {metricas['varianza_explicada']:.3f}")
        print(f"   • Componentes: {metricas['n_components']}")
        print(f"   • Usuarios: {metricas['n_usuarios']}")
        print(f"   • Items: {metricas['n_items']}")
        print(f"   • Sparsity: {metricas['sparsity']:.3f}")
        print(f"   • Total ratings: {metricas['total_ratings']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el entrenamiento: {str(e)}")
        return False

async def ejemplo_recomendaciones_usuario(servicio_recomendaciones):
    """Ejemplo de recomendaciones para usuario"""
    print("\n👤 Ejemplo de Recomendaciones para Usuario")
    print("=" * 50)
    
    # Usuarios de ejemplo
    usuarios_ejemplo = ['user_001', 'user_050', 'user_100']
    
    for usuario_id in usuarios_ejemplo:
        print(f"\n🔍 Generando recomendaciones para {usuario_id}")
        
        try:
            # Generar recomendaciones
            recomendaciones = await servicio_recomendaciones.recomendar_para_usuario(
                usuario_id=usuario_id,
                limit=5
            )
            
            print(f"   • Recomendaciones generadas: {len(recomendaciones)}")
            
            for i, rec in enumerate(recomendaciones, 1):
                print(f"   {i}. {rec.item_id} - Score: {rec.score:.3f} - Confianza: {rec.confianza:.3f}")
                if rec.explicacion:
                    print(f"      Explicación: {rec.explicacion}")
                if rec.razones:
                    print(f"      Razones: {', '.join(rec.razones)}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def ejemplo_recomendaciones_similares(servicio_recomendaciones):
    """Ejemplo de recomendaciones similares"""
    print("\n🔗 Ejemplo de Recomendaciones Similares")
    print("=" * 50)
    
    # Items de ejemplo
    items_ejemplo = ['item_001', 'item_050', 'item_100']
    
    for item_id in items_ejemplo:
        print(f"\n🔍 Generando recomendaciones similares para {item_id}")
        
        try:
            # Generar recomendaciones similares
            recomendaciones = await servicio_recomendaciones.recomendar_similares(
                item_id=item_id,
                limit=3
            )
            
            print(f"   • Items similares encontrados: {len(recomendaciones)}")
            
            for i, rec in enumerate(recomendaciones, 1):
                print(f"   {i}. {rec.item_id} - Similitud: {rec.score:.3f} - Confianza: {rec.confianza:.3f}")
                if rec.explicacion:
                    print(f"      Explicación: {rec.explicacion}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def ejemplo_comparacion_algoritmos(servicio_recomendaciones):
    """Ejemplo de comparación de algoritmos"""
    print("\n⚖️ Ejemplo de Comparación de Algoritmos")
    print("=" * 50)
    
    usuario_id = 'user_001'
    print(f"🔍 Comparando algoritmos para {usuario_id}")
    
    try:
        # Comparar algoritmos
        resultados = await servicio_recomendaciones.comparar_algoritmos(
            usuario_id=usuario_id,
            limit=3,
            algoritmos=['colaborativo']
        )
        
        for algoritmo, recomendaciones in resultados.items():
            print(f"\n📊 Algoritmo: {algoritmo}")
            print(f"   • Recomendaciones: {len(recomendaciones)}")
            
            for i, rec in enumerate(recomendaciones, 1):
                print(f"   {i}. {rec.item_id} - Score: {rec.score:.3f}")
    
    except Exception as e:
        print(f"❌ Error en comparación: {str(e)}")

async def ejemplo_evaluacion_modelo(servicio_recomendaciones, ratings_df):
    """Ejemplo de evaluación del modelo"""
    print("\n📈 Ejemplo de Evaluación del Modelo")
    print("=" * 50)
    
    try:
        # Preparar datos de test (usar una muestra de los ratings)
        datos_test = {
            'ratings': ratings_df.sample(100)  # Muestra de 100 ratings
        }
        
        print("📊 Evaluando modelo colaborativo...")
        
        # Evaluar modelo
        metricas = await servicio_recomendaciones.evaluar_algoritmo(
            algoritmo="colaborativo",
            datos_test=datos_test,
            metricas=['precision', 'recall', 'f1_score', 'coverage', 'diversity']
        )
        
        print("✅ Evaluación completada")
        print(f"   • Precision: {metricas['precision']:.3f}")
        print(f"   • Recall: {metricas['recall']:.3f}")
        print(f"   • F1-Score: {metricas['f1_score']:.3f}")
        print(f"   • Coverage: {metricas['coverage']:.3f}")
        print(f"   • Diversity: {metricas['diversity']:.3f}")
    
    except Exception as e:
        print(f"❌ Error en evaluación: {str(e)}")

async def ejemplo_estadisticas(servicio_recomendaciones):
    """Ejemplo de estadísticas del sistema"""
    print("\n📊 Ejemplo de Estadísticas del Sistema")
    print("=" * 50)
    
    try:
        # Obtener estadísticas generales
        estadisticas = await servicio_recomendaciones.obtener_estadisticas()
        
        print("📈 Estadísticas del Sistema:")
        print(f"   • Algoritmos disponibles: {', '.join(estadisticas['algoritmos_disponibles'])}")
        print(f"   • Algoritmo por defecto: {estadisticas['configuracion']['algoritmo_por_defecto']}")
        print(f"   • Máximo de recomendaciones: {estadisticas['configuracion']['max_recomendaciones']}")
        print(f"   • Confianza mínima: {estadisticas['configuracion']['min_confianza']}")
        print(f"   • Caché habilitado: {estadisticas['configuracion']['cache_habilitado']}")
        
        # Obtener estadísticas específicas de usuario
        estadisticas_usuario = await servicio_recomendaciones.obtener_estadisticas(usuario_id='user_001')
        
        print(f"\n👤 Estadísticas para user_001:")
        print(f"   • Algoritmo preferido: {estadisticas_usuario['usuario']['algoritmo_preferido']}")
    
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {str(e)}")

async def ejemplo_entidades_dominio():
    """Ejemplo de entidades del dominio"""
    print("\n🏗️ Ejemplo de Entidades del Dominio")
    print("=" * 50)
    
    # Crear usuario de ejemplo
    usuario = Usuario(
        id_usuario="user_ejemplo",
        email="ejemplo@test.com",
        nombre="Usuario",
        apellido="Ejemplo",
        edad=30,
        genero=Genero.MASCULINO,
        pais="Argentina",
        ciudad="Buenos Aires",
        tipo_usuario=TipoUsuario.ACTIVO
    )
    
    print("👤 Usuario creado:")
    print(f"   • ID: {usuario.id_usuario}")
    print(f"   • Email: {usuario.email}")
    print(f"   • Nombre completo: {usuario.nombre} {usuario.apellido}")
    print(f"   • Edad: {usuario.edad}")
    print(f"   • Género: {usuario.genero.value}")
    print(f"   • Ubicación: {usuario.ciudad}, {usuario.pais}")
    print(f"   • Tipo: {usuario.tipo_usuario.value}")
    print(f"   • Días de registro: {usuario.calcular_dias_registro()}")
    print(f"   • Nivel de actividad: {usuario.calcular_nivel_actividad()}")
    print(f"   • Valor del usuario: {usuario.calcular_valor_usuario():.3f}")
    
    # Crear item de ejemplo
    item = Item(
        id_item="item_ejemplo",
        titulo="Producto de Ejemplo",
        descripcion="Un producto de ejemplo para demostración",
        categoria=CategoriaItem.ELECTRONICA,
        precio=299.99,
        precio_original=399.99,
        descuento=100.00,
        stock=50,
        estado=EstadoItem.ACTIVO,
        rating_promedio=4.5,
        total_ratings=25,
        total_ventas=100,
        total_vistas=500
    )
    
    print(f"\n📦 Item creado:")
    print(f"   • ID: {item.id_item}")
    print(f"   • Título: {item.titulo}")
    print(f"   • Categoría: {item.categoria.value}")
    print(f"   • Precio: ${item.precio:.2f}")
    print(f"   • Descuento: {item.calcular_porcentaje_descuento():.1f}%")
    print(f"   • Stock: {item.stock}")
    print(f"   • Estado: {item.estado.value}")
    print(f"   • Rating: {item.rating_promedio}/5 ({item.total_ratings} reseñas)")
    print(f"   • Popularidad: {item.calcular_popularidad():.3f}")
    print(f"   • Nivel de precio: {item.obtener_nivel_precio()}")
    print(f"   • Nivel de rating: {item.obtener_nivel_rating()}")
    
    # Crear recomendación de ejemplo
    from dominio.entidades.recomendacion import Recomendacion, TipoAlgoritmo, TipoRecomendacion
    
    recomendacion = Recomendacion(
        item_id="item_ejemplo",
        usuario_id="user_ejemplo",
        score=4.2,
        ranking=1,
        algoritmo_usado=TipoAlgoritmo.COLABORATIVO,
        tipo_recomendacion=TipoRecomendacion.USUARIO,
        titulo="Producto de Ejemplo",
        categoria="electronica",
        precio=299.99,
        explicacion="Recomendado basado en usuarios similares",
        razones=["Basado en usuarios con gustos similares", "Patrones de comportamiento compartidos"],
        confianza=0.85
    )
    
    print(f"\n🎯 Recomendación creada:")
    print(f"   • Item: {recomendacion.item_id}")
    print(f"   • Usuario: {recomendacion.usuario_id}")
    print(f"   • Score: {recomendacion.score}")
    print(f"   • Ranking: {recomendacion.ranking}")
    print(f"   • Algoritmo: {recomendacion.algoritmo_usado.value}")
    print(f"   • Tipo: {recomendacion.tipo_recomendacion.value}")
    print(f"   • Confianza: {recomendacion.confianza:.3f}")
    print(f"   • Nivel de confianza: {recomendacion.obtener_nivel_confianza()}")
    print(f"   • Explicación: {recomendacion.obtener_explicacion_completa()}")
    print(f"   • Relevancia: {recomendacion.calcular_relevancia():.3f}")
    print(f"   • Válida: {recomendacion.es_valida()}")

async def main():
    """Función principal"""
    print("🎯 Sistema de Recomendaciones ML - Ejemplo de Uso")
    print("=" * 60)
    
    try:
        # Generar datos de ejemplo
        usuarios_df, items_df, ratings_df = generar_datos_ejemplo()
        
        # Configurar servicios
        servicio_recomendaciones, algoritmo_colaborativo = await configurar_servicios()
        
        # Ejecutar ejemplos
        await ejemplo_entidades_dominio()
        
        # Entrenar modelo
        entrenamiento_exitoso = await ejemplo_entrenamiento(servicio_recomendaciones, algoritmo_colaborativo, ratings_df)
        
        if entrenamiento_exitoso:
            await ejemplo_recomendaciones_usuario(servicio_recomendaciones)
            await ejemplo_recomendaciones_similares(servicio_recomendaciones)
            await ejemplo_comparacion_algoritmos(servicio_recomendaciones)
            await ejemplo_evaluacion_modelo(servicio_recomendaciones, ratings_df)
        
        await ejemplo_estadisticas(servicio_recomendaciones)
        
        print("\n✅ Todos los ejemplos ejecutados correctamente!")
        print("\n🚀 Para usar la API REST, ejecuta:")
        print("   python -m presentacion.api.aplicacion")
        print("   Luego visita: http://localhost:8000/docs")
        
        print("\n📊 Servicios disponibles:")
        print("   • API REST: http://localhost:8000")
        print("   • Dashboard: http://localhost:8501")
        print("   • MLflow: http://localhost:5000")
        print("   • Grafana: http://localhost:3000")
        print("   • Prometheus: http://localhost:9090")
        
    except Exception as e:
        print(f"\n❌ Error en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
