# 🚀 Sistema Inteligente de Análisis de Tendencias y Generación de Contenido Viral

## 📋 Descripción

Este workflow avanzado de N8N es un **sistema completo de automatización de marketing** que:

✨ **Monitorea automáticamente** las tendencias más populares en Reddit y HackerNews
🤖 **Genera contenido optimizado** usando GPT-4 basado en tendencias reales
🎨 **Crea imágenes atractivas** con DALL-E 3 para cada publicación
📱 **Publica automáticamente** en Twitter/X y LinkedIn
📊 **Registra todo** en Google Sheets para análisis
📧 **Envía reportes detallados** por email y Telegram

---

## 🎯 ¿Por qué es impresionante?

- **100% Automatizado**: Se ejecuta cada 6 horas sin intervención humana
- **Multi-plataforma**: Integra Reddit, HackerNews, OpenAI, Twitter, LinkedIn, Gmail, Telegram y Google Sheets
- **Inteligencia Real**: Analiza engagement real para identificar tendencias
- **Generación Diversa**: Crea 3 tipos de contenido diferentes (educativo, engagement, viral)
- **Trazabilidad Total**: Cada acción se registra y reporta
- **Escalable**: Puedes añadir más fuentes de datos o plataformas fácilmente

---

## 🏗️ Arquitectura del Workflow

```
📅 Schedule (cada 6h)
    ↓
    ├─→ 🔥 Reddit Trends → Procesar → 
    │                                  ↓
    └─→ 💻 HackerNews → IDs → Detalles → Procesar
                                         ↓
                                    🔀 MERGE
                                         ↓
                                    📊 Análisis Top 3
                                         ↓
                                    🤖 GPT-4: Generar 3 Posts
                                         ↓
                                    📝 Formatear
                                         ↓
                                    ✂️ Separar Posts (3 items)
                                         ↓
                                    🎨 DALL-E: Generar Imagen
                                         ↓
                                    📥 Descargar Imagen
                                         ↓
        ┌────────────────────────────────┼────────────────────────────┐
        ↓                                ↓                            ↓
    🐦 Twitter/X                    💼 LinkedIn                  📱 Telegram
        ↓                                                             
        └──────────────────┬──────────────────────────────────────────┘
                           ↓
            ┌──────────────┴──────────────┐
            ↓                             ↓
        📧 Gmail Report            📊 Google Sheets Log
```

---

## 🔧 Requisitos Previos

### 1. **Credenciales OpenAI** (REQUERIDO)
- Necesitas una API Key de OpenAI
- Modelos usados: `gpt-4o-mini` y `dall-e-3`
- Configurar en N8N: **Credentials** → **OpenAI** → OAuth2

### 2. **Twitter/X API** (Opcional pero recomendado)
- Crear cuenta de desarrollador en https://developer.twitter.com
- Obtener API Key, API Secret, Access Token, Access Secret
- Configurar OAuth 2.0 en N8N

### 3. **LinkedIn API** (Opcional)
- Crear app en https://www.linkedin.com/developers/
- Configurar OAuth 2.0 en N8N

### 4. **Google Sheets API** (Opcional)
- Habilitar Google Sheets API en Google Cloud Console
- Configurar OAuth 2.0 en N8N

### 5. **Gmail API** (Opcional)
- Habilitar Gmail API en Google Cloud Console
- Configurar OAuth 2.0 en N8N

### 6. **Telegram Bot** (Opcional)
- Crear bot con @BotFather en Telegram
- Obtener Bot Token
- Obtener tu Chat ID (usa @userinfobot)

---

## 📥 Instalación

### Paso 1: Importar el Workflow

1. Abre tu instancia de N8N
2. Ve a **Workflows** → **Add workflow** → **Import from File**
3. Copia el contenido del archivo JSON y pégalo
4. Click en **Import**

### Paso 2: Configurar Credenciales

#### OpenAI (OBLIGATORIO)
```
Settings → Credentials → Add Credential → OpenAI
- Authentication: OAuth2
- API Key: tu_api_key_de_openai
```

#### Twitter/X (OPCIONAL)
```
Settings → Credentials → Add Credential → Twitter OAuth2
- API Key: tu_api_key
- API Secret: tu_api_secret
- Access Token: tu_access_token
- Access Secret: tu_access_secret
```

#### Google Sheets (OPCIONAL)
```
Settings → Credentials → Add Credential → Google Sheets OAuth2
- Autorizar con tu cuenta de Google
- Crear una hoja llamada "Contenido Publicado"
- Copiar el ID de la hoja (está en la URL)
- Reemplazar YOUR_GOOGLE_SHEET_ID en el nodo
```

#### Telegram (OPCIONAL)
```
Settings → Credentials → Add Credential → Telegram
- Access Token: token_de_tu_bot
- Reemplazar YOUR_TELEGRAM_CHAT_ID en el nodo
```

### Paso 3: Personalizar Parámetros

Abre el workflow y modifica estos valores:

1. **Nodo "Notificar Telegram"**: 
   - Reemplaza `YOUR_TELEGRAM_CHAT_ID` con tu Chat ID real

2. **Nodo "Registrar en Google Sheets"**:
   - Reemplaza `YOUR_GOOGLE_SHEET_ID` con tu ID de Google Sheet

3. **Nodo "Enviar Reporte Email"**:
   - Cambia `your-email@gmail.com` por tu email
   - Cambia `recipient@example.com` por el destinatario

4. **Nodo "Generar Contenido (OpenAI)"** (Opcional):
   - Puedes modificar el prompt del sistema para ajustar el tono
   - Puedes cambiar el idioma (actualmente está en español)

---

## 🎮 Uso

### Ejecución Manual
1. Abre el workflow
2. Click en **Execute Workflow** (arriba a la derecha)
3. Espera 2-3 minutos mientras se ejecuta
4. Revisa los resultados en cada nodo

### Ejecución Automática
- El workflow se ejecuta **automáticamente cada 6 horas**
- Puedes cambiar la frecuencia en el nodo "Ejecutar cada 6 horas"
- Opciones: cada hora, cada día, custom cron

### Monitoreo
- Ve a **Executions** para ver el historial
- Revisa tu Google Sheet para ver todos los posts generados
- Chequea tu email para reportes detallados

---

## 📊 Estructura de Datos

### Tendencias Procesadas
```json
{
  "title": "Título de la tendencia",
  "score": 1523,
  "comments": 234,
  "url": "https://...",
  "engagement": 1991,
  "source": "Reddit"
}
```

### Posts Generados
```json
{
  "type": "educativo",
  "content": "Contenido del post...",
  "hashtags": ["#AI", "#Tech"],
  "fullPost": "Contenido completo con hashtags"
}
```

---

## 🔄 Flujo de Datos Detallado

1. **Recolección** (2 min):
   - Reddit API: Top 25 posts de r/technology
   - HackerNews API: Top 10 stories
   - Total: ~35 tendencias

2. **Análisis** (30 seg):
   - Calcula engagement: `score + (comments × 2)`
   - Ordena por engagement
   - Selecciona Top 3

3. **Generación IA** (60-90 seg):
   - GPT-4 analiza las 3 tendencias
   - Genera 3 posts diferentes
   - Cada post optimizado para redes sociales

4. **Creación Visual** (45 seg):
   - DALL-E 3 genera imagen única
   - Descarga en formato PNG
   - Adjunta a publicaciones

5. **Publicación** (30 seg):
   - Twitter/X: Post + imagen
   - LinkedIn: Post profesional + imagen
   - Simultaneo en ambas plataformas

6. **Registro y Notificación** (15 seg):
   - Telegram: Notificación instantánea
   - Gmail: Reporte HTML completo
   - Google Sheets: Log estructurado

**Tiempo total**: ~5 minutos por ejecución

---

## 🎨 Personalización Avanzada

### Cambiar Fuentes de Tendencias

Puedes agregar más fuentes modificando el workflow:

```javascript
// Ejemplo: Agregar ProductHunt
{
  "parameters": {
    "url": "https://api.producthunt.com/v2/api/graphql",
    "method": "POST",
    "body": {
      "query": "{ posts { edges { node { name votesCount } } } }"
    }
  },
  "name": "Obtener Tendencias ProductHunt",
  "type": "n8n-nodes-base.httpRequest"
}
```

### Modificar Estilo de Contenido

Edita el prompt en el nodo "Generar Contenido (OpenAI)":

```javascript
// Para contenido más formal:
"Eres un analista senior de tecnología. Crea contenido profesional y técnico..."

// Para contenido más casual:
"Eres un influencer tech. Crea posts divertidos y accesibles..."

// Para contenido en inglés:
"You are a viral content expert. Create engaging posts in English..."
```

### Ajustar Frecuencia de Imágenes

Puedes generar imagen solo para ciertos tipos de posts:

```javascript
// En el nodo "Separar Posts", agrega un filtro:
return posts.filter(post => post.type === 'educativo').map(post => ({ json: {...} }));
```

### Personalizar Reportes

Modifica el HTML del email en el nodo "Enviar Reporte Email":

```html
<style>
  body { font-family: Arial, sans-serif; }
  .highlight { background: #ffd700; padding: 5px; }
  .metric { font-size: 24px; color: #0066cc; }
</style>
<h2>🎯 Tu Reporte Personalizado</h2>
<div class="highlight">Engagement Total: <span class="metric">{{ suma_engagement }}</span></div>
```

---

## 🛠️ Troubleshooting

### Problema: "Error: Authentication required"
**Solución**: 
- Verifica que todas las credenciales estén configuradas
- Re-autoriza las conexiones OAuth2
- Revisa que los tokens no hayan expirado

### Problema: "Rate limit exceeded" en OpenAI
**Solución**:
- Reduce la frecuencia del workflow (cada 12h o 24h)
- Usa `gpt-3.5-turbo` en lugar de `gpt-4o-mini`
- Implementa un sistema de cola para distribuir las peticiones

### Problema: "No se generan imágenes"
**Solución**:
- Verifica tu saldo en OpenAI
- DALL-E 3 cuesta $0.04 por imagen
- Considera hacer la generación de imagen opcional

### Problema: "El workflow se ejecuta pero no publica"
**Solución**:
- Revisa los permisos de las APIs (Twitter requiere Elevated Access)
- Verifica que las credenciales tengan scope de escritura
- Prueba cada nodo de publicación individualmente

### Problema: "Error al procesar Reddit/HackerNews"
**Solución**:
- Las APIs públicas pueden cambiar, verifica la documentación
- Agrega manejo de errores con nodo "Error Trigger"
- Implementa reintentos automáticos

---

## 💡 Ideas de Mejora

### Nivel Básico
- ✅ Agregar más subreddits (r/programming, r/artificial, r/startups)
- ✅ Incluir análisis de sentimientos con biblioteca de NLP
- ✅ Guardar imágenes en Google Drive o Dropbox
- ✅ Crear variaciones A/B del mismo contenido

### Nivel Intermedio
- 🚀 Integrar con TikTok o Instagram para publicar
- 🚀 Analizar el rendimiento de posts anteriores
- 🚀 Usar webhooks para ejecución bajo demanda
- 🚀 Implementar sistema de aprobación manual antes de publicar

### Nivel Avanzado
- 🔥 Machine Learning para predecir viralidad
- 🔥 Generación de videos cortos con IA
- 🔥 Sistema multi-idioma con traducción automática
- 🔥 Dashboard en tiempo real con métricas
- 🔥 Integración con herramientas de SEO

---

## 📈 Métricas y KPIs

El workflow automáticamente registra:

| Métrica | Descripción | Donde verlo |
|---------|-------------|-------------|
| **Posts Generados** | Total de publicaciones creadas | Google Sheets |
| **Engagement Base** | Score inicial de la tendencia | Google Sheets, Email |
| **Fuente** | Reddit o HackerNews | Todos los reportes |
| **Tipo de Post** | Educativo, Engagement, Viral | Google Sheets |
| **Timestamp** | Fecha y hora exacta | Google Sheets, Email |
| **Hashtags Usados** | Lista de hashtags por post | Google Sheets |

### Dashboard Sugerido (Google Sheets)

Crea estas columnas adicionales con fórmulas:

```
=COUNTIF(B:B, "educativo")  // Cuenta posts educativos
=AVERAGE(F:F)                // Promedio de engagement
=SPARKLINE(F2:F100)         // Gráfico de tendencia
```

---

## 🔐 Seguridad y Privacidad

### Buenas Prácticas

1. **Nunca compartas tu JSON con credenciales**
   - Exporta sin credenciales: Settings → Export without credentials

2. **Usa variables de entorno**
   - N8N soporta variables: `{{$env.OPENAI_KEY}}`

3. **Limita los permisos OAuth**
   - Solo otorga los permisos necesarios
   - Revisa periódicamente las aplicaciones conectadas

4. **Monitorea el uso de APIs**
   - OpenAI: https://platform.openai.com/usage
   - Twitter: https://developer.twitter.com/en/portal/dashboard

5. **Backup regular**
   - Exporta el workflow semanalmente
   - Guarda versiones en Git

---

## 💰 Costos Estimados

### OpenAI (Principal gasto)

Por ejecución (3 posts):
- **GPT-4o-mini**: ~$0.002 por generación = $0.002
- **DALL-E 3**: $0.04 por imagen × 3 = $0.12
- **Total por ejecución**: ~$0.122

Por mes (4 ejecuciones/día × 30 días):
- **120 ejecuciones**: ~$14.64/mes

### Otras APIs (Generalmente gratuitas)

- **Reddit API**: Gratis (sin autenticación)
- **HackerNews API**: Gratis
- **Twitter API Free**: 1,500 posts/mes gratis
- **LinkedIn API**: Limitado pero suficiente
- **Google Sheets API**: Gratis hasta 500 requests/100 segundos
- **Gmail API**: Gratis hasta 1,000,000,000 de cuota

### Optimización de Costos

```javascript
// Opción 1: Usar GPT-3.5-turbo (75% más barato)
"modelId": "gpt-3.5-turbo"

// Opción 2: Generar solo 1 imagen en lugar de 3
// Agregar condición en el flujo

// Opción 3: Ejecutar menos frecuentemente
"hoursInterval": 12  // En lugar de 6
```

**Costo optimizado**: ~$2-5/mes

---

## 🧪 Testing

### Test Manual Paso a Paso

1. **Test de Recolección**:
   ```
   - Ejecuta solo "Obtener Tendencias Reddit"
   - Verifica que devuelve 25 posts
   - Revisa que los datos tienen title, score, comments
   ```

2. **Test de Procesamiento**:
   ```
   - Ejecuta hasta "Analizar Top Tendencias"
   - Verifica que se seleccionan las top 3
   - Revisa que el summary esté bien formateado
   ```

3. **Test de Generación IA**:
   ```
   - Ejecuta hasta "Separar Posts"
   - Verifica que se crean 3 posts diferentes
   - Revisa la calidad del contenido generado
   ```

4. **Test de Publicación** (¡CUIDADO!):
   ```
   - Desactiva temporalmente los nodos de publicación
   - O crea cuentas de prueba
   - Verifica que el formato sea correcto
   ```

### Test Automatizado

Crea un workflow de test separado:

```json
{
  "nodes": [
    {
      "name": "Test Data",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "json": {
            "title": "Test Trend",
            "score": 1000,
            "comments": 100
          }
        }
      }
    }
  ]
}
```

---

## 🌐 Recursos Adicionales

### Documentación Oficial
- [N8N Docs](https://docs.n8n.io/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Reddit API](https://www.reddit.com/dev/api/)
- [HackerNews API](https://github.com/HackerNews/API)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)

### Comunidad
- [N8N Community](https://community.n8n.io/)
- [N8N GitHub](https://github.com/n8n-io/n8n)
- [Workflow Templates](https://n8n.io/workflows/)

### Tutoriales Complementarios
- [N8N + OpenAI](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-langchain.openai/)
- [Social Media Automation](https://n8n.io/workflows/?categories=Social%20Media)
- [Data Processing](https://docs.n8n.io/workflows/components/nodes/)

---

## 🤝 Contribuciones

¿Tienes ideas para mejorar este workflow?

### Cómo contribuir:
1. Haz un fork del workflow
2. Implementa tu mejora
3. Documenta los cambios
4. Comparte en la comunidad de N8N

### Ideas bienvenidas:
- ✨ Nuevas fuentes de tendencias
- 🎨 Mejores prompts para IA
- 📊 Dashboards y visualizaciones
- 🔧 Optimizaciones de rendimiento
- 🌍 Soporte multi-idioma

---

## ⚠️ Disclaimer

Este workflow es una **herramienta de automatización** que debe usarse responsablemente:

- ✅ Respeta los términos de servicio de cada plataforma
- ✅ No spamees ni publiques contenido inapropiado
- ✅ Revisa el contenido generado antes de publicar
- ✅ Cumple con las regulaciones de cada país
- ✅ Usa las APIs de forma ética y legal

El creador del workflow no se hace responsable del uso indebido.

---

## 📝 Changelog

### v1.0.0 (2025-09-29)
- ✨ Lanzamiento inicial
- 🔥 Integración con Reddit y HackerNews
- 🤖 Generación de contenido con GPT-4
- 🎨 Generación de imágenes con DALL-E 3
- 📱 Publicación en Twitter y LinkedIn
- 📊 Logging en Google Sheets
- 📧 Reportes por email y Telegram

---

## 📞 Soporte

¿Necesitas ayuda?

- 💬 **Comunidad N8N**: [community.n8n.io](https://community.n8n.io/)
- 📧 **Email**: gabibenitezzz003@gmail.com
- 🐛 **Bugs**: Reporta problemas con detalles específicos
- 💡 **Ideas**: Comparte sugerencias de mejora

---

## ⭐ Si te gustó este workflow...

- Dale estrella en GitHub
- Compártelo en redes sociales
- Únete a la comunidad de N8N
- Crea tus propias variaciones

---

## 📜 Licencia

MIT License - Libre para usar, modificar y distribuir

```
Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🎉 ¡Comienza Ahora!

```bash
# 1. Importa el workflow en N8N
# 2. Configura las credenciales de OpenAI (mínimo)
# 3. Ejecuta manualmente para probar
# 4. Activa la ejecución automática
# 5. ¡Disfruta del contenido viral automático! 🚀
```

---
Realizado por gabi benitez