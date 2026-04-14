import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from motor_reglas import MotorReglas, ProcesadorLotes
    print("motor_reglas.py importado correctamente")
    
    # Probar inicialización del motor de reglas
    print("Inicializando motor de reglas...")
    motor = MotorReglas()
    print("Motor de reglas inicializado correctamente")
    
    # Probar obtener carpetas de Outlook
    print("Obteniendo carpetas de Outlook...")
    carpetas = motor.obtener_carpetas_outlook()
    print(f"Se encontraron {len(carpetas)} carpetas")
    
    # Mostrar algunas carpetas encontradas
    print("\nCarpetas encontradas:")
    for i, (nombre, carpeta) in enumerate(list(carpetas.items())[:10]):
        print(f"  {i+1}. {nombre}")
    
    if len(carpetas) > 10:
        print(f"  ... y {len(carpetas) - 10} más")
    
    # Probar contar correos no leídos
    print("\nContando correos no leídos...")
    procesador = ProcesadorLotes(motor)
    count = procesador.contar_correos_no_leidos()
    print(f"Correos no leídos: {count}")
    
    # Probar clasificación con un ejemplo
    print("\nProbando clasificación...")
    remitente = "facturas@ejemplo.com"
    asunto = "Factura 12345"
    cuerpo = "Adjunto factura correspondiente"
    
    carpeta, prioridad = motor.clasificar_correo(remitente, asunto, cuerpo)
    print(f"Clasificación: {carpeta} (prioridad: {prioridad})")
    
    # Probar con CCP
    asunto_ccp = "Solicitud CCP"
    cuerpo_ccp = "Se solicita Carta Porte"
    carpeta_ccp, prioridad_ccp = motor.clasificar_correo(remitente, asunto_ccp, cuerpo_ccp)
    print(f"Clasificación CCP: {carpeta_ccp} (prioridad: {prioridad_ccp})")
    
    print("\nPrueba completada exitosamente!")
    
    # Cerrar conexión
    motor.cerrar_conexion()
    
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de que pywin32 esté instalado correctamente")
except Exception as e:
    print(f"Error durante la prueba: {e}")
    print("Asegúrate de que Outlook esté abierto y con sesión iniciada")

input("\nPresiona Enter para salir...")
