import win32com.client
import re
from datetime import datetime

class EmailOrganizerSimulator:
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
    
    def simular_organizacion(self):
        """Simula la organización de correos sin moverlos"""
        print(" simulator: Iniciando simulación de organización de correos...")
        
        try:
            # Conexión con Outlook
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)
            
            # Obtener correos no leídos
            mensajes_no_leidos = inbox.Items.Restrict("[UnRead] = True")
            
            if not mensajes_no_leidos:
                print(" simulator: No hay correos no leídos para organizar")
                return
            
            print(f"\n simulator: Análisis de {len(mensajes_no_leidos)} correos no leídos...")
            print("="*70)
            
            resumen = {}
            
            for i, mensaje in enumerate(mensajes_no_leidos):
                # Extraer información
                asunto = mensaje.Subject if mensaje.Subject else "Sin asunto"
                cuerpo = mensaje.Body[:300] if mensaje.Body else ""
                remitente = mensaje.SenderName
                fecha = mensaje.ReceivedTime
                
                # Clasificar
                categoria = self.clasificar_correo(asunto, cuerpo)
                
                # Contar para resumen
                if categoria not in resumen:
                    resumen[categoria] = 0
                resumen[categoria] += 1
                
                # Mostrar simulación
                print(f" simulator: Correo #{i+1}")
                print(f"  De: {remitente}")
                print(f"  Asunto: {asunto[:60]}...")
                print(f"  Categoría: {categoria}")
                print(f"  Acción simulada: MOVER a carpeta '{categoria}'")
                print("-" * 50)
            
            # Mostrar resumen
            print(f"\n simulator: RESUMEN DE ORGANIZACIÓN")
            print("="*40)
            for categoria, cantidad in resumen.items():
                print(f"  {categoria}: {cantidad} correos")
            print("="*40)
            print(f" simulator: Total procesados: {len(mensajes_no_leidos)} correos")
            print("\n simulator: Esta es solo una simulación. No se movió ningún correo.")
            
        except Exception as e:
            print(f"\n simulator: Error: {e}")
            print(" simulator: Asegúrate de tener Outlook abierto")

def main():
    simulator = EmailOrganizerSimulator()
    
    print(" simulator: SIMULADOR DE ORGANIZACIÓN DE CORREOS CON IA")
    print("="*60)
    
    # Mostrar resumen antes de simular
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)
        mensajes_no_leidos = inbox.Items.Restrict("[UnRead] = True")
        print(f" simulator: Correos no leídos actuales: {len(mensajes_no_leidos)}")
    except:
        print(" simulator: No se pudo verificar correos no leídos")
        return
    
    print("\n simulator: Iniciando simulación...")
    simulator.simular_organizacion()

if __name__ == "__main__":
    main()
