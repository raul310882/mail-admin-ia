import win32com.client
import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
import unicodedata

class MotorReglas:
    def __init__(self):
        self.inicializar_base_datos()
        self.reglas_predefinidas = self.cargar_reglas_predefinidas()
        
    def inicializar_base_datos(self):
        """Inicializa la base de datos SQLite para reglas y configuración"""
        self.conn = sqlite3.connect('reglas_correos.db')
        self.cursor = self.conn.cursor()
        
        # Crear tablas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_remitentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente TEXT NOT NULL,
                carpeta_destino TEXT NOT NULL,
                condiciones_exclusion TEXT,
                prioridad INTEGER DEFAULT 1,
                activa BOOLEAN DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_palabras_clave (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                palabra_clave TEXT NOT NULL,
                carpeta_destino TEXT NOT NULL,
                campo_busqueda TEXT DEFAULT 'asunto',
                prioridad INTEGER DEFAULT 1,
                activa BOOLEAN DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lista_blanca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente TEXT NOT NULL UNIQUE,
                motivo TEXT,
                fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_clasificacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_criterio TEXT NOT NULL,
                patron TEXT NOT NULL,
                modo_coincidencia TEXT NOT NULL DEFAULT 'contiene',
                carpeta_destino TEXT NOT NULL,
                prioridad INTEGER DEFAULT 5,
                activa BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas_compuestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_criterio_1 TEXT NOT NULL,
                patron_1 TEXT NOT NULL,
                modo_coincidencia_1 TEXT NOT NULL DEFAULT 'contiene',
                tipo_criterio_2 TEXT NOT NULL,
                patron_2 TEXT NOT NULL,
                modo_coincidencia_2 TEXT NOT NULL DEFAULT 'contiene',
                carpeta_destino TEXT NOT NULL,
                prioridad INTEGER DEFAULT 10,
                activa BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def cargar_reglas_predefinidas(self) -> Dict:
        """Carga las reglas predefinidas del usuario"""
        return {
            'remitentes': [
                {
                    'remitente': 'facturas@ejemplo.com',
                    'carpeta': 'TP EGRESOS PROVEEDORES',
                    'exclusion': ['CCP', 'Carta Porte', 'CARTAPORTE'],
                    'prioridad': 10
                },
                {
                    'remitente': 'bitacora@ejemplo.com',
                    'carpeta': 'OPERACIONES TP/LOGISTICA/COORD LOGISTICA',
                    'condiciones': ['ENTREGA DE CORTE', 'CAMBIO DE TURNO', 'UNIDADES DISPONIBLES', 'SOLICITUD DE SERVICIO'],
                    'prioridad': 9
                }
            ],
            'palabras_clave': [
                {
                    'palabras': ['CCP', 'Carta Porte', 'CARTAPORTE'],
                    'carpeta': 'OPERACIONES TP/LOGISTICA/COMPLEMENTOS CARTA PORTE',
                    'campo': 'asunto_cuerpo',
                    'prioridad': 8
                },
                {
                    'palabras': ['ACUSES ENTREGADOS'],
                    'carpeta': 'OPERACIONES TP/LOGISTICA/ENTREGA DE CARTAPORTES LOGISTICA',
                    'campo': 'asunto',
                    'prioridad': 8
                },
                {
                    'palabras': ['PROPUESTA DE PROGRAMACION DE DESCANSOS', 'REPORTE DE INCIDENCIAS'],
                    'carpeta': 'RECURSOS HUMANOS',
                    'campo': 'asunto',
                    'prioridad': 7
                },
                {
                    'palabras': ['SPAM', 'virus', 'curso gratuito', 'invitación curso'],
                    'carpeta': 'SPAM',
                    'campo': 'asunto_cuerpo',
                    'prioridad': 6
                },
                {
                    'palabras': ['Listado de facturas con soporte'],
                    'carpeta': 'TP EGRESOS PROVEEDORES',
                    'campo': 'asunto',
                    'prioridad': 9,
                    'modo': 'parecido'
                }
            ]
        }

    def _normalizar_texto(self, texto: str) -> str:
        texto = (texto or '').strip().lower()
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        texto = re.sub(r'\s+', ' ', texto)
        return texto

    def _coincide_patron(self, texto: str, patron: str, modo: str = 'contiene') -> bool:
        texto_n = self._normalizar_texto(texto)
        patron_n = self._normalizar_texto(patron)

        if not patron_n:
            return False

        if modo == 'exacto':
            return texto_n == patron_n

        if modo == 'parecido':
            if patron_n in texto_n:
                return True
            similitud = SequenceMatcher(None, texto_n, patron_n).ratio()
            return similitud >= 0.72

        return patron_n in texto_n

    def obtener_reglas_clasificacion(self) -> List[Tuple]:
        """Obtiene reglas configurables activas por prioridad desc"""
        self.cursor.execute(
            """
            SELECT id, tipo_criterio, patron, modo_coincidencia, carpeta_destino, prioridad, activa
            FROM reglas_clasificacion
            ORDER BY prioridad DESC, id DESC
            """
        )
        return self.cursor.fetchall()

    def agregar_regla_clasificacion(
        self,
        tipo_criterio: str,
        patron: str,
        carpeta_destino: str,
        modo_coincidencia: str = 'contiene',
        prioridad: int = 5,
        activa: bool = True
    ) -> bool:
        """Agrega una regla configurable de clasificación"""
        try:
            self.cursor.execute(
                """
                INSERT INTO reglas_clasificacion
                (tipo_criterio, patron, modo_coincidencia, carpeta_destino, prioridad, activa)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tipo_criterio, patron, modo_coincidencia, carpeta_destino, prioridad, int(activa))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar regla configurable: {e}")
            return False

    def eliminar_regla_clasificacion(self, regla_id: int) -> bool:
        """Elimina una regla configurable por id"""
        try:
            self.cursor.execute("DELETE FROM reglas_clasificacion WHERE id = ?", (regla_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar regla configurable: {e}")
            return False

    def obtener_reglas_compuestas(self) -> List[Tuple]:
        """Obtiene reglas compuestas activas por prioridad desc"""
        self.cursor.execute(
            """
            SELECT id,
                   tipo_criterio_1,
                   patron_1,
                   modo_coincidencia_1,
                   tipo_criterio_2,
                   patron_2,
                   modo_coincidencia_2,
                   carpeta_destino,
                   prioridad,
                   activa
            FROM reglas_compuestas
            ORDER BY prioridad DESC, id DESC
            """
        )
        return self.cursor.fetchall()

    def agregar_regla_compuesta(
        self,
        tipo_criterio_1: str,
        patron_1: str,
        modo_coincidencia_1: str,
        tipo_criterio_2: str,
        patron_2: str,
        modo_coincidencia_2: str,
        carpeta_destino: str,
        prioridad: int = 10,
        activa: bool = True
    ) -> bool:
        """Agrega una regla compuesta (criterio1 AND criterio2)"""
        try:
            self.cursor.execute(
                """
                INSERT INTO reglas_compuestas
                (tipo_criterio_1, patron_1, modo_coincidencia_1,
                 tipo_criterio_2, patron_2, modo_coincidencia_2,
                 carpeta_destino, prioridad, activa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tipo_criterio_1,
                    patron_1,
                    modo_coincidencia_1,
                    tipo_criterio_2,
                    patron_2,
                    modo_coincidencia_2,
                    carpeta_destino,
                    prioridad,
                    int(activa)
                )
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar regla compuesta: {e}")
            return False

    def eliminar_regla_compuesta(self, regla_id: int) -> bool:
        """Elimina una regla compuesta por id"""
        try:
            self.cursor.execute("DELETE FROM reglas_compuestas WHERE id = ?", (regla_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar regla compuesta: {e}")
            return False

    def _valor_criterio(self, tipo: str, remitente: str, asunto: str, destinatarios: str) -> str:
        if tipo == 'remitente':
            return remitente
        if tipo == 'asunto':
            return asunto
        if tipo == 'destinatario':
            return destinatarios
        return ''

    def _clasificar_por_reglas_compuestas(
        self,
        remitente: str,
        asunto: str,
        destinatarios: str
    ) -> Optional[Tuple[str, int]]:
        for (
            _, tipo_1, patron_1, modo_1,
            tipo_2, patron_2, modo_2,
            carpeta, prioridad, activa
        ) in self.obtener_reglas_compuestas():
            if not activa:
                continue

            valor_1 = self._valor_criterio(tipo_1, remitente, asunto, destinatarios)
            valor_2 = self._valor_criterio(tipo_2, remitente, asunto, destinatarios)

            if self._coincide_patron(valor_1, patron_1, modo_1) and self._coincide_patron(valor_2, patron_2, modo_2):
                return (carpeta, prioridad)

        return None

    def _clasificar_por_reglas_configurables(
        self,
        remitente: str,
        asunto: str,
        destinatarios: str
    ) -> Optional[Tuple[str, int]]:
        for _, tipo, patron, modo, carpeta, prioridad, activa in self.obtener_reglas_clasificacion():
            if not activa:
                continue

            valor = self._valor_criterio(tipo, remitente, asunto, destinatarios)
            if self._coincide_patron(valor, patron, modo):
                return (carpeta, prioridad)
        return None
    
    def obtener_carpetas_outlook(self) -> Dict[str, any]:
        """Obtiene todas las carpetas y subcarpetas de Outlook"""
        try:
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)
            
            carpetas = {}
            
            def explorar_carpetas(carpeta, ruta=""):
                carpetas[ruta or carpeta.Name] = carpeta
                for subcarpeta in carpeta.Folders:
                    nueva_ruta = f"{ruta}/{subcarpeta.Name}" if ruta else subcarpeta.Name
                    explorar_carpetas(subcarpeta, nueva_ruta)
            
            explorar_carpetas(inbox)
            return carpetas
            
        except Exception as e:
            print(f"Error al obtener carpetas: {e}")
            return {}
    
    def clasificar_correo(
        self,
        remitente: str,
        asunto: str,
        cuerpo: str,
        destinatarios: str = '',
        remitente_nombre: str = ''
    ) -> Tuple[str, int]:
        """
        Clasifica un correo según las reglas definidas
        Retorna: (carpeta_destino, prioridad)
        """
        texto_completo = f"{asunto} {cuerpo}".lower()
        asunto_lower = asunto.lower()
        
        remitente_email = remitente or ''
        remitente_display = remitente_nombre or ''
        remitente_busqueda = f"{remitente_display} {remitente_email}".strip()

        # 1. Verificar lista blanca (máxima prioridad)
        if self.esta_en_lista_blanca(remitente_email) or (remitente_display and self.esta_en_lista_blanca(remitente_display)):
            return ("Bandeja de Entrada", 100)

        # 2. Reglas compuestas (criterios combinados)
        regla_compuesta = self._clasificar_por_reglas_compuestas(remitente_busqueda, asunto, destinatarios)
        if regla_compuesta:
            return regla_compuesta

        # 3. Reglas configurables de usuario (alta prioridad)
        regla_usuario = self._clasificar_por_reglas_configurables(remitente_busqueda, asunto, destinatarios)
        if regla_usuario:
            return regla_usuario
        
        # 4. Reglas de remitentes (prioridad alta)
        for regla in self.reglas_predefinidas['remitentes']:
            if regla['remitente'].lower() in remitente_busqueda.lower():
                # Verificar exclusiones
                if 'exclusion' in regla:
                    if any(exc.lower() in texto_completo for exc in regla['exclusion']):
                        continue  # Saltar esta regla si hay exclusión
                
                # Verificar condiciones específicas
                if 'condiciones' in regla:
                    if not any(cond.lower() in asunto_lower for cond in regla['condiciones']):
                        continue  # Saltar si no cumple condiciones
                
                return (regla['carpeta'], regla['prioridad'])
        
        # 5. Reglas de palabras clave (prioridad media)
        for regla in self.reglas_predefinidas['palabras_clave']:
            campo_busqueda = asunto_lower if regla['campo'] == 'asunto' else texto_completo
            modo = regla.get('modo', 'contiene')
            if any(self._coincide_patron(campo_busqueda, palabra, modo) for palabra in regla['palabras']):
                return (regla['carpeta'], regla['prioridad'])
        
        # 6. Clasificación por defecto
        return ("General", 0)
    
    def esta_en_lista_blanca(self, remitente: str) -> bool:
        """Verifica si un remitente está en la lista blanca"""
        self.cursor.execute("SELECT 1 FROM lista_blanca WHERE remitente = ?", (remitente,))
        return self.cursor.fetchone() is not None
    
    def agregar_a_lista_blanca(self, remitente: str, motivo: str = ""):
        """Agrega un remitente a la lista blanca"""
        try:
            self.cursor.execute(
                "INSERT OR IGNORE INTO lista_blanca (remitente, motivo) VALUES (?, ?)",
                (remitente, motivo)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar a lista blanca: {e}")
            return False
    
    def obtener_lista_blanca(self) -> List[Tuple]:
        """Obtiene todos los remitentes de la lista blanca"""
        self.cursor.execute("SELECT remitente, motivo, fecha_agregado FROM lista_blanca ORDER BY fecha_agregado DESC")
        return self.cursor.fetchall()
    
    def guardar_regla_aprendida(
        self, 
        remitente: str, 
        carpeta: str, 
        prioridad_personalizada: int = 15,
        incluir_destinatario: bool = False,
        destinatario: str = '',
        incluir_asunto: bool = False,
        asunto: str = ''
    ):
        """
        Guarda una nueva regla aprendida de la acción del usuario
        Puede guardar regla simple (solo remitente) o compuesta (remitente + destinatario + asunto)
        """
        if incluir_asunto and asunto:
            # Guardar como regla compuesta con asunto (máxima especificidad)
            if incluir_destinatario and destinatario:
                # Remitente + Destinatario + Asunto (triple criterio)
                # Usamos regla compuesta de 2 criterios: asunto + (remitente o destinatario)
                return self.agregar_regla_compuesta(
                    tipo_criterio_1='asunto',
                    patron_1=asunto,
                    modo_coincidencia_1='parecido',
                    tipo_criterio_2='remitente',
                    patron_2=remitente,
                    modo_coincidencia_2='contiene',
                    carpeta_destino=carpeta,
                    prioridad=prioridad_personalizada + 10,  # Prioridad máxima
                    activa=True
                )
            else:
                # Asunto + Remitente
                return self.agregar_regla_compuesta(
                    tipo_criterio_1='asunto',
                    patron_1=asunto,
                    modo_coincidencia_1='parecido',
                    tipo_criterio_2='remitente',
                    patron_2=remitente,
                    modo_coincidencia_2='contiene',
                    carpeta_destino=carpeta,
                    prioridad=prioridad_personalizada + 8,
                    activa=True
                )
        elif incluir_destinatario and destinatario:
            # Guardar como regla compuesta (remitente AND destinatario)
            return self.agregar_regla_compuesta(
                tipo_criterio_1='remitente',
                patron_1=remitente,
                modo_coincidencia_1='contiene',
                tipo_criterio_2='destinatario',
                patron_2=destinatario,
                modo_coincidencia_2='contiene',
                carpeta_destino=carpeta,
                prioridad=prioridad_personalizada + 5,  # Prioridad más alta para reglas compuestas
                activa=True
            )
        else:
            # Guardar como regla simple (solo remitente)
            return self.agregar_regla_clasificacion(
                tipo_criterio='remitente',
                patron=remitente,
                carpeta_destino=carpeta,
                modo_coincidencia='contiene',
                prioridad=prioridad_personalizada,
                activa=True
            )
    
    def detectar_asunto_similar(self, asunto_nuevo: str) -> List[Tuple]:
        """
        Detecta asuntos similares en reglas existentes
        Retorna lista de (patron, carpeta_destino, similitud)
        """
        similares = []
        
        # Buscar en reglas configurables
        for _, tipo, patron, modo, carpeta, prioridad, activa in self.obtener_reglas_clasificacion():
            if activa and tipo == 'asunto':
                similitud = SequenceMatcher(
                    None, 
                    self._normalizar_texto(asunto_nuevo), 
                    self._normalizar_texto(patron)
                ).ratio()
                
                if similitud >= 0.72:
                    similares.append((patron, carpeta, similitud))
        
        # Buscar en reglas compuestas
        for regla in self.obtener_reglas_compuestas():
            if regla[9]:  # activa
                # Verificar primer criterio si es asunto
                if regla[1] == 'asunto':
                    similitud = SequenceMatcher(
                        None, 
                        self._normalizar_texto(asunto_nuevo), 
                        self._normalizar_texto(regla[2])
                    ).ratio()
                    if similitud >= 0.72:
                        similares.append((regla[2], regla[7], similitud))
                
                # Verificar segundo criterio si es asunto
                if regla[4] == 'asunto':
                    similitud = SequenceMatcher(
                        None, 
                        self._normalizar_texto(asunto_nuevo), 
                        self._normalizar_texto(regla[5])
                    ).ratio()
                    if similitud >= 0.72:
                        similares.append((regla[5], regla[7], similitud))
        
        # Ordenar por similitud descendente
        similares.sort(key=lambda x: x[2], reverse=True)
        return similares[:5]  # Retornar top 5
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()

# Clase para manejar lotes de correos
class ProcesadorLotes:
    def __init__(self, motor_reglas: MotorReglas):
        self.motor = motor_reglas
        self.tamano_lote = 30
        
    def obtener_lote_correos(self, offset: int = 0) -> List[Dict]:
        """Obtiene un lote de correos no leídos"""
        try:
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)

            # Obtener correos no leídos
            mensajes_no_leidos = inbox.Items.Restrict("[UnRead] = True")
            mensajes_no_leidos.Sort("[ReceivedTime]", True)

            lote = []
            total = mensajes_no_leidos.Count
            for i in range(offset, min(offset + self.tamano_lote, total)):
                try:
                    mensaje = mensajes_no_leidos.Item(i + 1)  # COM índice 1-based
                    try:
                        remitente = mensaje.SenderName or 'Desconocido'
                    except Exception:
                        remitente = 'Desconocido'
                    try:
                        email_remitente = mensaje.SenderEmailAddress or ''
                    except Exception:
                        email_remitente = ''
                    try:
                        asunto = mensaje.Subject or 'Sin asunto'
                    except Exception:
                        asunto = 'Sin asunto'
                    try:
                        cuerpo = (mensaje.Body or '')[:300]
                    except Exception:
                        cuerpo = ''
                    try:
                        destinatarios = mensaje.To or ''
                    except Exception:
                        destinatarios = ''
                    try:
                        copia = mensaje.CC or ''
                    except Exception:
                        copia = ''
                    try:
                        fecha = mensaje.ReceivedTime
                    except Exception:
                        fecha = None

                    correo_data = {
                        'indice': i,
                        'mensaje': mensaje,
                        'remitente': remitente,
                        'email_remitente': email_remitente,
                        'asunto': asunto,
                        'cuerpo': cuerpo,
                        'destinatarios': destinatarios,
                        'cc': copia,
                        'fecha': fecha,
                        'clasificacion': None
                    }

                    # Clasificar el correo
                    carpeta, prioridad = self.motor.clasificar_correo(
                        correo_data['email_remitente'],
                        correo_data['asunto'],
                        correo_data['cuerpo'],
                        f"{correo_data['destinatarios']} {correo_data['cc']}",
                        correo_data['remitente']
                    )
                    correo_data['clasificacion'] = carpeta
                    correo_data['prioridad'] = prioridad

                    lote.append(correo_data)
                except Exception as e_msg:
                    print(f"Error procesando mensaje {i}: {e_msg}")
                    continue

            return lote

        except Exception as e:
            print(f"Error al obtener lote de correos: {e}")
            raise  # Re-raise so the UI shows the actual error
    
    def contar_correos_no_leidos(self) -> int:
        """Cuenta los correos no leídos totales"""
        try:
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)
            mensajes_no_leidos = inbox.Items.Restrict("[UnRead] = True")
            return len(mensajes_no_leidos)
        except Exception as e:
            print(f"Error al contar correos: {e}")
            return 0
