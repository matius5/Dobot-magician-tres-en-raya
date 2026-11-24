
import json
import pydobot
import traceback

with open("calibracion_dobot.json", encoding="utf-8") as f:
    cfg = json.load(f)

casilla = cfg["casillas"]["5"]

X = float(casilla[0])
Y = float(casilla[1])
Z_CONTACTO = float(casilla[2])
R = float(casilla[3])

# Altura libre provisional, basada en la calibracion.
Z_LIBRE = max(
    float(p[2]) for p in cfg["casillas"].values()
) + cfg["altura_seguridad_mm"]

print("\n=== VERIFICACION CENTRO CASILLA 5 ===")
print(f"X: {X:.4f}")
print(f"Y: {Y:.4f}")
print(f"Z libre: {Z_LIBRE:.4f}")
print(f"R: {R:.4f}")
print("No se tocara el tablero.")

confirmar = input(
    "\nEscribe CENTRO para autorizar: "
).strip()

if confirmar != "CENTRO":
    raise SystemExit("Cancelado")

robot = None

try:
    robot = pydobot.Dobot(
        port=cfg["puerto"],
        verbose=False
    )

    robot.speed(20, 20)

    x0, y0, z0, r0, *_ = robot.pose()

    # Elevar antes de desplazar horizontalmente.
    z_traslado = max(z0, Z_LIBRE)

    robot.move_to(
        x0, y0, z_traslado, r0,
        wait=True
    )

    robot.move_to(
        X, Y, z_traslado, R,
        wait=True
    )

    # Descender solo hasta la altura libre
    # previamente definida.
    if z_traslado > Z_LIBRE:
        robot.move_to(
            X, Y, Z_LIBRE, R,
            wait=True
        )

    xf, yf, zf, rf, *_ = robot.pose()

    print("\nPOSICION FINAL")
    print(f"X={xf:.4f}")
    print(f"Y={yf:.4f}")
    print(f"Z={zf:.4f}")
    print(f"R={rf:.4f}")

except Exception:
    traceback.print_exc()

finally:
    if robot is not None:
        robot.close()
        print("Conexion cerrada")
