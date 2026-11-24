"""Control del DOBOT Magician para tres en raya.

Usa pydobot y las coordenadas confirmadas en calibracion_dobot.json.
No reintenta movimientos cuando falla la comunicacion: la orden podria
haberse ejecutado aunque se haya perdido la respuesta del controlador.
"""

import json
import math
from pathlib import Path

import numpy as np
import pydobot


class ControlDobot:
    def __init__(self, archivo="calibracion_dobot.json"):
        ruta = Path(archivo)
        with ruta.open("r", encoding="utf-8") as f:
            self.cfg = json.load(f)

        self.casillas = {
            int(numero): np.array(valores, dtype=float)
            for numero, valores in self.cfg["casillas"].items()
        }
        if set(self.casillas) != set(range(1, 10)):
            raise ValueError("Se necesitan las coordenadas de las 9 casillas")
        if any(len(valores) != 4 or not np.isfinite(valores).all()
               for valores in self.casillas.values()):
            raise ValueError("Cada casilla debe tener X, Y, Z y R validos")

        self.robot = None
        self.velocidad_actual = None
        self.movimiento_incierto = False
        self.tamano = float(self.cfg["tamano_x_mm"])
        self.z_libre = (
            max(pos[2] for pos in self.casillas.values())
            + float(self.cfg["altura_seguridad_mm"])
        )
        self.vel_libre = 80
        self.vel_dibujo = 50

        self.h = self.casillas[3][:2] - self.casillas[1][:2]
        self.v = self.casillas[7][:2] - self.casillas[1][:2]
        if np.linalg.norm(self.h) == 0 or np.linalg.norm(self.v) == 0:
            raise ValueError("Las referencias del tablero son invalidas")
        self.h /= np.linalg.norm(self.h)
        self.v /= np.linalg.norm(self.v)

    def conectar(self):
        if self.movimiento_incierto:
            raise RuntimeError("Movimiento anterior sin confirmar; revisar robot")
        if self.robot is None:
            self.robot = pydobot.Dobot(
                port=self.cfg["puerto"], verbose=False
            )
            self.velocidad_actual = None
        return self.robot

    def cerrar(self):
        if self.robot is not None:
            try:
                self.robot.close()
            finally:
                self.robot = None
                self.velocidad_actual = None

    def mover(self, x, y, z, r, velocidad):
        if self.robot is None:
            raise RuntimeError("DOBOT no conectado")
        if self.movimiento_incierto:
            raise RuntimeError("Movimiento sin confirmar: no se enviaran mas ordenes")

        valores = (float(x), float(y), float(z), float(r))
        if not all(math.isfinite(valor) for valor in valores):
            raise ValueError("Coordenada no valida")

        print(
            f"MOVIMIENTO -> X={valores[0]:.2f}, Y={valores[1]:.2f}, "
            f"Z={valores[2]:.2f}, R={valores[3]:.2f}, VEL={velocidad}",
            flush=True,
        )

        try:
            if self.velocidad_actual != velocidad:
                self.robot.speed(velocidad, velocidad)
                self.velocidad_actual = velocidad
            # Un comando por movimiento. No se reenvia ante fallo.
            self.robot.move_to(*valores, wait=True)
        except Exception as exc:
            self.movimiento_incierto = True
            print("\nFALLO: movimiento sin confirmacion del DOBOT.", flush=True)
            print(f"Ultima orden: {valores}, velocidad={velocidad}", flush=True)
            print(
                "NO repetir automaticamente. El movimiento pudo ejecutarse "
                "aunque no llegara la respuesta. Revisar fisicamente el robot "
                "y el tablero antes de continuar.",
                flush=True,
            )
            raise RuntimeError(
                "Comunicacion/movimiento sin confirmar: juego detenido"
            ) from exc

    def elevar(self):
        if self.robot is None:
            raise RuntimeError("DOBOT no conectado")
        if self.movimiento_incierto:
            raise RuntimeError("Movimiento anterior sin confirmar")
        try:
            x, y, z, r, *_ = self.robot.pose()
        except Exception as exc:
            self.movimiento_incierto = True
            raise RuntimeError("No fue posible leer la posicion del DOBOT") from exc
        if z < self.z_libre:
            self.mover(x, y, self.z_libre, r, self.vel_libre)

    def mover_libre(self, x, y, r):
        self.elevar()
        self.mover(x, y, self.z_libre, r, self.vel_libre)

    def puntos_x(self, numero):
        if numero not in self.casillas:
            raise ValueError(f"Casilla invalida: {numero}")
        centro = self.casillas[numero][:2]
        mitad = self.tamano / 2.0
        a = centro - self.h * mitad - self.v * mitad
        b = centro + self.h * mitad + self.v * mitad
        c = centro + self.h * mitad - self.v * mitad
        d = centro - self.h * mitad + self.v * mitad
        return a, b, c, d

    def trazo(self, inicio, fin, z, r):
        self.mover_libre(inicio[0], inicio[1], r)
        self.mover(inicio[0], inicio[1], z, r, self.vel_dibujo)
        # Una unica orden lineal por diagonal, sin 6 segmentos.
        self.mover(fin[0], fin[1], z, r, self.vel_dibujo)
        self.mover(fin[0], fin[1], self.z_libre, r, self.vel_libre)

    def dibujar_x(self, numero):
        if numero not in self.casillas:
            raise ValueError(f"Casilla invalida: {numero}")
        if self.robot is None:
            raise RuntimeError("DOBOT no conectado")
        if self.movimiento_incierto:
            raise RuntimeError("DOBOT requiere revision antes de continuar")

        x, y, z, r = self.casillas[numero]
        a, b, c, d = self.puntos_x(numero)
        print(f"\nDOBOT: dibujando X en casilla {numero}", flush=True)

        # Las dos diagonales usan la Z del JSON de la casilla.
        # Se elimina la antigua correccion especial para la casilla 4.
        self.trazo(a, b, z, r)
        self.trazo(c, d, z, r)

        self.mover_libre(x, y, r)
        print("X dibujada correctamente", flush=True)

    def reposo(self):
        if not self.cfg.get("reposo_validado", False):
            raise RuntimeError("Posicion y trayectoria de reposo no validadas")
        if self.robot is None:
            raise RuntimeError("DOBOT no conectado")
        if self.movimiento_incierto:
            raise RuntimeError("No ir a reposo: movimiento sin confirmar")

        xr, yr, zr, rr = map(float, self.cfg["pos_reposo"])
        try:
            x, y, z, r, *_ = self.robot.pose()
        except Exception as exc:
            self.movimiento_incierto = True
            raise RuntimeError("No se pudo leer la posicion para reposo") from exc
        altura_traslado = max(z, self.z_libre, zr)
        if z < altura_traslado:
            self.mover(x, y, altura_traslado, r, self.vel_libre)
        self.mover(xr, yr, altura_traslado, rr, self.vel_libre)
        if abs(zr - altura_traslado) > 0.1:
            self.mover(xr, yr, zr, rr, self.vel_libre)
        print("DOBOT en reposo", flush=True)
