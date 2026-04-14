# Organizador de Correos Outlook con IA

## Descripción
Sistema local de clasificación automática de correos de Outlook 2016 con aprendizaje de reglas y procesamiento por lotes.

## Requisitos
- Outlook 2016 (o superior) instalado y abierto
- Python 3.13 instalado
- Entorno virtual configurado en `C:\mail-admin-ia\venv`

## Instalación
El sistema ya está instalado y configurado. Solo necesitas tener Outlook abierto antes de ejecutar el programa.

## Cómo Ejecutar

### Método 1: Desde el Escritorio (Recomendado)
1. Doble clic en el acceso directo **"Organizador Correos IA"** en tu escritorio
2. Asegúrate de que Outlook esté abierto antes de ejecutar

### Método 2: Desde el Directorio
1. Navega a `C:\mail-admin-ia`
2. Doble clic en `ejecutar_organizador.bat`

## Uso del Sistema

### Interfaz Principal
- **Panel de Control**: Botones para cargar correos, mover correos, lista blanca y configuración
- **Lista de Correos**: Muestra los correos no leídos en lotes de 10
- **Panel de Detalles**: Muestra información completa del correo seleccionado

### Procesamiento de Correos
1. Clic en **"📨 Cargar Correos"** para cargar el siguiente lote de 10 correos
2. Revisa la clasificación sugerida en la columna "Clasificación IA"
3. Si la clasificación es incorrecta, **doble clic** en la columna "Clasificación IA" para cambiarla
4. Selecciona los correos que deseas mover usando los checkboxes
5. Clic en **"📤 Mover Seleccionados"** para mover los correos a sus carpetas

### Modificación Rápida de Clasificación
1. **Doble clic** en la columna "Clasificación IA" de cualquier correo
2. Selecciona la clasificación correcta del desplegable
3. Opciones disponibles:
   - **💾 Guardar como regla**: Guarda la clasificación para futuros correos
   - **👥 Incluir destinatario**: Crea regla más específica (remitente + destinatario)
   - **📝 Incluir asunto**: Aprende patrones de asuntos similares
4. Clic en **"Confirmar"** para aplicar el cambio

### Lista Blanca
1. Clic en **"📋 Lista Blanca"**
2. Agrega remitentes de confianza que deben ser procesados normalmente
3. Los remitentes en lista blanca tienen máxima prioridad

### Configuración de Reglas
1. Clic en **"🔧 Configurar Reglas"**
2. Agrega o modifica reglas de clasificación personalizadas
3. Puedes crear reglas por remitente, asunto, palabras clave, o reglas compuestas

## Sistema de Aprendizaje

El sistema aprende de tus acciones y crea reglas automáticamente:

### Tipos de Reglas Aprendidas
- **Solo Remitente** (prioridad 15): Clasifica todos los correos de ese remitente
- **Remitente + Destinatario** (prioridad 20): Clasifica correos específicos entre remitente y destinatario
- **Asunto + Remitente** (prioridad 23): Aprende patrones de asuntos similares
- **Asunto + Remitente + Destinatario** (prioridad 25): Máxima especificidad

### Detección de Asuntos Similares
El sistema detecta automáticamente asuntos similares a reglas existentes y te muestra sugerencias con porcentaje de similitud.

### Prioridad de Reglas
Las reglas aprendidas manualmente tienen mayor prioridad que las reglas predefinidas, asegurando que tus decisiones se respeten.

## Estructura de Carpetas
El sistema se integra con tu estructura existente de carpetas de Outlook.

## Solución de Problemas

### Outlook no está abierto
El sistema requiere que Outlook esté abierto. Abre Outlook antes de ejecutar el programa.

### Error de conexión con Outlook
Cierra y vuelve a abrir Outlook, luego ejecuta el programa nuevamente.

### No aparecen correos
Asegúrate de que hay correos no leídos en tu bandeja de entrada.

## Archivos del Sistema
- `motor_reglas.py`: Motor de reglas y clasificación
- `interfaz_grafica.py`: Interfaz gráfica de usuario
- `ejecutar_organizador.bat`: Script de ejecución
- `reglas.db`: Base de datos SQLite con reglas aprendidas

## Soporte
Para problemas o preguntas, revisa la configuración de reglas o la lista blanca para ajustar el comportamiento del sistema.
