
import cv2
import numpy as np
import json
from pathlib import Path

CAMARA = 0
TAMANO = 600

puntos = []
archivo = Path("calibracion_vision.json")


def seleccionar_esquina(evento, x, y, flags, param):
    if evento == cv2.EVENT_LBUTTONDOWN and len(puntos) < 4:
        puntos.append([x, y])
        print(f"Esquina {len(puntos)}: ({x}, {y})")


def corregir_perspectiva(imagen):
    origen = np.float32(puntos)

    destino = np.float32([
        [0, 0],
        [TAMANO - 1, 0],
        [TAMANO - 1, TAMANO - 1],
        [0, TAMANO - 1]
    ])

    matriz = cv2.getPerspectiveTransform(origen, destino)

    return cv2.warpPerspective(
        imagen, matriz, (TAMANO, TAMANO)
    )


def dibujar_casillas(imagen):
    resultado = imagen.copy()
    paso = TAMANO // 3

    for i in range(1, 3):
        cv2.line(
            resultado, (i * paso, 0),
            (i * paso, TAMANO), (0, 255, 0), 2
        )
        cv2.line(
            resultado, (0, i * paso),
            (TAMANO, i * paso), (0, 255, 0), 2
        )

    for fila in range(3):
        for columna in range(3):
            numero = fila * 3 + columna + 1
            cx = columna * paso + paso // 2
            cy = fila * paso + paso // 2

            cv2.putText(
                resultado, str(numero),
                (cx - 12, cy + 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (0, 0, 255), 3
            )

    return resultado


cap = cv2.VideoCapture(CAMARA, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la camara.")

cv2.namedWindow("CALIBRAR TABLERO")
cv2.setMouseCallback("CALIBRAR TABLERO", seleccionar_esquina)

print("=== CALIBRACION DEL TABLERO ===")
print("Selecciona las cuatro esquinas en orden:")
print("1. Superior izquierda")
print("2. Superior derecha")
print("3. Inferior derecha")
print("4. Inferior izquierda")
print("R = reiniciar")
print("G = guardar calibracion")
print("Q = salir")

while True:
    ok, frame = cap.read()

    if not ok:
        print("Error de captura.")
        break

    vista = frame.copy()

    for i, (x, y) in enumerate(puntos):
        cv2.circle(vista, (x, y), 6, (0, 0, 255), -1)
        cv2.putText(
            vista, str(i + 1), (x + 8, y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2
        )

    if len(puntos) == 4:
        tablero = corregir_perspectiva(frame)
        tablero = dibujar_casillas(tablero)
        cv2.imshow("TABLERO CORREGIDO", tablero)

    cv2.imshow("CALIBRAR TABLERO", vista)

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord("r"):
        puntos.clear()
        cv2.destroyWindow("TABLERO CORREGIDO") if (
            cv2.getWindowProperty(
                "TABLERO CORREGIDO", cv2.WND_PROP_VISIBLE
            ) >= 0
        ) else None
        print("Calibracion reiniciada.")

    elif tecla == ord("g") and len(puntos) == 4:
        datos = {
            "camara": CAMARA,
            "tamano": TAMANO,
            "puntos": puntos
        }

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)

        print(f"Calibracion guardada: {archivo}")

    elif tecla == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
