
import json
import math
import traceback
import numpy as np
import pydobot

# =========================================
# CONFIGURACION
# =========================================

with open("calibracion_dobot.json", encoding="utf-8") as f:
    cfg = json.load(f)

CASILLAS = {
    int(k): np.array(v, dtype=float)
    for k, v in cfg["casillas"].items()
}

PUERTO = cfg["puerto"]
TAMANO = float(cfg["tamano_x_mm"])
MARGEN_Z = float(cfg["altura_seguridad_mm"])

VELOCIDAD_LIBRE = 60
VELOCIDAD_DIBUJO = 60

# Altura elevada comun
Z_SEGURA = max(c[2] for c in CASILLAS.values()) + MARGEN_Z

# Direcciones del tablero
H = CASILLAS[3][:2] - CASILLAS[1][:2]
V = CASILLAS[7][:2] - CASILLAS[1][:2]

H = H / np.linalg.norm(H)
V = V / np.linalg.norm(V)

robot = None


def puntos_x(numero):
    centro = CASILLAS[numero]
    xy = centro[:2]
    mitad = TAMANO / 2.0

    a = xy - H * mitad - V * mitad
    b = xy + H * mitad + V * mitad
    c = xy + H * mitad - V * mitad
    d = xy - H * mitad + V * mitad

    return a, b, c, d


def mover(x, y, z, r, velocidad):
    robot.speed(velocidad, velocidad)
    robot.move_to(
        float(x),
        float(y),
        float(z),
        float(r),
        wait=True
    )


def elevar():
    x, y, z, r, *_ = robot.pose()

    if z < Z_SEGURA:
        mover(x, y, Z_SEGURA, r, VELOCIDAD_LIBRE)


def mover_elevado(x, y, r):
    elevar()
    mover(x, y, Z_SEGURA, r, VELOCIDAD_LIBRE)


def verificar_centro(numero):
    x, y, z, r = CASILLAS[numero]

    print(f"\nVerificando centro de casilla {numero}")
    mover_elevado(x, y, r)

    print("Centro alcanzado a altura elevada.")
    print(f"X={x:.4f}, Y={y:.4f}, Z={Z_SEGURA:.4f}")


def trayectoria_elevada(numero):
    r = CASILLAS[numero][3]
    a, b, c, d = puntos_x(numero)

    print(f"\nTRAYECTORIA ELEVADA CASILLA {numero}")

    for nombre, punto in zip("ABCD", (a, b, c, d)):
        mover_elevado(punto[0], punto[1], r)
        print(f"Punto {nombre} alcanzado")

    verificar_centro(numero)


def dibujar_trazo(inicio, fin, z, r):
    # Situarse sobre el inicio a altura libre
    mover_elevado(inicio[0], inicio[1], r)

    # Bajar suavemente
    mover(
        inicio[0], inicio[1], z, r,
        VELOCIDAD_DIBUJO
    )

    # Dividir el trazo en segmentos pequeños
    # para controlar mejor el recorrido.
    segmentos = 1

    for i in range(1, segmentos + 1):
        t = i / segmentos
        xy = inicio + (fin - inicio) * t

        mover(
            xy[0], xy[1], z, r,
            VELOCIDAD_DIBUJO
        )

    # Levantar antes del siguiente trazo
    mover(
        fin[0], fin[1], Z_SEGURA, r,
        VELOCIDAD_LIBRE
    )


def dibujar_x(numero):
    x, y, z, r = CASILLAS[numero]
    a, b, c, d = puntos_x(numero)

    print(f"\nDIBUJANDO X EN CASILLA {numero}")
    print(f"Z contacto: {z:.4f}")

    dibujar_trazo(a, b, z, r)
    dibujar_trazo(c, d, z, r)

    mover_elevado(x, y, r)
    print(f"\nX TERMINADA EN CASILLA {numero}")


# =========================================
# PROGRAMA PRINCIPAL
# =========================================

print("\n=== DOBOT - PRUEBA DE CASILLAS ===")
print("Las coordenadas se leen del archivo JSON.")

print("\nCasillas disponibles: 1 a 9")
print("Casilla 5: ya fue probada.")

numero = int(input("\nQue casilla deseas probar? "))

if numero not in CASILLAS:
    raise SystemExit("Casilla invalida")

if numero == 5:
    raise SystemExit(
        "La casilla 5 ya esta ocupada. "
        "Prueba otra casilla."
    )

print("\nCentro seleccionado:")
print(CASILLAS[numero])
print(f"Z elevada propuesta: {Z_SEGURA:.4f}")

print("\nMODOS:")
print("1 = Verificar centro elevado")
print("2 = Probar trayectoria elevada")
print("3 = Dibujar X fisicamente")

modo = input("\nSelecciona 1, 2 o 3: ").strip()

if modo not in ("1", "2", "3"):
    raise SystemExit("Modo invalido")

if modo == "3":
    print("\nATENCION:")
    print("Verifica que la casilla este vacia.")
    print("Confirma centro, altura y contacto.")
    print("Supervisa los movimientos.")

confirmar = input(
    "\nEscribe AUTORIZAR para continuar: "
).strip()

if confirmar != "AUTORIZAR":
    raise SystemExit("Operacion cancelada")

try:
    robot = pydobot.Dobot(
        port=PUERTO,
        verbose=False
    )

    if modo == "1":
        verificar_centro(numero)

    elif modo == "2":
        trayectoria_elevada(numero)

    elif modo == "3":
        # Autorizacion adicional para contacto
        # antes del primer trazo.
        respuesta = input(
            "Escribe CONTACTO para permitir "
            "el dibujo fisico: "
        ).strip()

        if respuesta == "CONTACTO":
            dibujar_x(numero)
        else:
            print("Dibujo cancelado")

except Exception:
    print("\nERROR DURANTE LA OPERACION")
    traceback.print_exc()
    print("Revisar el robot antes de repetir.")

finally:
    if robot is not None:
        robot.close()
        print("\nPuerto COM3 liberado.")
