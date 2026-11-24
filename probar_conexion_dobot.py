
import pydobot
from serial.tools import list_ports

PUERTO = "COM3"

print("=== CONEXION DOBOT MAGICIAN ===")

print("\nPuertos disponibles:")
for puerto in list_ports.comports():
    print(puerto.device, "-", puerto.description)

robot = None

try:
    print(f"\nConectando al DOBOT en {PUERTO}...")

    robot = pydobot.Dobot(
        port=PUERTO,
        verbose=False
    )

    print("CONEXION ESTABLECIDA")

    # Solo consultar posicion, sin mover.
    pose = robot.pose()

    x, y, z, r, j1, j2, j3, j4 = pose

    print("\n=== POSICION ACTUAL ===")
    print(f"X: {x:.4f} mm")
    print(f"Y: {y:.4f} mm")
    print(f"Z: {z:.4f} mm")
    print(f"R: {r:.4f} grados")

    print("\n=== ARTICULACIONES ===")
    print(f"J1: {j1:.4f}")
    print(f"J2: {j2:.4f}")
    print(f"J3: {j3:.4f}")
    print(f"J4: {j4:.4f}")

    print("\nPRUEBA FINALIZADA SIN MOVIMIENTOS")

except Exception as error:
    print("\nERROR DE CONEXION:")
    print(type(error).__name__, str(error))

finally:
    if robot is not None:
        robot.close()
        print("\nPuerto COM3 liberado.")
