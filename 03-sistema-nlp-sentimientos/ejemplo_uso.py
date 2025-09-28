"""
Ejemplo de Uso del Sistema NLP
Demostración de las funcionalidades del sistema de análisis de sentimientos y entidades
"""
import asyncio
import json
from datetime import datetime

from aplicacion.servicios.servicio_sentimientos import ServicioSentimientos
from aplicacion.servicios.servicio_entidades import ServicioEntidades
from infraestructura.algoritmos.spacy_sentimientos import AlgoritmoSpacySentimientos
from infraestructura.algoritmos.spacy_entidades import AlgoritmoSpacyEntidades


async def configurar_servicios():
    """Configurar servicios de NLP"""
    print("🔧 Configurando servicios de NLP...")
    
    # Crear servicios
    servicio_sentimientos = ServicioSentimientos()
    servicio_entidades = ServicioEntidades()
    
    # Crear algoritmos
    algoritmo_sentimientos = AlgoritmoSpacySentimientos()
    algoritmo_entidades = AlgoritmoSpacyEntidades()
    
    # Registrar algoritmos
    servicio_sentimientos.registrar_algoritmo("spacy", algoritmo_sentimientos)
    servicio_entidades.registrar_algoritmo("spacy", algoritmo_entidades)
    
    print("✅ Servicios configurados correctamente")
    
    return servicio_sentimientos, servicio_entidades


async def ejemplo_analisis_sentimientos(servicio_sentimientos):
    """Ejemplo de análisis de sentimientos"""
    print("\n📊 Ejemplo de Análisis de Sentimientos")
    print("=" * 50)
    
    # Textos de ejemplo en diferentes idiomas
    textos_ejemplo = [
        {
            "texto": "Este producto es excelente, lo recomiendo totalmente. La calidad es increíble y el servicio al cliente es fantástico.",
            "idioma": "es",
            "descripcion": "Texto positivo en español"
        },
        {
            "texto": "I love this new feature! It's amazing and works perfectly. Great job team!",
            "idioma": "en",
            "descripcion": "Texto positivo en inglés"
        },
        {
            "texto": "No me gusta nada este servicio. Es terrible, muy lento y el soporte es pésimo. No lo recomiendo.",
            "idioma": "es",
            "descripcion": "Texto negativo en español"
        },
        {
            "texto": "The weather is nice today. It's sunny and warm.",
            "idioma": "en",
            "descripcion": "Texto neutral en inglés"
        }
    ]
    
    for ejemplo in textos_ejemplo:
        print(f"\n📝 {ejemplo['descripcion']}")
        print(f"Texto: {ejemplo['texto']}")
        
        try:
            # Analizar sentimiento
            resultado = await servicio_sentimientos.analizar_sentimiento(
                texto=ejemplo['texto'],
                idioma=ejemplo['idioma']
            )
            
            # Mostrar resultados
            print(f"   • Categoría: {resultado.categoria.value}")
            print(f"   • Polaridad: {resultado.polaridad:.3f}")
            print(f"   • Subjetividad: {resultado.subjetividad:.3f}")
            print(f"   • Confianza: {resultado.confianza:.3f}")
            print(f"   • Intensidad: {resultado.obtener_intensidad()}")
            print(f"   • Resumen: {resultado.obtener_resumen()}")
            
            if resultado.palabras_clave:
                print(f"   • Palabras clave: {', '.join(resultado.palabras_clave[:5])}")
            
            if resultado.emociones_detectadas:
                emocion_principal = resultado.obtener_emocion_principal()
                if emocion_principal:
                    print(f"   • Emoción principal: {emocion_principal}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


async def ejemplo_extraccion_entidades(servicio_entidades):
    """Ejemplo de extracción de entidades"""
    print("\n🏷️ Ejemplo de Extracción de Entidades")
    print("=" * 50)
    
    # Textos de ejemplo con entidades
    textos_ejemplo = [
        {
            "texto": "Apple Inc. fue fundada por Steve Jobs en Cupertino, California en 1976. La empresa tiene su sede en Estados Unidos.",
            "idioma": "es",
            "descripcion": "Texto con personas, organizaciones y lugares"
        },
        {
            "texto": "Microsoft Corporation, fundada por Bill Gates y Paul Allen en 1975, tiene su sede en Redmond, Washington.",
            "idioma": "es",
            "descripcion": "Texto con múltiples entidades"
        },
        {
            "texto": "The meeting is scheduled for January 15, 2024 at 3:00 PM. The budget is $50,000 and we expect 80% completion.",
            "idioma": "en",
            "descripcion": "Texto con fechas, dinero y porcentajes"
        }
    ]
    
    for ejemplo in textos_ejemplo:
        print(f"\n📝 {ejemplo['descripcion']}")
        print(f"Texto: {ejemplo['texto']}")
        
        try:
            # Extraer entidades
            entidades = await servicio_entidades.extraer_entidades(
                texto=ejemplo['texto'],
                idioma=ejemplo['idioma']
            )
            
            print(f"   • Entidades encontradas: {len(entidades)}")
            
            # Agrupar por tipo
            tipos_entidades = {}
            for entidad in entidades:
                tipo = entidad.tipo.value
                if tipo not in tipos_entidades:
                    tipos_entidades[tipo] = []
                tipos_entidades[tipo].append(entidad)
            
            # Mostrar por tipo
            for tipo, entidades_tipo in tipos_entidades.items():
                print(f"   • {tipo}:")
                for entidad in entidades_tipo:
                    print(f"     - '{entidad.texto}' (confianza: {entidad.confianza:.3f})")
            
            # Mostrar entidades más importantes
            entidades_importantes = sorted(
                entidades, 
                key=lambda e: e.calcular_puntuacion_compuesta(), 
                reverse=True
            )[:3]
            
            if entidades_importantes:
                print(f"   • Entidades más importantes:")
                for entidad in entidades_importantes:
                    print(f"     - '{entidad.texto}' ({entidad.tipo.value}) - {entidad.obtener_importancia()}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


async def ejemplo_analisis_completo(servicio_sentimientos, servicio_entidades):
    """Ejemplo de análisis completo"""
    print("\n🔍 Ejemplo de Análisis Completo")
    print("=" * 50)
    
    texto_ejemplo = """
    Apple Inc. ha lanzado su nuevo iPhone 15 con características increíbles. 
    El CEO Tim Cook anunció que las ventas han superado todas las expectativas. 
    El producto estará disponible en Estados Unidos, Canadá y México a partir del 15 de septiembre de 2024. 
    El precio será de $999 USD y los analistas predicen que será un éxito rotundo.
    """
    
    print(f"📝 Texto a analizar:")
    print(f"   {texto_ejemplo.strip()}")
    
    try:
        # Análisis de sentimientos
        print(f"\n📊 Análisis de Sentimientos:")
        resultado_sentimientos = await servicio_sentimientos.analizar_sentimiento(
            texto=texto_ejemplo,
            idioma="es"
        )
        
        print(f"   • Categoría: {resultado_sentimientos.categoria.value}")
        print(f"   • Polaridad: {resultado_sentimientos.polaridad:.3f}")
        print(f"   • Subjetividad: {resultado_sentimientos.subjetividad:.3f}")
        print(f"   • Confianza: {resultado_sentimientos.confianza:.3f}")
        
        # Extracción de entidades
        print(f"\n🏷️ Extracción de Entidades:")
        entidades = await servicio_entidades.extraer_entidades(
            texto=texto_ejemplo,
            idioma="es"
        )
        
        print(f"   • Total de entidades: {len(entidades)}")
        
        # Mostrar entidades por tipo
        tipos_entidades = {}
        for entidad in entidades:
            tipo = entidad.tipo.value
            if tipo not in tipos_entidades:
                tipos_entidades[tipo] = []
            tipos_entidades[tipo].append(entidad)
        
        for tipo, entidades_tipo in tipos_entidades.items():
            print(f"   • {tipo}: {len(entidades_tipo)} entidades")
            for entidad in entidades_tipo[:3]:  # Mostrar solo las primeras 3
                print(f"     - '{entidad.texto}' (confianza: {entidad.confianza:.3f})")
        
        # Estadísticas del análisis
        print(f"\n📈 Estadísticas del Análisis:")
        print(f"   • Complejidad: {len(texto_ejemplo)} caracteres")
        print(f"   • Entidades confiables: {len([e for e in entidades if e.es_confiable()])}")
        print(f"   • Sentimiento confiable: {'Sí' if resultado_sentimientos.es_confiable() else 'No'}")
        
        # Resumen ejecutivo
        print(f"\n📋 Resumen Ejecutivo:")
        print(f"   • Sentimiento: {resultado_sentimientos.obtener_resumen()}")
        print(f"   • Entidades principales: {', '.join([e.texto for e in entidades[:5]])}")
        print(f"   • Análisis completo: ✅")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


async def ejemplo_analisis_lote(servicio_sentimientos, servicio_entidades):
    """Ejemplo de análisis en lote"""
    print("\n📦 Ejemplo de Análisis en Lote")
    print("=" * 50)
    
    # Textos para análisis en lote
    textos_lote = [
        "Este producto es fantástico, lo recomiendo totalmente.",
        "No me gusta nada, es terrible y muy caro.",
        "La calidad está bien, pero podría ser mejor.",
        "Excelente servicio al cliente, muy profesional.",
        "El envío fue lento y el producto llegó dañado."
    ]
    
    print(f"📝 Analizando {len(textos_lote)} textos en lote...")
    
    try:
        # Análisis de sentimientos en lote
        resultados_sentimientos = await servicio_sentimientos.analizar_sentimientos_lote(
            textos=textos_lote,
            idioma="es"
        )
        
        print(f"\n📊 Resultados de Sentimientos:")
        for i, resultado in enumerate(resultados_sentimientos):
            print(f"   {i+1}. {resultado.categoria.value} (polaridad: {resultado.polaridad:.3f})")
        
        # Extracción de entidades en lote
        resultados_entidades = await servicio_entidades.extraer_entidades_lote(
            textos=textos_lote,
            idioma="es"
        )
        
        print(f"\n🏷️ Resultados de Entidades:")
        for i, entidades in enumerate(resultados_entidades):
            print(f"   {i+1}. {len(entidades)} entidades encontradas")
        
        # Estadísticas generales
        print(f"\n📈 Estadísticas Generales:")
        categorias = [r.categoria.value for r in resultados_sentimientos]
        from collections import Counter
        distribucion = Counter(categorias)
        print(f"   • Distribución de sentimientos: {dict(distribucion)}")
        
        total_entidades = sum(len(ents) for ents in resultados_entidades)
        print(f"   • Total de entidades: {total_entidades}")
        
        polaridad_promedio = sum(r.polaridad for r in resultados_sentimientos) / len(resultados_sentimientos)
        print(f"   • Polaridad promedio: {polaridad_promedio:.3f}")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


async def main():
    """Función principal"""
    print("🎯 Sistema NLP - Ejemplo de Uso")
    print("=" * 60)
    
    try:
        # Configurar servicios
        servicio_sentimientos, servicio_entidades = await configurar_servicios()
        
        # Ejecutar ejemplos
        await ejemplo_analisis_sentimientos(servicio_sentimientos)
        await ejemplo_extraccion_entidades(servicio_entidades)
        await ejemplo_analisis_completo(servicio_sentimientos, servicio_entidades)
        await ejemplo_analisis_lote(servicio_sentimientos, servicio_entidades)
        
        print("\n✅ Todos los ejemplos ejecutados correctamente!")
        print("\n🚀 Para usar la API REST, ejecuta:")
        print("   python -m presentacion.api.aplicacion")
        print("   Luego visita: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error en la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
