
import cv2
import json
import numpy as np
from pathlib import Path
from collections import deque
from ultralytics import YOLO

# ====================================
# CONFIGURACION
# ====================================

CAMARA = 0
CONFIANZA = 0.40
ESTABILIDAD = 5
ARCHIVO_MODELO = "modelos/hf_tictactoe/weights/best.onnx"
ARCHIVO_CALIBRACION = "calibracion_vision.json"

# El robot juega X y comienza la partida.
ROBOT = "X"
HUMANO = "O"
VACIO = "."

# ====================================
# CARGAR MODELO Y CALIBRACION
# ====================================

if not Path(ARCHIVO_MODELO).exists():
    raise FileNotFoundError(ARCHIVO_MODELO)

modelo = YOLO(ARCHIVO_MODELO, task="detect")

with open(ARCHIVO_CALIBRACION, encoding="utf-8") as f:
    config = json.load(f)

tamano = config["tamano"]
origen = np.float32(config["puntos"])

destino = np.float32([
    [0, 0],
    [tamano - 1, 0],
    [tamano - 1, tamano - 1],
    [0, tamano - 1]
])

matriz = cv2.getPerspectiveTransform(origen, destino)

# ====================================
# LOGICA DEL TRES EN RAYA
# ====================================

LINEAS = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6)
]


def ganador(tablero):
    for a, b, c in LINEAS:
        if (
            tablero[a] != VACIO
            and tablero[a] == tablero[b] == tablero[c]
        ):
            return tablero[a]

    if VACIO not in tablero:
        return "EMPATE"

    return None


def minimax(tablero, turno, profundidad=0,
            alfa=-1000, beta=1000):

    resultado = ganador(tablero)

    if resultado == ROBOT:
        return 10 - profundidad, None

    if resultado == HUMANO:
        return profundidad - 10, None

    if resultado == "EMPATE":
        return 0, None

    mejor_casilla = None

    # Priorizar el centro, esquinas y lados.
    orden = [4, 0, 2, 6, 8, 1, 3, 5, 7]

    if turno == ROBOT:
        mejor_puntuacion = -1000

        for i in orden:
            if tablero[i] != VACIO:
                continue

            tablero[i] = ROBOT

            puntuacion, _ = minimax(
                tablero, HUMANO,
                profundidad + 1, alfa, beta
            )

            tablero[i] = VACIO

            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_casilla = i

            alfa = max(alfa, mejor_puntuacion)

            if beta <= alfa:
                break

        return mejor_puntuacion, mejor_casilla

    else:
        mejor_puntuacion = 1000

        for i in orden:
            if tablero[i] != VACIO:
                continue

            tablero[i] = HUMANO

            puntuacion, _ = minimax(
                tablero, ROBOT,
                profundidad + 1, alfa, beta
            )

            tablero[i] = VACIO

            if puntuacion < mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_casilla = i

            beta = min(beta, mejor_puntuacion)

            if beta <= alfa:
                break

        return mejor_puntuacion, mejor_casilla


def turno_actual(tablero):
    cantidad_x = tablero.count("X")
    cantidad_o = tablero.count("O")

    # El robot X siempre comienza.
    if cantidad_x == cantidad_o:
        return ROBOT

    if cantidad_x == cantidad_o + 1:
        return HUMANO

    return "INVALIDO"


# ====================================
# VISION ARTIFICIAL
# ====================================

def reconocer_tablero(frame):
    tablero = [VACIO] * 9
    confianzas = [0.0] * 9

    resultados = modelo.predict(
        frame,
        conf=CONFIANZA,
        imgsz=640,
        device="cpu",
        verbose=False
    )[0]

    vista = resultados.plot()

    for caja in resultados.boxes:
        clase = modelo.names[int(caja.cls[0])]
        confianza = float(caja.conf[0])

        if clase not in ("X", "O"):
            continue

        x1, y1, x2, y2 = caja.xyxy[0].tolist()

        centro = np.float32([[
            [(x1 + x2) / 2, (y1 + y2) / 2]
        ]])

        corregido = cv2.perspectiveTransform(
            centro, matriz
        )

        x, y = corregido[0][0]

        if not (0 <= x < tamano and 0 <= y < tamano):
            continue

        columna = min(2, int(x * 3 / tamano))
        fila = min(2, int(y * 3 / tamano))

        indice = fila * 3 + columna

        if confianza > confianzas[indice]:
            tablero[indice] = clase
            confianzas[indice] = confianza

    return tablero, vista


def dibujar_tablero(frame, tablero, sugerencia):
    vista = cv2.warpPerspective(
        frame, matriz, (tamano, tamano)
    )

    paso = tamano // 3

    for i in range(1, 3):
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

    for indice in range(9):
        fila, columna = divmod(indice, 3)

        cx = columna * paso + paso // 2
        cy = fila * paso + paso // 2

        cv2.putText(
            vista, tablero[indice],
            (cx - 18, cy + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4, (255, 0, 255), 3
        )

        if sugerencia == indice:
            cv2.circle(
                vista, (cx, cy), 50,
                (0, 255, 255), 4
            )

            cv2.putText(
                vista, "JUGAR X",
                (cx - 55, cy - 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 130, 255), 2
            )

    return vista


def imprimir_tablero(tablero):
    print("\nTABLERO DETECTADO:")

    for fila in range(3):
        print(" | ".join(
            tablero[fila * 3:fila * 3 + 3]
        ))


# ====================================
# PROGRAMA PRINCIPAL
# ====================================

cap = cv2.VideoCapture(CAMARA, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la camara")

historial = deque(maxlen=ESTABILIDAD)
ultimo_estado = None

print("\n=== DOBOT TRES EN RAYA ===")
print("ROBOT: X")
print("HUMANO: O")
print("Presiona Q para salir.")
print("Esta version NO mueve el robot.")

while True:
    ok, frame = cap.read()

    if not ok:
        break

    tablero, vista_yolo = reconocer_tablero(frame)

    historial.append(tuple(tablero))

    estable = (
        len(historial) == ESTABILIDAD
        and len(set(historial)) == 1
    )

    sugerencia = None

    if estable:
        estado = list(historial[-1])
        resultado = ganador(estado)
        turno = turno_actual(estado)

        # Solo proponer una jugada para
        # estados validos y sin ganador.
        valido = (
            turno != "INVALIDO"
            and not (
                resultado == "X"
                and estado.count("X") != estado.count("O") + 1
            )
            and not (
                resultado == "O"
                and estado.count("X") != estado.count("O")
            )
        )

        if valido and resultado is None and turno == ROBOT:
            _, sugerencia = minimax(
                estado.copy(), ROBOT
            )

        if tuple(estado) != ultimo_estado:
            imprimir_tablero(estado)

            if not valido:
                print("Estado invalido o deteccion incompleta.")
            elif resultado:
                print("RESULTADO:", resultado)
            elif turno == HUMANO:
                print("Turno del humano (O).")
            elif sugerencia is not None:
                print(
                    "ROBOT X DEBE JUGAR EN CASILLA:",
                    sugerencia + 1
                )

            ultimo_estado = tuple(estado)

    vista_tablero = dibujar_tablero(
        frame,
        tablero,
        sugerencia if estable else None
    )

    cv2.imshow("YOLO - DETECCIONES", vista_yolo)
    cv2.imshow("TABLERO + MINIMAX", vista_tablero)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
