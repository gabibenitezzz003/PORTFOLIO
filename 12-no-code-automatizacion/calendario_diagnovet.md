# 🏥 Sistema de Gestión de Turnos - DiagnoVET

> **Workflow de n8n** para automatizar la gestión de turnos en clínica veterinaria con integración a Google Calendar, notificaciones por email y sincronización con Supabase.

---

## 📋 Descripción General

Este workflow automatiza completamente el proceso de gestión de turnos veterinarios, desde la creación hasta la cancelación, manteniendo sincronizados:
- **Google Calendar** (calendario principal de la clínica)
- **Sistema de notificaciones** (emails automáticos a tutores)
- **Base de datos Supabase** (estado de turnos)

---

## 🔄 Flujo de Funcionamiento

### 1. 📡 **Webhook de Entrada** 
```
Endpoint: /turnos
Método: POST
```

**Datos esperados:**
```json
{
  "id": "turno_123",
  "tipo_evento": "crear|modificar|cancelar",
  "fecha_hora": "2025-09-21T14:30:00",
  "tutor": "Juan Pérez",
  "email_tutor": "juan@email.com",
  "paciente": "Rocky",
  "tipo_consulta": "Consulta general"
}
```

### 2. ⚡ **Switch: Tipo de Evento**

El workflow identifica el tipo de operación y se ramifica en 3 caminos:

```mermaid
graph TD
    A[Webhook Turnos] --> B[Tipo de Evento]
    B --> C[Crear Turno]
    B --> D[Modificar Turno]
    B --> E[Cancelar Turno]
```

---

## 🚀 Operaciones Disponibles

### ✅ **CREAR TURNO**

**Google Calendar:**
- Crea evento en calendario principal
- Horario: `{{ $json.fecha_hora }}`
- Detalles automáticos del paciente y tutor

**Proceso:**
1. Nuevo evento en Google Calendar
2. Email de confirmación al tutor
3. Actualización estado en Supabase: `"creado"`

### ✏️ **MODIFICAR TURNO**

**Google Calendar:**
- Busca eventos entre: `2025-09-19` a `2025-10-31`
- Actualiza información del evento existente

**Proceso:**
1. Localiza y modifica evento en Google Calendar
2. Email de notificación de cambios
3. Actualización estado en Supabase: `"modificado"`

### ❌ **CANCELAR TURNO**

**Google Calendar:**
- Busca eventos entre: `2025-09-19` a `2025-09-30`
- Elimina el evento del calendario

**Proceso:**
1. Elimina evento de Google Calendar
2. Email de cancelación al tutor
3. Actualización estado en Supabase: `"cancelado"`

---

## 📧 Sistema de Notificaciones

### 📨 **Email Automático**

**Configuración:**
- **De:** `noreply@diagnovet.com`
- **Para:** `{{ $json.email_tutor }}`
- **Asunto:** `"Notificación de turno - {{ $json.tipo_evento }}"`

### 🎨 **Template HTML Responsivo**

El email incluye:
- ✅ Diseño profesional con colores de marca
- 📱 Compatible con dispositivos móviles
- 🔗 Botones de acción (Confirmar/Cancelar)
- 📋 Información completa del turno
- 🏥 Branding de DiagnoVET

**Variables dinámicas:**
```html
{{ $json.tutor }}         <!-- Nombre del tutor -->
{{ $json.paciente }}      <!-- Nombre de la mascota -->
{{ $json.fecha_hora }}    <!-- Fecha y hora del turno -->
{{ $json.tipo_consulta }} <!-- Tipo de consulta -->
{{ $json.id }}           <!-- ID del turno -->
```

---

## 💾 Integración con Supabase

### 🔄 **Actualización Automática**

**Endpoint:** 
```
PATCH https://vdvftolwwyprwttfspgx.supabase.co/rest/v1/turno?id=eq.{{$json.id}}
```

**Headers:**
```json
{
  "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "estado": "{{ $json.tipo_evento }}"
}
```

---

## ⚙️ Configuración Técnica

### 🔐 **Credenciales Configuradas**

1. **Google Calendar OAuth2**
   - ID: `d5rspaengZxOaNZz`
   - Calendario: `diagnovetprueba@gmail.com`

2. **SMTP Email**
   - ID: `TUj54aX1NbnSWKFP`
   - Servidor configurado para envío

3. **Supabase API**
   - Tokens de autenticación embebidos
   - Acceso a tabla `turno`

### 🌐 **Endpoints de Acción**

Los emails incluyen links funcionales:
```
Confirmar: https://diagnovet.com/confirmar?turno={{ $json.id }}
Cancelar:  https://diagnovet.com/cancelar?turno={{ $json.id }}
```

---

## 🔧 Uso del Workflow

### 📤 **Ejemplo de Petición**

```bash
curl -X POST https://tu-n8n-instance.com/webhook/turnos \
  -H "Content-Type: application/json" \
  -d '{
    "id": "turno_001",
    "tipo_evento": "crear",
    "fecha_hora": "2025-09-21T15:30:00",
    "tutor": "María González",
    "email_tutor": "maria@email.com",
    "paciente": "Milo",
    "tipo_consulta": "Vacunación"
  }'
```

### 📥 **Respuesta Esperada**

El workflow ejecutará en secuencia:
1. ✅ Evento creado en Google Calendar
2. 📧 Email enviado a `maria@email.com`
3. 💾 Estado actualizado en Supabase
4. 🔄 Proceso completado

---

## 🚀 Estados del Workflow

| Estado | Descripción | Acción en Calendar | Email | Supabase |
|--------|-------------|-------------------|-------|----------|
| `crear` | Nuevo turno | ➕ Crear evento | 📧 Confirmación | ✅ `creado` |
| `modificar` | Cambio de turno | ✏️ Actualizar | 📧 Modificación | ✅ `modificado` |
| `cancelar` | Eliminar turno | ❌ Eliminar | 📧 Cancelación | ✅ `cancelado` |

---

## 📊 Monitoreo

### ✅ **Indicadores de Éxito**
- Evento aparece en Google Calendar
- Email recibido por el tutor
- Estado actualizado en Supabase

### ⚠️ **Posibles Errores**
- Credenciales de Google Calendar expiradas
- SMTP no configurado correctamente
- Token de Supabase inválido
- Formato de fecha incorrecto

---

## 🔮 Mejoras Sugeridas

1. **🔄 Validación de datos** antes del procesamiento
2. **📱 Integración con WhatsApp** para notificaciones
3. **🗓️ Recordatorios automáticos** 24h antes
4. **📈 Dashboard de métricas** de turnos
5. **🔐 Encriptación** de datos sensibles
6. **⏰ Zona horaria** configurable
7. **📋 Logs de auditoría** detallados

---

## 📞 Soporte

Para consultas sobre este workflow:
- 📧 Email: gabibenitezzz003@gmail.com
- 📚 Documentación: [Docs de n8n](https://docs.n8n.io)

---

*Desarrollado y Automatizando para gestionar tiempos productivos*