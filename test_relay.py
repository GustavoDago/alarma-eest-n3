import serial
import time
import os
import platform

# Configuración: Intenta usar /dev/ttyUSB0 en Linux y COM3 en Windows por defecto
DEFAULT_PORT = '/dev/ttyUSB0' if platform.system() != 'Windows' else 'COM3'
PORT = os.getenv('RELAY_PORT', DEFAULT_PORT)
BAUD_RATE = 9600

# Comandos Hexadecimales LCUS-1
CMD_ON = bytes([0xA0, 0x01, 0x01, 0xA2])
CMD_OFF = bytes([0xA0, 0x01, 0x00, 0xA1])

def run_test():
    print(f"🚀 Iniciando prueba de relé en {platform.system()}...")
    print(f"🔌 Intentando conectar al puerto: {PORT}")
    
    try:
        # Abrir el puerto serial
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        
        for i in range(1, 3):
            print(f"🔔 Click #{i}: ENCENDIDO")
            ser.write(CMD_ON)
            time.sleep(0.8)
            
            print(f"🔕 Click #{i}: APAGADO")
            ser.write(CMD_OFF)
            
            if i < 2:
                print("...esperando 1 segundo...")
                time.sleep(1)
        
        ser.close()
        print("\n✨ Prueba finalizada exitosamente.")
        
    except serial.SerialException as e:
        print(f"\n❌ Error de conexión: {e}")
        print(f"💡 Tip: Si estás en Debian, verifica que el puerto sea '{PORT}' y que tengas permisos.")
        print("   Puedes probar con: sudo usermod -a -G dialout $USER (y reiniciar sesión)")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    run_test()
