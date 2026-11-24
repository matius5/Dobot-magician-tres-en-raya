
import pydobot
import traceback
from serial.tools import list_ports

PUERTO = "COM3"
robot = None

print("=== DIAGNOSTICO DOBOT ===")

try:
    print("\nPASO 1: Comprobando COM3")

    puertos = [p.device for p in list_ports.comports()]
    print("Puertos:", puertos)

    if PUERTO not in puertos:
        raise RuntimeError("COM3 no esta disponible")

    print("\nPASO 2: Conectando al robot")

    robot = pydobot.Dobot(
        port=PUERTO,
        verbose=False
    )

    print("Conexion establecida")

    print("\nPASO 3: Leyendo posicion")

    posicion = robot.pose()
    print("Respuesta:", posicion)

    if len(posicion) != 8:
        raise RuntimeError(
            f"Respuesta incompleta: {len(posicion)} valores"
        )

    x, y, z, r, j1, j2, j3, j4 = posicion

    print("\nCOORDENADAS ACTUALES")
    print(f"X: {x:.4f}")
    print(f"Y: {y:.4f}")
    print(f"Z: {z:.4f}")
    print(f"R: {r:.4f}")

    print("\nDIAGNOSTICO DE LECTURA COMPLETADO")
    print("No se enviaron comandos de movimiento.")

except Exception:
    print("\n=== ERROR DETECTADO ===")
    traceback.print_exc()

finally:
    if robot is not None:
        try:
            robot.close()
            print("\nPuerto COM3 liberado")
        except Exception:
            traceback.print_exc()
