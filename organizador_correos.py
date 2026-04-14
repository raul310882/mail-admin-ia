import win32com.client
import re
from datetime import datetime

class EmailOrganizer:
    def __init__(self):
        # Palabras clave para clasificación
        self.palabras_urgente = ['urgente', 'inmediato', 'asap', 'emergencia', 'crítico', 'pronto', 'hoy']
        self.palabras_facturacion = ['factura', 'pago', 'cobro', 'facturación', 'invoice', 'payment', 'cuenta']
        self.palabras_informativo = ['información', 'info', 'actualización', 'novedades', 'comunicado', 'aviso']
        self.palabras_spam = ['spam', 'oferta', 'promoción', 'descuento', 'gratis', 'ganaste', 'premio']
        
    def clasificar_correo(self, asunto, cuerpo):
        """Clasifica un correo basado en su contenido"""
        texto_completo = f"{asunto} {cuerpo}".lower()
        
        # Verificar spam primero
        if any(palabra in texto_completo for palabra in self.palabras_spam):
            return "SPAM"
        
        # Verificar urgencia
        if any(palabra in texto_completo for palabra in self.palabras_urgente):
            return "Urgente"
        
        # Verificar facturación
        if any(palabra in texto_completo for palabra in self.palabras_facturacion):
            return "Facturacion"
        
        # Verificar informativo
        if any(palabra in texto_completo for palabra in self.palabras_informativo):
            return "Informativo"
        
        # Clasificación por defecto
        return "General"
    
    def crear_o_obtener_carpeta(self, inbox, nombre_carpeta):
        """Crea una carpeta si no existe o la devuelve si existe"""
        try:
            # Intentar obtener la carpeta existente
            carpeta = inbox.Folders[nombre_carpeta]
            print(f"📁 Carpeta '{nombre_carpeta}' encontrada")
            return carpeta
        except:
            # Si no existe, crearla
            try:
                nueva_carpeta = inbox.Folders.Add(nombre_carpeta)
                print(f"📁 Carpeta '{nombre_carpeta}' creada")
                return nueva_carpeta
            except Exception as e:
                print(f"❌ Error al crear carpeta '{nombre_carpeta}': {e}")
                return None
    
    def organizar_correos_no_leidos(self):
        """Organiza correos no leídos moviéndolos a carpetas según su clasificación"""
        print("🤖 Iniciando organizador automático de correos...")
        
        try:
            # Conexión con Outlook
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)
            
            # Crear carpetas si no existen
            carpetas = {}
            categorias = ["Urgente", "Facturacion", "Informativo", "SPAM", "General"]
            
            for categoria in categorias:
                carpeta = self.crear_o_obtener_carpeta(inbox, categoria)
                if carpeta:
                    carpetas[categoria] = carpeta
            
            # Obtener correos no leídos
            mensajes_no_leidos = inbox.Items.Restrict("[UnRead] = True")
            
            if not mensajes_no_leidos:
                print("📭 No hay correos no leídos para organizar")
                return
            
            print(f"\n📊 Procesando {len(mensajes_no_leidos)} correos no leídos...")
            print("="*60)
            
            movidos = 0
            
            for mensaje in mensajes_no_leidos:
                # Extraer información
                asunto = mensaje.Subject if mensaje.Subject else ""
                cuerpo = mensaje.Body[:500] if mensaje.Body else ""
                remitente = mensaje.SenderName
                fecha = mensaje.ReceivedTime
                
                # Clasificar
                categoria = self.clasificar_correo(asunto, cuerpo)
                
                # Mover a la carpeta correspondiente
                if categoria in carpetas:
                    try:
                        mensaje.Move(carpetas[categoria])
                        print(f"✅ Movido: '{asunto[:50]}...' → {categoria}")
                        movidos += 1
                    except Exception as e:
                        print(f"❌ Error al mover correo: {e}")
                else:
                    print(f"⚠️ No se pudo mover: '{asunto[:50]}...' (categoría: {categoria})")
            
            print(f"\n🎉 Organización completada: {movidos} correos movidos")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Asegúrate de tener Outlook abierto")

def main():
    organizer = EmailOrganizer()
    
    print("📧 ORGANIZADOR AUTOMÁTICO DE CORREOS CON IA")
    print("="*50)
    
    # Mostrar resumen antes de organizar
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)
        mensajes_no_leidos = inbox.Items.Restrict("[UnRead] = True")
        print(f"📭 Correos no leídos actuales: {len(mensajes_no_leidos)}")
    except:
        print("❌ No se pudo verificar correos no leídos")
        return
    
    print("\n¿Deseas organizar los correos no leídos ahora? (s/n)")
    respuesta = input("> ").lower().strip()
    
    if respuesta == 's' or respuesta == 'si' or respuesta == 'sí':
        organizer.organizar_correos_no_leidos()
    else:
        print("❌ Operación cancelada")

if __name__ == "__main__":
    main()
