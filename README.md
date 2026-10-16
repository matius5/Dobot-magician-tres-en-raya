# Dobot Magician jugando tres en raya

**Robótica e IA · Corte 2 — Avance 2**  
**Docente:** Nazhir Amaya  
**Integrantes:** Mateo Peña, Daniel Ibáñez y José Valencia  
**Entrega:** 19 de noviembre de 2026

El proyecto busca que una persona juegue **O** y comience la partida, mientras el **Dobot Magician dibuja X** con un marcador borrable sobre un tablero de acrílico.

> **Avance actual:** el equipo ejecutó una demo sencilla con OpenCV y reporta que parece funcionar. Faltan fotografías y métricas. Aún no se ha tenido acceso al Dobot ni se ha entrenado YOLO.

📄 **[Consultar informe académico completo — seis apartados de la rúbrica](documentacion/ABPr_Avance_2.md)**

## 1. Propuesta

Una cámara USB fija observará el tablero. OpenCV y un detector YOLO11n entrenado interpretarán las casillas; Minimax elegirá la jugada y Python comunicará la trayectoria al Dobot mediante su API/SDK compatible.

La demo actual utiliza reglas geométricas con OpenCV. El entrenamiento YOLO, Minimax y la integración con el brazo siguen pendientes.

## 2. Montaje y posicionamiento

Se preparará un espacio de trabajo con el robot, el tablero y la cámara fijos. Se registrarán los nueve centros de casilla y las alturas de traslado y contacto del marcador. Se comprobarán centros y extremos de los trazos antes de dibujar.

[Consultar procedimiento propuesto de calibración](documentacion/calibracion.md). El profesor no exige PCB para este proyecto.

## 3. Organización

| Carpeta | Contenido |
|---|---|
| [documentacion/](documentacion/) | Informe, avances y calibración |
| [codigo/vision/](codigo/vision/) | Espacio para la demo y el detector |
| [codigo/inteligencia/](codigo/inteligencia/) | Espacio para Minimax |
| [codigo/robot/](codigo/robot/) | Espacio para conexión, movimientos y calibración |
| [entrenamiento/](entrenamiento/) | Preparación de datos, configuración y resultados |
| [modelos/](modelos/) | Registro de pesos entrenados cuando estén disponibles |
| [evidencias/](evidencias/) | Fotos, capturas y videos reales |

Las carpetas pendientes contienen instrucciones de incorporación; no representan módulos ya implementados. El código ejecutado por el equipo todavía debe incorporarse y ajustarse para que **O inicie**.

## 4. Próximas entregas

- [ ] Incorporar el código probado y ajustar la validación de turnos.
- [ ] Tomar fotografías del tablero y etiquetar X/O.
- [ ] Entrenar YOLO11n y demostrar inferencia en PC.
- [ ] Implementar y probar Minimax con la persona O y el robot X.
- [ ] Acceder al Dobot y demostrar comunicación desde Python.
- [ ] Calibrar posiciones y probar trazos.
- [ ] Registrar una partida completa.

Las dos demostraciones prioritarias son **modelo entrenado funcionando en PC** y **comunicación Python–Dobot**.

## 5. Documentación y evidencias

- [Informe académico](documentacion/ABPr_Avance_2.md)
- [Bitácora de avances](documentacion/avances.md)
- [Posicionamiento y calibración](documentacion/calibracion.md)
- [Guía de evidencias](evidencias/README.md)

Las imágenes técnicas serán elaboradas por el equipo y las evidencias corresponderán a pruebas reales. No se incluyen imágenes generadas con IA ni resultados de entrenamiento o movimiento sin verificar.
