"""
Algoritmo de Sentimientos con spaCy - Infraestructura
Implementación concreta usando spaCy para análisis de sentimientos
"""
import spacy
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from dominio.algoritmos.algoritmo_sentimientos import AlgoritmoSentimientos
from dominio.entidades.analisis_sentimiento import AnalisisSentimiento, CategoriaSentimiento, ModeloSentimiento


class AlgoritmoSpacySentimientos(AlgoritmoSentimientos):
    """
    Implementación de análisis de sentimientos usando spaCy
    Utiliza modelos pre-entrenados de spaCy
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar algoritmo de spaCy
        
        Args:
            configuracion: Configuración específica del algoritmo
        """
        super().__init__("spacy", configuracion)
        
        # Configuración por defecto
        self.configuracion_default = {
            "modelo_es": "es_core_news_sm",
            "modelo_en": "en_core_web_sm",
            "modelo_fr": "fr_core_news_sm",
            "modelo_de": "de_core_news_sm",
            "cargar_modelos": True,
            "usar_pipe_sentimientos": True
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
        
        # Modelos cargados
        self.modelos: Dict[str, spacy.Language] = {}
        
        # Cargar modelos si está habilitado
        if self.configuracion_final["cargar_modelos"]:
            self._cargar_modelos()
    
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del algoritmo
        
        Returns:
            True si la configuración es válida
        """
        # Verificar que los modelos están disponibles
        modelos_requeridos = [
            self.configuracion_final["modelo_es"],
            self.configuracion_final["modelo_en"],
            self.configuracion_final["modelo_fr"],
            self.configuracion_final["modelo_de"]
        ]
        
        for modelo in modelos_requeridos:
            try:
                spacy.load(modelo)
            except OSError:
                self.logger.warning(f"Modelo spaCy no encontrado: {modelo}")
                return False
        
        return True
    
    def _cargar_modelos(self) -> None:
        """Cargar modelos de spaCy"""
        try:
            # Cargar modelo español
            self.modelos["es"] = spacy.load(self.configuracion_final["modelo_es"])
            self.logger.info(f"Modelo español cargado: {self.configuracion_final['modelo_es']}")
            
            # Cargar modelo inglés
            self.modelos["en"] = spacy.load(self.configuracion_final["modelo_en"])
            self.logger.info(f"Modelo inglés cargado: {self.configuracion_final['modelo_en']}")
            
            # Cargar modelo francés
            self.modelos["fr"] = spacy.load(self.configuracion_final["modelo_fr"])
            self.logger.info(f"Modelo francés cargado: {self.configuracion_final['modelo_fr']}")
            
            # Cargar modelo alemán
            self.modelos["de"] = spacy.load(self.configuracion_final["modelo_de"])
            self.logger.info(f"Modelo alemán cargado: {self.configuracion_final['modelo_de']}")
            
        except Exception as e:
            self.logger.error(f"Error cargando modelos spaCy: {str(e)}")
            raise
    
    def _obtener_modelo(self, idioma: str) -> spacy.Language:
        """
        Obtener modelo de spaCy para un idioma
        
        Args:
            idioma: Código del idioma
            
        Returns:
            Modelo de spaCy
        """
        # Mapear idiomas a códigos de modelo
        mapeo_idiomas = {
            "es": "es",
            "en": "en",
            "fr": "fr",
            "de": "de"
        }
        
        codigo_modelo = mapeo_idiomas.get(idioma, "es")
        
        if codigo_modelo not in self.modelos:
            # Cargar modelo bajo demanda
            try:
                if codigo_modelo == "es":
                    self.modelos["es"] = spacy.load(self.configuracion_final["modelo_es"])
                elif codigo_modelo == "en":
                    self.modelos["en"] = spacy.load(self.configuracion_final["modelo_en"])
                elif codigo_modelo == "fr":
                    self.modelos["fr"] = spacy.load(self.configuracion_final["modelo_fr"])
                elif codigo_modelo == "de":
                    self.modelos["de"] = spacy.load(self.configuracion_final["modelo_de"])
            except Exception as e:
                self.logger.error(f"Error cargando modelo {codigo_modelo}: {str(e)}")
                # Usar modelo por defecto
                codigo_modelo = "es"
        
        return self.modelos[codigo_modelo]
    
    async def analizar(self, texto: str, idioma: str = "es") -> AnalisisSentimiento:
        """
        Analizar sentimientos de un texto usando spaCy
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            
        Returns:
            Resultado del análisis de sentimientos
        """
        try:
            # Obtener modelo
            modelo = self._obtener_modelo(idioma)
            
            # Procesar texto
            doc = modelo(texto)
            
            # Calcular polaridad y subjetividad
            polaridad, subjetividad = self._calcular_sentimientos_spacy(doc)
            
            # Categorizar sentimiento
            categoria = self._categorizar_sentimiento(polaridad, subjetividad)
            
            # Calcular confianza y calidad
            confianza = self._calcular_confianza(polaridad, subjetividad)
            calidad = self._calcular_calidad(texto, polaridad)
            
            # Extraer palabras clave
            palabras_clave = self._extraer_palabras_clave_spacy(doc)
            
            # Detectar emociones
            emociones = self._detectar_emociones(texto)
            
            # Crear resultado
            resultado = AnalisisSentimiento(
                texto=texto,
                idioma=idioma,
                modelo_usado=ModeloSentimiento.SPACY,
                polaridad=polaridad,
                subjetividad=subjetividad,
                categoria=categoria,
                confianza=confianza,
                calidad_analisis=calidad,
                palabras_clave=palabras_clave,
                emociones_detectadas=emociones,
                fecha_analisis=datetime.utcnow(),
                tiempo_procesamiento_ms=0.0,  # Se calculará externamente
                version_modelo=self.configuracion_final.get(f"modelo_{idioma}")
            )
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en análisis spaCy: {str(e)}")
            raise
    
    def _calcular_sentimientos_spacy(self, doc: spacy.tokens.Doc) -> tuple[float, float]:
        """
        Calcular sentimientos usando spaCy
        
        Args:
            doc: Documento procesado por spaCy
            
        Returns:
            Tupla con (polaridad, subjetividad)
        """
        # Implementación básica usando características de spaCy
        # En una implementación real, se usaría un modelo de sentimientos entrenado
        
        polaridad = 0.0
        subjetividad = 0.0
        
        # Contar palabras positivas y negativas
        palabras_positivas = 0
        palabras_negativas = 0
        palabras_totales = 0
        
        # Listas de palabras de sentimiento (se pueden expandir)
        palabras_positivas_lista = [
            'bueno', 'excelente', 'fantástico', 'genial', 'perfecto', 'maravilloso',
            'increíble', 'asombroso', 'magnífico', 'estupendo', 'formidable',
            'good', 'excellent', 'fantastic', 'great', 'perfect', 'wonderful',
            'amazing', 'awesome', 'magnificent', 'terrific', 'outstanding'
        ]
        
        palabras_negativas_lista = [
            'malo', 'terrible', 'horrible', 'pésimo', 'fatal', 'desastroso',
            'abominable', 'atroz', 'espantoso', 'repugnante', 'odioso',
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hateful',
            'atrocious', 'abominable', 'repugnant', 'odious'
        ]
        
        for token in doc:
            if not token.is_stop and not token.is_punct and token.is_alpha:
                palabras_totales += 1
                token_text = token.text.lower()
                
                if token_text in palabras_positivas_lista:
                    palabras_positivas += 1
                elif token_text in palabras_negativas_lista:
                    palabras_negativas += 1
        
        if palabras_totales > 0:
            # Calcular polaridad basada en la diferencia de palabras
            diferencia = palabras_positivas - palabras_negativas
            polaridad = diferencia / palabras_totales
            
            # Normalizar a rango [-1, 1]
            polaridad = max(-1.0, min(1.0, polaridad))
            
            # Calcular subjetividad basada en la presencia de palabras de sentimiento
            palabras_sentimiento = palabras_positivas + palabras_negativas
            subjetividad = min(1.0, palabras_sentimiento / palabras_totales)
        
        return polaridad, subjetividad
    
    def _extraer_palabras_clave_spacy(self, doc: spacy.tokens.Doc, limite: int = 10) -> List[str]:
        """
        Extraer palabras clave usando spaCy
        
        Args:
            doc: Documento procesado por spaCy
            limite: Número máximo de palabras clave
            
        Returns:
            Lista de palabras clave
        """
        palabras_clave = []
        
        # Extraer sustantivos y adjetivos como palabras clave
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                palabras_clave.append(token.text.lower())
        
        # Contar frecuencia
        frecuencia = {}
        for palabra in palabras_clave:
            frecuencia[palabra] = frecuencia.get(palabra, 0) + 1
        
        # Ordenar por frecuencia y devolver las más frecuentes
        palabras_ordenadas = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)
        
        return [palabra for palabra, _ in palabras_ordenadas[:limite]]
    
    def _analizar_entidades_sentimiento(self, doc: spacy.tokens.Doc) -> Dict[str, float]:
        """
        Analizar sentimientos de entidades específicas
        
        Args:
            doc: Documento procesado por spaCy
            
        Returns:
            Diccionario con sentimientos por entidad
        """
        sentimientos_entidades = {}
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE']:
                # Analizar contexto de la entidad
                contexto = self._obtener_contexto_entidad(doc, ent.start, ent.end)
                polaridad, _ = self._calcular_sentimientos_spacy(contexto)
                sentimientos_entidades[ent.text] = polaridad
        
        return sentimientos_entidades
    
    def _obtener_contexto_entidad(
        self, 
        doc: spacy.tokens.Doc, 
        inicio: int, 
        fin: int, 
        ventana: int = 5
    ) -> spacy.tokens.Doc:
        """
        Obtener contexto de una entidad
        
        Args:
            doc: Documento completo
            inicio: Índice de inicio de la entidad
            fin: Índice de fin de la entidad
            ventana: Tamaño de la ventana de contexto
            
        Returns:
            Documento con contexto de la entidad
        """
        # Expandir ventana
        inicio_contexto = max(0, inicio - ventana)
        fin_contexto = min(len(doc), fin + ventana)
        
        # Crear nuevo documento con el contexto
        tokens_contexto = list(doc[inicio_contexto:fin_contexto])
        
        # Crear nuevo documento (simplificado)
        return doc[inicio_contexto:fin_contexto]
    
    def obtener_estadisticas_modelo(self, idioma: str) -> Dict[str, Any]:
        """
        Obtener estadísticas del modelo para un idioma
        
        Args:
            idioma: Código del idioma
            
        Returns:
            Diccionario con estadísticas del modelo
        """
        try:
            modelo = self._obtener_modelo(idioma)
            
            return {
                "idioma": idioma,
                "nombre_modelo": modelo.meta.get("name", "unknown"),
                "version": modelo.meta.get("version", "unknown"),
                "pipeline": modelo.pipe_names,
                "vocab_size": len(modelo.vocab),
                "cargado": True
            }
        except Exception as e:
            return {
                "idioma": idioma,
                "error": str(e),
                "cargado": False
            }
