
import json
import numpy as np

with open("calibracion_dobot.json", encoding="utf-8") as f:
    cfg = json.load(f)

casillas = {
    int(k): np.array(v, dtype=float)
    for k, v in cfg["casillas"].items()
}

TAMANO_X = cfg["tamano_x_mm"]
ALTURA_SEGURA = cfg["altura_seguridad_mm"]

# Direcciones del tablero: casillas 1-3 y 1-7.
horizontal = casillas[3][:2] - casillas[1][:2]
vertical = casillas[7][:2] - casillas[1][:2]

horizontal /= np.linalg.norm(horizontal)
vertical /= np.linalg.norm(vertical)

angulo = np.degrees(
    np.arccos(
        np.clip(np.dot(horizontal, vertical), -1, 1)
    )
)

print(f"Angulo entre ejes: {angulo:.2f} grados")


def generar_x(numero):
    x, y, z, r = casillas[numero]

    centro = np.array([x, y])
    mitad = TAMANO_X / 2

    a = centro - horizontal * mitad - vertical * mitad
    b = centro + horizontal * mitad + vertical * mitad

    c = centro + horizontal * mitad - vertical * mitad
    d = centro - horizontal * mitad + vertical * mitad

    z_libre = z + ALTURA_SEGURA

    return [
        ("Aproximar A", *a, z_libre, r),
        ("Contacto A", *a, z, r),
        ("Dibujar B", *b, z, r),
        ("Levantar B", *b, z_libre, r),
        ("Aproximar C", *c, z_libre, r),
        ("Contacto C", *c, z, r),
        ("Dibujar D", *d, z, r),
        ("Levantar D", *d, z_libre, r)
    ]


print("\n=== NUEVAS TRAYECTORIAS ===")
print("SOLO CALCULO: EL ROBOT NO SE MOVERA")

for numero in range(1, 10):
    print(f"\nCASILLA {numero}")

    for paso in generar_x(numero):
        accion, x, y, z, r = paso

        print(
            f"{accion:14s}"
            f"X={x:8.3f} "
            f"Y={y:8.3f} "
            f"Z={z:8.3f} "
            f"R={r:7.3f}"
        )
