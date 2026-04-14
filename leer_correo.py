import win32com.client
import sys

def leer_ultimo_correo():
    print("Iniciando conexión con Outlook...")
    try:
        # Esto conecta el script con la aplicación de escritorio de Outlook
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        
        # El número 6 es el identificador interno de Windows para la Bandeja de Entrada (Inbox)
        inbox = outlook.GetDefaultFolder(6)
        
        # Obtener los elementos y ordenarlos por fecha de recepción (del más reciente al más antiguo)
        mensajes = inbox.Items
        mensajes.Sort("[ReceivedTime]", True)
        
        # Tomar el primer mensaje (el más reciente)
        ultimo_mensaje = mensajes.GetFirst()
        
        if ultimo_mensaje:
            print("\n" + "="*40)
            print("📬 ÚLTIMO CORREO ENCONTRADO")
            print("="*40)
            print(f"De:      {ultimo_mensaje.SenderName}")
            # Algunos correos internos de Exchange no exponen SenderEmailAddress de forma sencilla, 
            # usar getattr evita que el script falle si falta el dato.
            print(f"Correo:  {getattr(ultimo_mensaje, 'SenderEmailAddress', 'No disponible')}")
            print(f"Asunto:  {ultimo_mensaje.Subject}")
            print(f"Fecha:   {ultimo_mensaje.ReceivedTime}")
            print("-" * 40)
            # Imprimimos solo los primeros 200 caracteres del cuerpo para no saturar la consola
            cuerpo = ultimo_mensaje.Body[:200].replace('\n', ' ').replace('\r', '')
            print(f"Extracto:\n{cuerpo}...")
            print("="*40)
        else:
            print("La bandeja de entrada está vacía.")
            
    except Exception as e:
        print(f"\n❌ Error al conectar con Outlook: {e}")
        print("💡 Tip: Asegúrate de tener la aplicación de escritorio de Outlook abierta antes de correr el script.")

if __name__ == "__main__":
    leer_ultimo_correo()
