# Posicionamiento y calibración del Dobot

**Estado:** procedimiento propuesto; todavía no se ha tenido acceso al robot.

## 1. Montaje

Fijar la base en una mesa estable. Ubicar el tablero de acrílico donde el Dobot pueda alcanzar las nueve casillas y todos los extremos de los trazos con el marcador instalado. Fijar la cámara USB sobre el tablero y reducir reflejos. Las dimensiones definitivas se determinarán en el laboratorio.

## 2. Referencias

Identificar el software, firmware y API/SDK compatibles. Establecer las referencias del robot según el manual del equipo. Registrar los nueve centros de casilla, la orientación de la cuadrícula y las alturas de contacto y traslado. Verificar la posición de la punta con el marcador realmente instalado.

## 3. Comprobación

Realizar recorridos sin contacto, comprobando centros y extremos de cada diagonal. Después ensayar trazos en una superficie de prueba. Dibujar X con dos diagonales y levantar el marcador entre ellas. Registrar la desviación de posición y ajustar.

## 4. Relación con visión

Asociar cada fila/columna detectada con su posición guardada. La rectificación visual de cuatro esquinas no sustituye esta calibración física. Retirar el brazo del campo visual antes de leer el tablero. Recalibrar si se mueve el tablero, la base, la cámara o cambia la geometría de la herramienta.

## 5. Registro pendiente

| Casilla | Fila | Columna | X robot | Y robot | Z contacto | Z traslado |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | | | | |
| 2 | 0 | 1 | | | | |
| 3 | 0 | 2 | | | | |
| 4 | 1 | 0 | | | | |
| 5 | 1 | 1 | | | | |
| 6 | 1 | 2 | | | | |
| 7 | 2 | 0 | | | | |
| 8 | 2 | 1 | | | | |
| 9 | 2 | 2 | | | | |

Completar unidades y convenciones conforme al SDK utilizado. Las casillas vacías de esta tabla no son coordenadas ejecutables.
