**Proyecto:** Dobot Magician jugando tres en raya  
**Asignatura:** Robótica e IA  
**Docente:** Nazhir Amaya  
**Integrantes:** Mateo Peña, Daniel Ibáñez y José Valencia  
**Entrega:** 19 de noviembre de 2026 — Corte 2, Avance 2

## 1. Título y objetivos (0,5 puntos)

**Título:** Dobot Magician jugando tres en raya mediante visión por computador e inteligencia artificial.

**Objetivo general:** Desarrollar un sistema que permita al Dobot Magician jugar tres en raya contra una persona, reconociendo un tablero físico, seleccionando jugadas con Minimax y dibujando su símbolo con un marcador borrable.

**Objetivos específicos:**

1. Entrenar y evaluar YOLO11n para reconocer X y O y representar las nueve casillas del tablero.
2. Implementar Minimax y verificar las reglas para seleccionar jugadas legales a partir del estado reconocido.
3. Integrar Python con el Dobot Magician y calibrar las posiciones del tablero para ejecutar y comprobar los trazos del robot.

## 2. Planteamiento del problema (0,5 puntos)

Para jugar sobre un tablero físico, el robot debe reconocer símbolos, decidir una respuesta y ejecutarla en la casilla correcta. La iluminación, la perspectiva y las variaciones de trazos pueden afectar la lectura; los errores de calibración pueden desplazar el dibujo.

La propuesta mantiene el propósito inicial de una partida autónoma entre una persona y el Dobot. Una cámara USB fija observará el tablero; el computador interpretará las imágenes y elegirá la jugada; el brazo dibujará su respuesta.

**Pregunta orientadora:** ¿Cómo integrar percepción visual, decisión y control del Dobot Magician para reconocer un tablero físico y ejecutar jugadas válidas de tres en raya?

## 3. Estado del arte y marco teórico (0,5 puntos)

**Estado del arte:** OpenCV permite construir soluciones geométricas para símbolos bajo condiciones controladas. YOLO11 ofrece detección y entrenamiento con imágenes propias [1]; se selecciona YOLO11n como base para X/O. Minimax permite elegir movimientos mediante búsqueda adversaria [2]. El Dobot Magician dispone de documentación e interfaces para programar su operación [3]. El proyecto integrará estos enfoques, cuyo desempeño conjunto debe medirse. La comparación con proyectos académicos similares está pendiente de completar.

**Marco teórico:**

- **OpenCV:** captura imágenes y corrige la perspectiva del tablero.
- **YOLO11n:** detector que se entrenará con símbolos etiquetados; entrega clases y cajas delimitadoras.
- **Minimax:** explora jugadas y respuestas para elegir una acción óptima con reglas y estados correctos; no necesita entrenamiento neuronal.
- **Calibración:** relaciona casillas y posiciones físicas. Los píxeles no se envían directamente como coordenadas del robot.
- **API/SDK:** interfaz para comunicar Python con el Dobot; debe ser compatible con el modelo y firmware disponibles.

**Referencias:**

[1] Ultralytics. *YOLO11*. https://docs.ultralytics.com/models/yolo11/  
[2] Russell y Norvig. *Artificial Intelligence: A Modern Approach*, búsqueda adversaria. https://aima.cs.berkeley.edu/  
[3] Dobot. *Magician: documentación y descargas*. https://www.dobot-robots.com/products/education/magician.html  
[4] OpenCV. *Geometric Image Transformations*. https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html

## 4. Introducción y materiales (0,5 puntos)

El proyecto integra visión, inteligencia de juego y robótica. La persona dibujará O y comenzará; el Dobot responderá dibujando X. Después de cada jugada humana, el sistema interpretará el tablero, seleccionará una respuesta y dibujará el símbolo del robot.

El equipo ejecutó la demo geométrica con OpenCV y reporta que parece funcionar. La comprobación es preliminar, sin capturas aportadas ni métricas de precisión. Las siguientes etapas son entrenar YOLO, implementar Minimax y comprobar la comunicación y el movimiento del Dobot.

**Tabla 1. Materiales y herramientas previstos.**

| Elemento | Función |
|---|---|
| Dobot Magician, fuente y cable de comunicación compatibles | Ejecutar movimientos desde Python |
| Marcador borrable y soporte compatible | Dibujar símbolos |
| Cámara USB y soporte fijo | Observar el tablero |
| Tablero de acrílico, marcadores borrables y fijaciones | Superficie de juego estable |
| Computador con Python y VS Code | Desarrollo, inferencia y control |
| OpenCV, NumPy y Ultralytics | Procesamiento visual y entrenamiento |
| API/SDK y controladores del Dobot | Comunicación con el brazo |

## 5. Componente técnico (2,5 puntos)

**Arquitectura:** cámara USB → OpenCV y YOLO11n → matriz de casillas → Minimax → Python y API/SDK → Dobot con marcador borrable → verificación visual.

**Percepción:** fotografiar el tablero, etiquetar X/O y separar entrenamiento, validación y prueba por sesión. Entrenar YOLO11n, evaluar sus métricas y asignar cada detección a una casilla después de rectificar la imagen. La ausencia de detección no garantiza una casilla vacía; las lecturas ambiguas deben bloquear el movimiento.

**Decisión:** validar el turno y el estado; comprobar ganador o empate; ejecutar Minimax para elegir una casilla libre. La persona empieza con O y el Dobot responde con X. La validación se ajustará: antes de la respuesta del Dobot habrá una O más que X; después, ambas cantidades serán iguales.

**Control:** comprobar la conexión Python–Dobot, registrar centros de casilla y alturas de traslado y contacto. Probar primero movimientos sin contacto y después el dibujo, verificando el fin de cada orden. Retirar el brazo del campo visual para confirmar la jugada. La cámara y el tablero permanecerán fijos.

**Posicionamiento del Dobot — observación del docente:** se fijará la base sobre una mesa estable y se ubicará el tablero dentro de una zona alcanzable por el brazo con el marcador instalado. La cámara USB quedará fija sobre el tablero, procurando reducir los reflejos del acrílico. Las dimensiones y posiciones definitivas se comprobarán cuando se tenga acceso al robot.

Inicialmente se enseñarán y guardarán las coordenadas de los nueve centros de casilla mediante el software compatible con el Dobot. Se calibrarán por separado la altura de contacto y la de traslado. Se verificarán los centros y los extremos de los trazos mediante movimientos sin contacto. Cada casilla detectada se asociará a su posición guardada. Para dibujar X se realizarán dos diagonales, levantando el marcador entre ambas. Si se mueve el tablero o la base, deberá repetirse la calibración. Este procedimiento está propuesto, no ejecutado.

**Tabla 2. Avance y evidencias pendientes.**

| Componente | Lo disponible | Lo pendiente |
|---|---|---|
| OpenCV | Demo ejecutada por el equipo; parece funcionar | Capturas, mediciones y ajuste de reglas para que O inicie |
| Pruebas de software | 12 tableros sintéticos y tres casos de reglas comprobados en el paquete inicial | Evaluación con imágenes reales |
| YOLO11n | Base propuesta para el detector | Tomar fotografías, etiquetar, entrenar y evaluar |
| Minimax | Algoritmo seleccionado | Implementación y simulación |
| Python–Dobot | Arquitectura definida; aún sin acceso al robot | Acceso al equipo, conexión y video de movimiento |
| Partida física | Flujo propuesto | Calibración, dibujo e integración |

La demo actual no utiliza YOLO y no sustituye el modelo entrenado solicitado. Las pruebas sintéticas no demuestran precisión real ni funcionamiento físico. Las dos demostraciones prioritarias son el modelo entrenado funcionando en PC y la comunicación Python–Dobot.

**Ilustración 1. Arquitectura del sistema.** Pendiente: insertar diagrama propio del equipo.

**Ilustración 2. Montaje y calibración.** Pendiente: insertar esquema propio o fotografía real de cámara, tablero y Dobot.

**Ilustración 3. Resultados.** Pendiente: insertar capturas reales de inferencia y movimiento.

No se incluyen imágenes generadas con IA. Cada figura debe elaborarse o capturarse por el equipo y poder justificarse durante la sustentación.

**Tabla 3. Montaje físico requerido para este proyecto.**

| Elemento | Situación actual |
|---|---|
| Espacio de trabajo del Dobot | Requisito confirmado; preparación pendiente |
| Base del robot y tablero de acrílico fijos | Ubicación por comprobar al acceder al equipo |
| Cámara USB y soporte fijo | Configuración seleccionada; montaje pendiente |
| Marcador borrable ajustado al Dobot | Herramienta seleccionada; sujeción y contacto por calibrar |

Según la aclaración del equipo, el profesor no exige PCB para este proyecto, sino un espacio preparado para el trabajo del Dobot. No se trasladan los requisitos de fabricación electrónica de la rúbrica general.

## 6. Metodología, cronograma y dificultades (0,5 puntos)

**Metodología:** desarrollo incremental de percepción, comunicación, entrenamiento, juego, calibración e integración, con evidencia independiente por etapa.

**Tabla 4. Cronograma y verificación.**

| Periodo | Actividad | Estado documentado |
|---|---|---|
| Hasta el 15 de octubre | Arquitectura y demo OpenCV | Código, pruebas sintéticas y ejecución preliminar reportada |
| 16–20 de octubre | Montaje y conexión Python–Dobot | Pendiente |
| 21–27 de octubre | Dataset y Minimax | Pendiente |
| 28 de octubre–3 de noviembre | Entrenamiento y evaluación YOLO | Pendiente |
| 4–10 de noviembre | Calibración y dibujo | Pendiente |
| 11–17 de noviembre | Integración y partidas | Pendiente |
| 18 de noviembre | Revisión y evidencias | Pendiente |
| 19 de noviembre de 2026 | Entrega y sustentación | Programada |

**Cumplimiento:** el equipo ejecutó la visión sencilla y reporta funcionamiento preliminar. Falta tomar fotografías para entrenar y todavía no se ha tenido acceso al Dobot. La comunicación, el posicionamiento y la calibración están pendientes. El cronograma se ajustará a la disponibilidad del laboratorio.

**Dificultades encontradas:** falta de acceso al robot y de fotografías para el entrenamiento. La observación del docente se centra en cómo posicionar el Dobot; se atenderá mediante fijación del montaje, enseñanza de posiciones y comprobación del alcance. Queda por evaluar el efecto de los reflejos del acrílico, la sujeción del marcador y la oclusión de la cámara.

**Repositorio:** `matius5/Dobot-magician-tres-en-raya`, con carpetas de visión, inteligencia, control del robot, entrenamiento, modelos, documentación y evidencias. Solo se incorporarán resultados y archivos existentes.

**Presentación y evaluación:** utilizar una misma fuente y tamaño para títulos y párrafos; conservar la numeración de apartados, tablas e ilustraciones; revisar ortografía, pues cada error penaliza 0,1. El visor Markdown puede cambiar el tamaño de los encabezados: ajustar el estilo de la versión presentada. Todos los integrantes deben sustentar equitativamente; se evaluará la explicación grupal y el dominio individual.