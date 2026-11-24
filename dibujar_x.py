
import json
import numpy as np
import pydobot
import traceback

with open("calibracion_dobot.json", encoding="utf-8") as f:
    cfg = json.load(f)

casillas = {
    int(k): np.array(v, dtype=float)
    for k, v in cfg["casillas"].items()
}

CASILLA = 5
TAMANO = float(cfg["tamano_x_mm"])

VELOCIDAD_LIBRE = 30
VELOCIDAD_CONTACTO = 10

centro = casillas[CASILLA].copy()
z_contacto = float(centro[2])
r = float(centro[3])

# Altura de traslado, por encima de los centros medidos.
z_libre = max(p[2] for p in casillas.values()) + 15.0

# Direcciones del tablero
horizontal = casillas[3][:2] - casillas[1][:2]
vertical = casillas[7][:2] - casillas[1][:2]

horizontal /= np.linalg.norm(horizontal)
vertical /= np.linalg.norm(vertical)

mitad = TAMANO / 2.0

A = centro[:2] - horizontal * mitad - vertical * mitad
B = centro[:2] + horizontal * mitad + vertical * mitad
C = centro[:2] + horizontal * mitad - vertical * mitad
D = centro[:2] - horizontal * mitad + vertical * mitad

robot = None


def mover(x, y, z, velocidad):
    robot.speed(velocidad, velocidad)
    robot.move_to(
        float(x), float(y), float(z), r,
        wait=True
    )


def trazo(inicio, fin):
    # Posicionarse sobre el inicio
    mover(inicio[0], inicio[1], z_libre, VELOCIDAD_LIBRE)

    # Bajar hasta contacto
    mover(inicio[0], inicio[1], z_contacto, VELOCIDAD_CONTACTO)

    # Dibujar diagonal
    mover(fin[0], fin[1], z_contacto, VELOCIDAD_CONTACTO)

    # Levantar el lapiz
    mover(fin[0], fin[1], z_libre, VELOCIDAD_LIBRE)


print("=== DIBUJAR X - CASILLA 5 ===")
print(f"Centro: {centro[:2]}")
print(f"Z contacto: {z_contacto:.4f}")
print(f"Z libre: {z_libre:.4f}")
print("Se dibujaran dos diagonales de 18 mm.")

confirmacion = input(
    "\nEscribe DIBUJAR para autorizar: "
).strip()

if confirmacion != "DIBUJAR":
    raise SystemExit("Cancelado")

try:
    robot = pydobot.Dobot(
        port=cfg["puerto"],
        verbose=False
    )

    x, y, z, r_actual, *_ = robot.pose()

    # Elevar antes de trasladar
    z_traslado = max(z, z_libre)
    mover(x, y, z_traslado, VELOCIDAD_LIBRE)

    print("\nDibujando primera diagonal...")
    trazo(A, B)

    print("Dibujando segunda diagonal...")
    trazo(C, D)

    # Volver al centro a altura libre
    mover(centro[0], centro[1], z_libre, VELOCIDAD_LIBRE)

    print("\nX COMPLETADA")

except Exception:
    traceback.print_exc()

finally:
    if robot is not None:
        robot.close()
        print("Conexion COM3 cerrada.")
