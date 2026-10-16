# Entrenamiento de YOLO11n

Pendiente tomar fotografías del tablero real y etiquetar símbolos.

1. Capturar variaciones de trazos, iluminación y estados del tablero.
2. Etiquetar clases: `0: X`, `1: O`.
3. Separar entrenamiento, validación y prueba por sesión, evitando imágenes casi idénticas en distintos conjuntos.
4. Crear `data.yaml` con rutas reales.
5. Entrenar y registrar configuración, versiones, métricas y pesos.
6. Evaluar en imágenes reservadas y con la cámara USB.

No existen datos, pesos propios ni resultados de entrenamiento incorporados todavía. Mantener las imágenes originales separadas de las evidencias de inferencia.
