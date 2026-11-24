
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
TAMANO_X = 18.0
VELOCIDAD = 70
ACELERACION = 70

centro = casillas[CASILLA].copy()


# Altura comun por encima de todos los centros
z_segura = max(p[2] for p in casillas.values()) + 15.0

# Vectores del tablero
horizontal = casillas[3][:2] - casillas[1][:2]
vertical = casillas[7][:2] - casillas[1][:2]

horizontal /= np.linalg.norm(horizontal)
vertical /= np.linalg.norm(vertical)

mitad = TAMANO_X / 2

A = centro[:2] - horizontal * mitad - vertical * mitad
B = centro[:2] + horizontal * mitad + vertical * mitad
C = centro[:2] + horizontal * mitad - vertical * mitad
D = centro[:2] - horizontal * mitad + vertical * mitad

puntos = [("A", A), ("B", B), ("C", C), ("D", D)]

print("\n=== DOBOT: PRUEBA X CASILLA 5 ===")
print("Modo: trayectoria elevada, SIN contacto")
print(f"Z de prueba: {z_segura:.3f}")

for nombre, punto in puntos:
    print(
        f"{nombre}: X={punto[0]:.3f}, "
        f"Y={punto[1]:.3f}"
    )

print("\nEl robot recorrera A-B y C-D.")
print("Verifica que no haya obstaculos.")

respuesta = input(
    "\nEscribe PROBAR para comenzar: "
).strip()

if respuesta != "PROBAR":
    raise SystemExit("Prueba cancelada")

robot = None

try:
    robot = pydobot.Dobot(
        port=cfg["puerto"],
        verbose=False
    )

    robot.speed(VELOCIDAD, ACELERACION)

    x, y, z, r, *_ = robot.pose()

    # Primero alcanzar la altura libre
    if z < z_segura:
        robot.move_to(x, y, z_segura, r, wait=True)

    def mover(punto):
        robot.move_to(
            float(punto[0]),
            float(punto[1]),
            float(z_segura),
            float(centro[3]),
            wait=True
        )

    print("\nPrimer trazo elevado")
    mover(A)
    mover(B)

    print("Segundo trazo elevado")
    mover(C)
    mover(D)

    # Retirar hacia el centro a altura libre
    mover(centro[:2])

    print("\nPRUEBA FINALIZADA")
    print("La punta debe quedar elevada sobre la casilla 5.")

except Exception:
    traceback.print_exc()

finally:
    if robot is not None:
        robot.close()
        print("Conexion COM3 cerrada.")
