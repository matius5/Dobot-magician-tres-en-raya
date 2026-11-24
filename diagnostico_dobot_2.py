
import serial
import pydobot
import traceback
from serial.tools import list_ports

PUERTO = "COM3"

print("=== DIAGNOSTICO SEGUNDO DOBOT ===")

print("\n1. Puertos detectados:")
for p in list_ports.comports():
    print(p.device, "-", p.description)

print("\n2. Comprobando acceso a COM3")

try:
    with serial.Serial(
        port=PUERTO,
        baudrate=115200,
        timeout=2
    ) as conexion:
        print("COM3 abierto correctamente")
except Exception:
    print("ERROR al abrir COM3")
    traceback.print_exc()
    raise SystemExit

print("\n3. Probando comunicacion con pydobot")

robot = None

try:
    robot = pydobot.Dobot(
        port=PUERTO,
        verbose=True
    )

    print("\nCONEXION EXITOSA")
    print("Posicion:", robot.pose())

except Exception:
    print("\nERROR DE COMUNICACION")
    traceback.print_exc()

finally:
    if robot is not None:
        robot.close()

print("\nDiagnostico finalizado.")
print("No se ordenaron movimientos.")
