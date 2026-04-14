import win32com.client
import re
from datetime import datetime

class EmailClassifier:
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
            return "SPAM/Descartable"
        
        # Verificar urgencia
        if any(palabra in texto_completo for palabra in self.palabras_urgente):
            return "Urgente"
        
        # Verificar facturación
        if any(palabra in texto_completo for palabra in self.palabras_facturacion):
            return "Facturación"
        
        # Verificar informativo
        if any(palabra in texto_completo for palabra in self.palabras_informativo):
            return "Informativo"
        
        # Clasificación por defecto
        return "General"

def leer_y_clasificar_correos():
    print("🤖 Iniciando clasificador de correos con IA...")
    
    try:
        # Conexión con Outlook
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)
        mensajes = inbox.Items
        mensajes.Sort("[ReceivedTime]", True)
        
        # Crear clasificador
        classifier = EmailClassifier()
        
        # Procesar últimos 5 correos
        print("\n" + "="*60)
        print("📊 ANÁLISIS DE ÚLTIMOS CORREOS")
        print("="*60)
        
        for i in range(min(5, len(mensajes))):
            mensaje = mensajes.GetNext()
            if mensaje:
                # Extraer información
                asunto = mensaje.Subject
                cuerpo = mensaje.Body[:500] if mensaje.Body else ""
                remitente = mensaje.SenderName
                fecha = mensaje.ReceivedTime
                
                # Clasificar
                categoria = classifier.clasificar_correo(asunto, cuerpo)
                
                # Mostrar resultados
                print(f"\n📧 Correo #{i+1}")
                print(f"📂 Categoría: {categoria}")
                print(f"👤 De: {remitente}")
                print(f"📋 Asunto: {asunto}")
                print(f"📅 Fecha: {fecha}")
                print("-" * 40)
        
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Asegúrate de tener Outlook abierto")

if __name__ == "__main__":
    leer_y_clasificar_correos()
