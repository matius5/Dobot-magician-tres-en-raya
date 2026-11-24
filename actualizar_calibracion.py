
import json
import math
import shutil
from pathlib import Path
from datetime import datetime

ARCHIVO = Path("calibracion_dobot.json")


def pedir_coordenadas(numero):
    print(f"\n=== CENTRO CASILLA {numero} ===")
    print("Introduce los valores de DobotStudio.")

    valores = []

    for eje in ["X", "Y", "Z", "R"]:
        while True:
            try:
                entrada = input(f"{eje}: ").strip()
                valor = float(entrada.replace(",", "."))

                if not math.isfinite(valor):
                    raise ValueError

                valores.append(valor)
                break

            except ValueError:
                print("Valor no valido. Intenta otra vez.")

    return valores


def interpolar(esquinas, fila, columna):
    u = columna / 2.0
    v = fila / 2.0

    p1 = esquinas[1]
    p3 = esquinas[3]
    p7 = esquinas[7]
    p9 = esquinas[9]

    resultado = []

    for i in range(4):
        valor = (
            (1 - u) * (1 - v) * p1[i]
            + u * (1 - v) * p3[i]
            + (1 - u) * v * p7[i]
            + u * v * p9[i]
        )

        resultado.append(round(valor, 4))

    return resultado


print("\n=== CALIBRACION AUTOMATICA DOBOT ===")
print("Segundo DOBOT Magician")
print("Mide los centros de las casillas 1, 3, 7 y 9.")
print("La Z debe corresponder al contacto suave.")

esquinas = {}

for numero in [1, 3, 7, 9]:
    esquinas[numero] = pedir_coordenadas(numero)

casillas = {}

for fila in range(3):
    for columna in range(3):
        numero = fila * 3 + columna + 1

        casillas[str(numero)] = interpolar(
            esquinas, fila, columna
        )

print("\n=== NUEVAS COORDENADAS ===")

for numero, posicion in casillas.items():
    x, y, z, r = posicion

    print(
        f"Casilla {numero}: "
        f"X={x:.4f} "
        f"Y={y:.4f} "
        f"Z={z:.4f} "
        f"R={r:.4f}"
    )

print("\nEstas coordenadas reemplazaran las anteriores.")
confirmar = input(
    "Escribe GUARDAR para confirmar: "
).strip()

if confirmar != "GUARDAR":
    raise SystemExit("Calibracion cancelada.")

if ARCHIVO.exists():
    with ARCHIVO.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo = ARCHIVO.with_name(
        f"calibracion_dobot_backup_{fecha}.json"
    )

    shutil.copy2(ARCHIVO, respaldo)
    print("Respaldo creado:", respaldo)

else:
    cfg = {
        "puerto": "COM3",
        "tamano_x_mm": 18.0,
        "altura_seguridad_mm": 15.0,
        "tolerancia_mm": 0.0
    }

cfg["casillas"] = casillas

# No conservar ajustes especificos del primer robot.
cfg["offset_x_mm"] = 0.0
cfg["offset_y_mm"] = 0.0

# El reposo del segundo robot debe validarse por separado.
cfg["reposo_validado"] = False

# Guardar las referencias originales.
cfg["esquinas_calibracion"] = {
    str(k): v for k, v in esquinas.items()
}

with ARCHIVO.open("w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

print("\nCALIBRACION GUARDADA CORRECTAMENTE")
print("Archivo:", ARCHIVO)
print("Los centros anteriores fueron reemplazados.")
print("No se realizaron movimientos del robot.")
print("RECUERDA: validar la nueva posicion de reposo.")
