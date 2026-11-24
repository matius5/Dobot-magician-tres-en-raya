
import cv2
from pathlib import Path
from ultralytics import YOLO

RUTA = Path("modelos/hf_tictactoe/weights/best.onnx")

if not RUTA.exists():
    raise FileNotFoundError(f"No existe: {RUTA}")

modelo = YOLO(str(RUTA), task="detect")

print("=== MODELO YOLO CARGADO ===")
print("Clases:", modelo.names)
print("Presiona Q para salir.")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la camara 0")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    resultados = modelo.predict(
        frame,
        conf=0.35,
        imgsz=640,
        device="cpu",
        verbose=False
    )

    imagen = resultados[0].plot()

    cv2.imshow("DOBOT - YOLO X O", imagen)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
