
import cv2
import json
import random
import time
from pathlib import Path
import numpy as np

CONFIG = Path("calibracion_vision.json")
BASE = Path("datos") / "dataset"
CLASES = {"X": "X", "O": "O", ".": "vacia"}

with open(CONFIG, encoding="utf-8") as f:
    config = json.load(f)

camara = config["camara"]
tamano = config["tamano"]
puntos = np.float32(config["puntos"])

destino = np.float32([
    [0, 0],
    [tamano - 1, 0],
    [tamano - 1, tamano - 1],
    [0, tamano - 1]
])

matriz = cv2.getPerspectiveTransform(puntos, destino)

for grupo in ("train", "val"):
    for clase in CLASES.values():
        (BASE / grupo / clase).mkdir(
            parents=True, exist_ok=True
        )

cap = cv2.VideoCapture(camara, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la camara")

contador = 0

print("=== RECOLECTOR DE DATOS ===")
print("C = capturar el tablero")
print("Q = salir")
print("X = cruz, O = circulo, . = vacia")
print("Ejemplo: X.O...O.X")
print("El orden de las casillas es 1 a 9.")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    tablero = cv2.warpPerspective(
        frame, matriz, (tamano, tamano)
    )

    vista = tablero.copy()
    paso = tamano // 3

    for i in (1, 2):
        cv2.line(
            vista, (i * paso, 0),
            (i * paso, tamano),
            (0, 255, 0), 2
        )
        cv2.line(
            vista, (0, i * paso),
            (tamano, i * paso),
            (0, 255, 0), 2
        )

    cv2.putText(
        vista, "C: CAPTURAR | Q: SALIR",
        (12, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 0, 255), 2
    )

    cv2.imshow("RECOLECTAR DATOS", vista)

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord("q"):
        break

    if tecla == ord("c"):
        print("\nCaptura solicitada.")
        print("Ve a la terminal de VS Code.")

        estado = input(
            "Escribe las 9 casillas (X, O o .): "
        ).strip().upper().replace(" ", "")

        if len(estado) != 9 or any(
            simbolo not in CLASES for simbolo in estado
        ):
            print("ERROR: introduce exactamente 9 simbolos.")
            continue

        # Un tablero completo pertenece a un solo grupo.
        # Esto reduce la filtracion entre train y val.
        grupo = "val" if random.random() < 0.2 else "train"

        contador += 1
        identificador = f"{time.time_ns()}_{contador}"

        for fila in range(3):
            for columna in range(3):
                indice = fila * 3 + columna
                clase = CLASES[estado[indice]]

                # Usar la region central para evitar bordes.
                margen = int(paso * 0.14)

                x1 = columna * paso + margen
                y1 = fila * paso + margen
                x2 = (columna + 1) * paso - margen
                y2 = (fila + 1) * paso - margen

                recorte = tablero[y1:y2, x1:x2]

                ruta = (
                    BASE / grupo / clase /
                    f"{identificador}_c{indice + 1}.jpg"
                )

                cv2.imwrite(str(ruta), recorte)

        print(
            f"Guardadas 9 imagenes en {grupo}: {estado}"
        )
        print(
            "Puedes cambiar las fichas y capturar otra vez."
        )

cap.release()
cv2.destroyAllWindows()

print("\nRecoleccion finalizada.")
