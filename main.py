"""Tres en raya con YOLO + Minimax + DOBOT Magician.
Requiere dobot_control.py, calibracion_vision.json y calibracion_dobot.json.
Por seguridad, solicita confirmación manual antes de cada movimiento real.
"""
import json
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from dobot_control import ControlDobot

# Mantener True para probar primero sin mover el DOBOT.
SIMULACION = False
MODELO = "modelos/hf_tictactoe/weights/best.onnx"
CONFIANZA = 0.48
SEGUNDOS_ESTABLES = 1.7
SEGUNDOS_SIN_MOVIMIENTO = 1.3
UMBRAL_CAMBIO = 20
FRACCION_CAMBIO = 0.018
X, O, VACIO = "X", "O", "."
LINEAS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
ORDEN = [4,0,2,6,8,1,3,5,7]


def resultado(tablero):
    for a, b, c in LINEAS:
        if tablero[a] != VACIO and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a]
    return "EMPATE" if VACIO not in tablero else None


def minimax(tablero, jugador, profundidad=0, alfa=-1000, beta=1000):
    fin = resultado(tablero)
    if fin == X:
        return 10 - profundidad, None
    if fin == O:
        return profundidad - 10, None
    if fin == "EMPATE":
        return 0, None
    mejor = None
    if jugador == X:
        valor = -1000
        for i in ORDEN:
            if tablero[i] != VACIO:
                continue
            tablero[i] = X
            puntuacion, _ = minimax(tablero, O, profundidad + 1, alfa, beta)
            tablero[i] = VACIO
            if puntuacion > valor:
                valor, mejor = puntuacion, i
            alfa = max(alfa, valor)
            if alfa >= beta:
                break
        return valor, mejor
    valor = 1000
    for i in ORDEN:
        if tablero[i] != VACIO:
            continue
        tablero[i] = O
        puntuacion, _ = minimax(tablero, X, profundidad + 1, alfa, beta)
        tablero[i] = VACIO
        if puntuacion < valor:
            valor, mejor = puntuacion, i
        beta = min(beta, valor)
        if alfa >= beta:
            break
    return valor, mejor


def tablero_texto(celdas):
    return " / ".join(" ".join(celdas[i:i+3]) for i in (0,3,6))


def compatible(observado, confirmado):
    # Una X/O ya confirmada puede desaparecer de la detección,
    # pero NO puede cambiar de símbolo.
    return all(
        real == VACIO or visto in (VACIO, real)
        for visto, real in zip(observado, confirmado)
    )


def nuevos(observado, confirmado):
    return [(i, observado[i]) for i in range(9)
            if confirmado[i] == VACIO and observado[i] != VACIO]


class Vision:
    def __init__(self):
        with open("calibracion_vision.json", encoding="utf-8") as archivo:
            cfg = json.load(archivo)
        self.camara = cfg["camara"]
        self.lado = int(cfg["tamano"])
        src = np.float32(cfg["puntos"])
        n = self.lado - 1
        dst = np.float32([[0,0],[n,0],[n,n],[0,n]])
        self.matriz = cv2.getPerspectiveTransform(src, dst)
        self.modelo = YOLO(MODELO, task="detect")
        self.anterior = None
        self.ultima_actividad = time.monotonic()

    def procesar(self, imagen):
        recortada = cv2.warpPerspective(imagen, self.matriz, (self.lado, self.lado))
        gris = cv2.GaussianBlur(cv2.cvtColor(recortada, cv2.COLOR_BGR2GRAY), (9,9), 0)
        ahora = time.monotonic()
        if self.anterior is not None:
            delta = cv2.absdiff(gris, self.anterior)
            fraccion = float(np.mean(delta > UMBRAL_CAMBIO))
            if fraccion > FRACCION_CAMBIO:
                self.ultima_actividad = ahora
        self.anterior = gris

        detecciones = self.modelo.predict(
            imagen, conf=CONFIANZA, imgsz=640, device="cpu", verbose=False
        )[0]
        estado = [VACIO] * 9
        confianza = [0.0] * 9
        margen = 0.18  # Se rechazan detecciones pegadas a las líneas de la cuadrícula.
        for caja in detecciones.boxes:
            etiqueta = detecciones.names[int(caja.cls[0])]
            if etiqueta not in (X, O):
                continue
            x1, y1, x2, y2 = caja.xyxy[0].tolist()
            pixel = np.float32([[[(x1+x2)/2, (y1+y2)/2]]])
            xx, yy = cv2.perspectiveTransform(pixel, self.matriz)[0,0]
            if not (0 <= xx < self.lado and 0 <= yy < self.lado):
                continue
            fx, fy = xx / self.lado * 3, yy / self.lado * 3
            col, fila = int(fx), int(fy)
            if not (margen <= fx-col <= 1-margen and margen <= fy-fila <= 1-margen):
                continue
            i = fila*3 + col
            confianza_actual = float(caja.conf[0])
            if confianza_actual > confianza[i]:
                estado[i] = etiqueta
                confianza[i] = confianza_actual
        return recortada, estado, ahora - self.ultima_actividad


def dibujar_pantalla(imagen, confirmado, observado, fase, pendiente):
    vista = imagen.copy()
    lado = vista.shape[0]
    paso = lado // 3
    for i in (1,2):
        cv2.line(vista, (i*paso,0), (i*paso,lado), (0,255,0), 2)
        cv2.line(vista, (0,i*paso), (lado,i*paso), (0,255,0), 2)
    for i in range(9):
        fila, col = divmod(i, 3)
        cx, cy = col*paso + paso//2, fila*paso + paso//2
        simbolo = confirmado[i] if confirmado[i] != VACIO else observado[i]
        color = (255,0,255) if confirmado[i] != VACIO else (0,165,255)
        cv2.putText(vista, simbolo, (cx-13, cy+16), cv2.FONT_HERSHEY_SIMPLEX, 1.35, color, 3)
        if i == pendiente:
            cv2.circle(vista, (cx,cy), 48, (0,255,255), 3)
    cv2.rectangle(vista, (0,0), (lado,36), (25,25,25), -1)
    cv2.putText(vista, fase[:42], (10,25), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,255,255), 2)
    return vista


def iniciar():
    if not Path(MODELO).exists():
        raise FileNotFoundError(MODELO)
    vision = Vision()
    camara = cv2.VideoCapture(vision.camara, cv2.CAP_DSHOW)
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not camara.isOpened():
        raise RuntimeError("No se pudo abrir la camara")
    confirmado = [VACIO] * 9
    fase = "ESPERAR_TABLERO_VACIO"
    pendiente = None
    candidato = None
    desde = 0.0
    robot = None
    pausa = False

    print("\n=== TRES EN RAYA: DOBOT X / PERSONA O ===")
    print("Modo:", "SIMULACION" if SIMULACION else "ROBOT REAL")
    print("Teclas: Q=salir, P=pausa, R=reiniciar tablero limpio, M=autorizar jugada real")
    print("V=confirmar manualmente una X ya dibujada (solo si se ve fisicamente)")

    try:
        if not SIMULACION:
            with open("calibracion_dobot.json", encoding="utf-8") as f:
                config = json.load(f)
            if not config.get("reposo_validado", False):
                raise RuntimeError("Primero valida la ruta de reposo")
            robot = ControlDobot()
            robot.conectar()
            # Llevar al reposo solo cuando la ruta ya fue comprobada.
            robot.reposo()

        while True:
            ok, imagen = camara.read()
            if not ok:
                print("Se interrumpio la camara")
                break
            recortada, observado, quieto = vision.procesar(imagen)
            actual = time.monotonic()
            firma = tuple(observado)
            if firma != candidato:
                candidato, desde = firma, actual
            lectura_estable = (
                actual - desde >= SEGUNDOS_ESTABLES
                and quieto >= SEGUNDOS_SIN_MOVIMIENTO
            )

            if not pausa and lectura_estable:
                if fase == "ESPERAR_TABLERO_VACIO":
                    if observado == [VACIO]*9:
                        confirmado = [VACIO]*9
                        fase = "TURNO_ROBOT"
                        print("Tablero vacio confirmado")
                elif fase == "TURNO_ROBOT":
                    if resultado(confirmado) is not None:
                        fase = "FIN"
                    elif compatible(observado, confirmado) and not nuevos(observado, confirmado):
                        _, indice = minimax(confirmado.copy(), X)
                        if indice is not None:
                            pendiente = indice
                            print("Robot propone casilla", indice+1)
                            fase = "AUTORIZAR_MOVIMIENTO" if not SIMULACION else "VERIFICAR_X"
                            if SIMULACION:
                                print("SIMULACION: dibuja manualmente X en", indice+1)
                    # Cualquier deteccion extraña se ignora, no provoca ERROR permanente.
                elif fase == "VERIFICAR_X":
                    if (pendiente is not None and compatible(observado, confirmado)
                            and observado[pendiente] == X
                            and all(i == pendiente or simbolo == VACIO for i, simbolo in nuevos(observado, confirmado))):
                        confirmado[pendiente] = X
                        print("X verificada en", pendiente+1, tablero_texto(confirmado))
                        pendiente = None
                        fase = "FIN" if resultado(confirmado) else "TURNO_HUMANO"
                        if fase == "TURNO_HUMANO":
                            print("Esperando O; retira completamente tu mano")
                elif fase == "TURNO_HUMANO":
                    if compatible(observado, confirmado):
                        detectadas = nuevos(observado, confirmado)
                        if len(detectadas) == 1 and detectadas[0][1] == O:
                            casilla, _ = detectadas[0]
                            confirmado[casilla] = O
                            print("O confirmada en", casilla+1, tablero_texto(confirmado))
                            if resultado(confirmado):
                                fase = "FIN"
                            else:
                                fase = "TURNO_ROBOT"
                elif fase == "FIN":
                    pass

            if fase == "FIN":
                mensaje = f"FIN: {resultado(confirmado)} (R reinicia)"
            elif pausa:
                mensaje = "PAUSA (P reanuda)"
            elif fase == "AUTORIZAR_MOVIMIENTO":
                mensaje = f"RETIRA MANOS / M autoriza X en {pendiente+1}"
            elif fase == "VERIFICAR_X":
                mensaje = f"Esperando verificar X en {pendiente+1}"
            else:
                mensaje = fase
            cv2.imshow("DOBOT - TRES EN RAYA", dibujar_pantalla(recortada, confirmado, observado, mensaje, pendiente))
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q'):
                break
            if tecla == ord('p'):
                pausa = not pausa
                candidato = None
                print("PAUSADO" if pausa else "REANUDADO")
            if tecla == ord('r'):
                # No borra fichas fisicas: espera confirmacion visual de tablero limpio.
                confirmado = [VACIO]*9
                pendiente = None
                fase = "ESPERAR_TABLERO_VACIO"
                candidato = None
                pausa = False
                print("Limpia el tablero para reiniciar")
            if tecla == ord('v') and fase == "VERIFICAR_X" and pendiente is not None:
                print("CONFIRMACION MANUAL: X fisicamente comprobada en", pendiente+1)
                confirmado[pendiente] = X
                pendiente = None
                fase = "FIN" if resultado(confirmado) else "TURNO_HUMANO"
            if tecla == ord('m') and fase == "AUTORIZAR_MOVIMIENTO" and not pausa:
                # Autorizacion humana es obligatoria: NO hay detector de manos fiable.
                if quieto < SEGUNDOS_SIN_MOVIMIENTO or not compatible(observado, confirmado) or nuevos(observado, confirmado):
                    print("No se autoriza: imagen en movimiento o detecciones inesperadas")
                    continue
                if pendiente is None or confirmado[pendiente] != VACIO:
                    print("No se autoriza: casilla no disponible")
                    continue
                print("Movimiento autorizado: casilla", pendiente+1)
                try:
                    # La camara no se evalua durante el movimiento del brazo.
                    robot.dibujar_x(pendiente+1)
                    robot.reposo()
                    fase = "VERIFICAR_X"
                    candidato = None
                    vision.anterior = None
                    vision.ultima_actividad = time.monotonic()
                    print("Movimiento terminado; verificando X")
                except Exception:
                    fase = "FALLO_MOVIMIENTO"
                    print("FALLO: detener juego, revisar DOBOT y su posicion. NO reintentar automaticamente.")
                    raise
    finally:
        camara.release()
        cv2.destroyAllWindows()
        if robot is not None:
            robot.cerrar()


if __name__ == "__main__":
    iniciar()
