import time
import serial
import os
import platform

# Configuración del puerto - Se puede sobrescribir con una variable de entorno
# En Windows suele ser COM1, COM2, etc. En Linux /dev/ttyUSB0
DEFAULT_PORT = 'COM3' if platform.system() == 'Windows' else '/dev/ttyUSB0'
SERIAL_PORT = os.getenv('RELAY_PORT', DEFAULT_PORT)
BAUD_RATE = 9600

# Comandos Hexadecimales para el módulo LCUS-1 (CH340)
# Formato: [ID, Dirección, Estado, Checksum]
CMD_ON = bytes([0xA0, 0x01, 0x01, 0xA2])
CMD_OFF = bytes([0xA0, 0x01, 0x00, 0xA1])

def trigger_relay(duration_seconds):
    """
    Esta función maneja la conexión física con el Relé USB.
    Envía la señal de encendido, espera el tiempo de duración y lo apaga.
    """
    ser = None
    try:
        print(f"🔌 [HARDWARE] Intentando abrir puerto {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        
        print("🔌 [HARDWARE] Enviando señal de ENCENDIDO al Relé...")
        ser.write(CMD_ON)
        
        time.sleep(duration_seconds)
        
        print("🔌 [HARDWARE] Enviando señal de APAGADO al Relé...")
        ser.write(CMD_OFF)
        
    except Exception as e:
        print(f"❌ [ERROR HARDWARE] Error al comunicarse con el relé: {e}")
        print(f"💡 Tip: Verifica que el relé esté conectado y que el puerto '{SERIAL_PORT}' sea el correcto.")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("🔌 [HARDWARE] Puerto serial cerrado.")
