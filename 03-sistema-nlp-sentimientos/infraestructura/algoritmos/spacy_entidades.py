"""
Algoritmo de Extracción de Entidades con spaCy - Infraestructura
Implementación concreta usando spaCy para extracción de entidades
"""
import spacy
from typing import Dict, Any, List, Optional, Tuple
import structlog
from datetime import datetime

from ...dominio.algoritmos.algoritmo_entidades import AlgoritmoEntidades
from ...dominio.entidades.entidad_nombrada import EntidadNombrada, TipoEntidad


class AlgoritmoSpacyEntidades(AlgoritmoEntidades):
    """
    Implementación de extracción de entidades usando spaCy
    Utiliza modelos pre-entrenados de spaCy para NER
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
            "incluir_contexto": True,
            "ventana_contexto": 50,
            "incluir_dependencias": False,
            "filtro_duplicados": True
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
    
    async def extraer(self, texto: str, idioma: str = "es") -> List[EntidadNombrada]:
        """
        Extraer entidades de un texto usando spaCy
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            
        Returns:
            Lista de entidades extraídas
        """
        try:
            # Obtener modelo
            modelo = self._obtener_modelo(idioma)
            
            # Procesar texto
            doc = modelo(texto)
            
            # Extraer entidades
            entidades = []
            
            for ent in doc.ents:
                # Mapear tipo de entidad
                tipo_entidad = self._mapear_tipo_entidad(ent.label_)
                
                # Calcular confianza
                confianza = self._calcular_confianza_entidad_spacy(ent, doc)
                
                # Calcular calidad
                calidad = self._calcular_calidad_entidad_spacy(ent, doc)
                
                # Obtener contexto si está habilitado
                contexto_anterior = None
                contexto_posterior = None
                oracion_completa = None
                
                if self.configuracion_final["incluir_contexto"]:
                    contexto_anterior, contexto_posterior = self._obtener_contexto_entidad_spacy(
                        doc, ent.start_char, ent.end_char
                    )
                    oracion_completa = self._obtener_oracion_completa_spacy(doc, ent.start_char)
                
                # Obtener lema y POS tag
                lema = ent.lemma_ if hasattr(ent, 'lemma_') else None
                etiqueta_pos = None
                
                # Obtener dependencias si está habilitado
                dependencias = []
                if self.configuracion_final["incluir_dependencias"]:
                    dependencias = self._obtener_dependencias_entidad_spacy(ent, doc)
                
                # Crear entidad
                entidad = EntidadNombrada(
                    texto=ent.text,
                    tipo=tipo_entidad,
                    inicio=ent.start_char,
                    fin=ent.end_char,
                    confianza=confianza,
                    calidad_extraccion=calidad,
                    contexto_anterior=contexto_anterior,
                    contexto_posterior=contexto_posterior,
                    oracion_completa=oracion_completa,
                    lema=lema,
                    etiqueta_pos=etiqueta_pos,
                    dependencias=dependencias,
                    modelo_usado="spacy",
                    fecha_extraccion=datetime.utcnow(),
                    version_modelo=self.configuracion_final.get(f"modelo_{idioma}")
                )
                
                entidades.append(entidad)
            
            # Filtrar duplicados si está habilitado
            if self.configuracion_final["filtro_duplicados"]:
                entidades = self._filtrar_entidades_duplicadas(entidades)
            
            return entidades
            
        except Exception as e:
            self.logger.error(f"Error en extracción spaCy: {str(e)}")
            raise
    
    def _calcular_confianza_entidad_spacy(
        self, 
        entidad: spacy.tokens.Span, 
        doc: spacy.tokens.Doc
    ) -> float:
        """
        Calcular confianza de una entidad usando spaCy
        
        Args:
            entidad: Entidad extraída por spaCy
            doc: Documento procesado
            
        Returns:
            Valor de confianza (0.0 a 1.0)
        """
        # spaCy no proporciona confianza directamente, así que la calculamos
        factores = []
        
        # Factor de longitud
        longitud = len(entidad.text)
        factor_longitud = min(1.0, longitud / 20)  # Normalizar a 20 caracteres
        factores.append(factor_longitud)
        
        # Factor de capitalización apropiada
        if entidad.label_ in ['PERSON', 'ORG', 'GPE']:
            if entidad.text.istitle() or entidad.text.isupper():
                factores.append(1.0)
            else:
                factores.append(0.7)
        else:
            factores.append(0.8)
        
        # Factor de contexto (palabras alrededor)
        contexto_score = self._evaluar_contexto_entidad_spacy(entidad, doc)
        factores.append(contexto_score)
        
        # Factor de consistencia con el modelo
        consistencia_score = self._evaluar_consistencia_entidad_spacy(entidad, doc)
        factores.append(consistencia_score)
        
        return sum(factores) / len(factores)
    
    def _calcular_calidad_entidad_spacy(
        self, 
        entidad: spacy.tokens.Span, 
        doc: spacy.tokens.Doc
    ) -> float:
        """
        Calcular calidad de una entidad usando spaCy
        
        Args:
            entidad: Entidad extraída por spaCy
            doc: Documento procesado
            
        Returns:
            Valor de calidad (0.0 a 1.0)
        """
        factores = []
        
        # Factor de formato
        factor_formato = self._evaluar_formato_entidad(entidad.text, self._mapear_tipo_entidad(entidad.label_))
        factores.append(factor_formato)
        
        # Factor de coherencia semántica
        coherencia = self._evaluar_coherencia_semantica_spacy(entidad, doc)
        factores.append(coherencia)
        
        # Factor de frecuencia en el documento
        frecuencia = self._calcular_frecuencia_entidad_spacy(entidad.text, doc)
        factores.append(frecuencia)
        
        return sum(factores) / len(factores)
    
    def _evaluar_contexto_entidad_spacy(
        self, 
        entidad: spacy.tokens.Span, 
        doc: spacy.tokens.Doc
    ) -> float:
        """
        Evaluar contexto de una entidad
        
        Args:
            entidad: Entidad extraída
            doc: Documento procesado
            
        Returns:
            Puntuación de contexto (0.0 a 1.0)
        """
        # Obtener tokens alrededor de la entidad
        inicio = max(0, entidad.start - 3)
        fin = min(len(doc), entidad.end + 3)
        contexto_tokens = doc[inicio:fin]
        
        # Verificar palabras clave en el contexto
        palabras_clave_positivas = ['el', 'la', 'de', 'en', 'con', 'por', 'para']
        palabras_clave_negativas = ['no', 'sin', 'contra', 'anti']
        
        puntuacion = 0.5  # Base
        
        for token in contexto_tokens:
            if token.text.lower() in palabras_clave_positivas:
                puntuacion += 0.1
            elif token.text.lower() in palabras_clave_negativas:
                puntuacion -= 0.1
        
        return max(0.0, min(1.0, puntuacion))
    
    def _evaluar_consistencia_entidad_spacy(
        self, 
        entidad: spacy.tokens.Span, 
        doc: spacy.tokens.Doc
    ) -> float:
        """
        Evaluar consistencia de una entidad con el modelo
        
        Args:
            entidad: Entidad extraída
            doc: Documento procesado
            
        Returns:
            Puntuación de consistencia (0.0 a 1.0)
        """
        # Verificar si la entidad tiene características típicas de su tipo
        tipo = entidad.label_
        texto = entidad.text
        
        puntuacion = 0.5  # Base
        
        if tipo == 'PERSON':
            # Verificar si parece un nombre de persona
            if texto.istitle() and len(texto.split()) >= 2:
                puntuacion += 0.3
            if any(char.isdigit() for char in texto):
                puntuacion -= 0.2
        
        elif tipo == 'ORG':
            # Verificar si parece una organización
            if any(palabra in texto.upper() for palabra in ['INC', 'CORP', 'LTD', 'S.A.', 'S.L.']):
                puntuacion += 0.3
            if texto.istitle():
                puntuacion += 0.2
        
        elif tipo == 'GPE':
            # Verificar si parece un lugar
            if texto.istitle():
                puntuacion += 0.2
            if any(palabra in texto.upper() for palabra in ['CIUDAD', 'PAÍS', 'ESTADO', 'REGIÓN']):
                puntuacion += 0.3
        
        return max(0.0, min(1.0, puntuacion))
    
    def _evaluar_coherencia_semantica_spacy(
        self, 
        entidad: spacy.tokens.Span, 
        doc: spacy.tokens.Doc
    ) -> float:
        """
        Evaluar coherencia semántica de una entidad
        
        Args:
            entidad: Entidad extraída
            doc: Documento procesado
            
        Returns:
            Puntuación de coherencia (0.0 a 1.0)
        """
        # Verificar si la entidad tiene sentido en el contexto
        puntuacion = 0.5  # Base
        
        # Verificar si no contiene solo puntuación
        if entidad.text.replace('.', '').replace(',', '').replace('!', '').replace('?', '').strip():
            puntuacion += 0.2
        
        # Verificar si tiene al menos una letra
        if any(c.isalpha() for c in entidad.text):
            puntuacion += 0.2
        
        # Verificar longitud apropiada
        if 2 <= len(entidad.text) <= 50:
            puntuacion += 0.1
        
        return max(0.0, min(1.0, puntuacion))
    
    def _calcular_frecuencia_entidad_spacy(
        self, 
        texto_entidad: str, 
        doc: spacy.tokens.Doc
    ) -> float:
        """
        Calcular frecuencia de una entidad en el documento
        
        Args:
            texto_entidad: Texto de la entidad
            doc: Documento procesado
            
        Returns:
            Factor de frecuencia (0.0 a 1.0)
        """
        # Contar ocurrencias de la entidad
        ocurrencias = 0
        for ent in doc.ents:
            if ent.text.lower() == texto_entidad.lower():
                ocurrencias += 1
        
        # Normalizar frecuencia
        if ocurrencias == 1:
            return 0.5
        elif ocurrencias == 2:
            return 0.7
        elif ocurrencias >= 3:
            return 1.0
        else:
            return 0.3
    
    def _obtener_contexto_entidad_spacy(
        self, 
        doc: spacy.tokens.Doc, 
        inicio: int, 
        fin: int
    ) -> Tuple[str, str]:
        """
        Obtener contexto de una entidad usando spaCy
        
        Args:
            doc: Documento procesado
            inicio: Posición de inicio de la entidad
            fin: Posición de fin de la entidad
            ventana: Tamaño de la ventana de contexto
            
        Returns:
            Tupla con (contexto_anterior, contexto_posterior)
        """
        ventana = self.configuracion_final["ventana_contexto"]
        
        # Contexto anterior
        inicio_contexto = max(0, inicio - ventana)
        contexto_anterior = doc.text[inicio_contexto:inicio].strip()
        
        # Contexto posterior
        fin_contexto = min(len(doc.text), fin + ventana)
        contexto_posterior = doc.text[fin:fin_contexto].strip()
        
        return contexto_anterior, contexto_posterior
    
    def _obtener_oracion_completa_spacy(
        self, 
        doc: spacy.tokens.Doc, 
        posicion: int
    ) -> Optional[str]:
        """
        Obtener oración completa usando spaCy
        
        Args:
            doc: Documento procesado
            posicion: Posición en el texto
            
        Returns:
            Oración completa o None
        """
        # Encontrar la oración que contiene la posición
        for sent in doc.sents:
            if sent.start_char <= posicion <= sent.end_char:
                return sent.text.strip()
        
        return None
    
    def _obtener_dependencias_entidad_spacy(
        self, 
        entidad: spacy.tokens.Span, 
        doc: spacy.tokens.Doc
    ) -> List[Dict[str, Any]]:
        """
        Obtener dependencias de una entidad usando spaCy
        
        Args:
            entidad: Entidad extraída
            doc: Documento procesado
            
        Returns:
            Lista de dependencias
        """
        dependencias = []
        
        for token in entidad:
            if token.dep_ != "ROOT":
                dependencias.append({
                    "token": token.text,
                    "dep": token.dep_,
                    "head": token.head.text,
                    "head_pos": token.head.pos_
                })
        
        return dependencias
    
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
                "ner_labels": list(modelo.get_pipe("ner").labels) if "ner" in modelo.pipe_names else [],
                "cargado": True
            }
        except Exception as e:
            return {
                "idioma": idioma,
                "error": str(e),
                "cargado": False
            }
