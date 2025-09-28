"""
Excepciones del Pipeline - Pipeline ETL
Excepciones específicas para el pipeline de procesamiento de datos
"""


class ExcepcionPipeline(Exception):
    """Excepción base para el pipeline"""
    pass


class ErrorExtraccion(ExcepcionPipeline):
    """Excepción cuando hay error en la extracción de datos"""
    pass


class ErrorTransformacion(ExcepcionPipeline):
    """Excepción cuando hay error en la transformación de datos"""
    pass


class ErrorCarga(ExcepcionPipeline):
    """Excepción cuando hay error en la carga de datos"""
    pass


class ErrorValidacion(ExcepcionPipeline):
    """Excepción cuando hay error en la validación de datos"""
    pass


class ErrorConfiguracion(ExcepcionPipeline):
    """Excepción cuando hay error en la configuración"""
    pass


class ErrorAnalisis(ExcepcionPipeline):
    """Excepción cuando hay error en el análisis de datos"""
    pass


class ErrorVisualizacion(ExcepcionPipeline):
    """Excepción cuando hay error en la generación de visualizaciones"""
    pass


class ErrorReporte(ExcepcionPipeline):
    """Excepción cuando hay error en la generación de reportes"""
    pass


class ErrorDatos(ExcepcionPipeline):
    """Excepción cuando hay error con los datos"""
    pass


class ErrorArchivo(ExcepcionPipeline):
    """Excepción cuando hay error con archivos"""
    pass


class ErrorConexion(ExcepcionPipeline):
    """Excepción cuando hay error de conexión"""
    pass


class ErrorProcesamiento(ExcepcionPipeline):
    """Excepción cuando hay error en el procesamiento"""
    pass
