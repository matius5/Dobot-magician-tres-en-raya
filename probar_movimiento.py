
import pydobot
import math

PUERTO = "COM3"

# Primera prueba: elevar solo 5 mm
DESPLAZAMIENTO_Z = 5.0

# Referencia medida de la casilla 9
REFERENCIA_X = 193.9535
REFERENCIA_Y = -14.2731

robot = None

try:
    robot = pydobot.Dobot(port=PUERTO, verbose=False)

    x, y, z, r, *_ = robot.pose()

    print("=== POSICION INICIAL ===")
    print(f"X={x:.3f}, Y={y:.3f}, Z={z:.3f}, R={r:.3f}")

    distancia = math.hypot(
        x - REFERENCIA_X,
        y - REFERENCIA_Y
    )

    if distancia > 3.0:
        raise RuntimeError(
            "El robot cambio de posicion. "
            "Revisar las coordenadas antes de mover."
        )

    destino_z = z + DESPLAZAMIENTO_Z

    print("\nMovimiento propuesto:")
    print(f"X={x:.3f}, Y={y:.3f}")
    print(f"Z inicial={z:.3f}")
    print(f"Z destino={destino_z:.3f}")
    print("Solo se elevara el lapiz 5 mm.")

    respuesta = input(
        "\nEscribe MOVER para autorizar: "
    ).strip()

    if respuesta != "MOVER":
        print("Movimiento cancelado.")
    else:
        robot.speed(20, 20)

        robot.move_to(
            x, y, destino_z, r,
            wait=True
        )

        xf, yf, zf, rf, *_ = robot.pose()

        print("\n=== POSICION FINAL ===")
        print(f"X={xf:.3f}")
        print(f"Y={yf:.3f}")
        print(f"Z={zf:.3f}")
        print(f"R={rf:.3f}")

        error = abs(zf - destino_z)
        print(f"Error Z: {error:.3f} mm")

        if error > 2.0:
            print("ADVERTENCIA: revisar movimiento.")

except Exception as e:
    print("ERROR:", type(e).__name__, str(e))

finally:
    if robot is not None:
        robot.close()
        print("Conexion cerrada.")
