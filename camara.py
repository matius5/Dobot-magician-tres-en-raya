
import cv2
from pathlib import Path

# Configuracion
ANCHO = 640
ALTO = 480
CARPETA = Path("datos") / "capturas"
CARPETA.mkdir(parents=True, exist_ok=True)


def buscar_camaras():
    disponibles = []

    print("\n=== BUSCANDO CAMARAS ===")

    for indice in range(5):
        cap = cv2.VideoCapture(indice, cv2.CAP_DSHOW)

        if cap.isOpened():
            ok, frame = cap.read()

            if ok and frame is not None:
                h, w = frame.shape[:2]
                print(f"Camara {indice}: FUNCIONA ({w}x{h})")
                disponibles.append(indice)

        cap.release()

    return disponibles


def iniciar_camara(indice):
    cap = cv2.VideoCapture(indice, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("ERROR: No se pudo abrir la camara.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)

    print("\n=== CAMARA ACTIVADA ===")
    print("Presiona S para guardar una imagen.")
    print("Presiona Q para salir.")

    contador = 0

    while True:
        ok, frame = cap.read()

        if not ok:
            print("No se pudo obtener la imagen.")
            break

        cv2.putText(
            frame,
            f"CAMARA {indice} - DOBOT 3 EN RAYA",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )

        cv2.imshow("DOBOT - VISION EN TIEMPO REAL", frame)

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("s"):
            contador += 1
            ruta = CARPETA / f"camara_{indice}_{contador}.jpg"
            cv2.imwrite(str(ruta), frame)
            print(f"Imagen guardada: {ruta}")

        elif tecla == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    camaras = buscar_camaras()

    if not camaras:
        print("ERROR: No se encontraron camaras funcionales.")
    else:
        print(f"\nCamaras disponibles: {camaras}")

        while True:
            try:
                indice = int(input("Selecciona el indice de la camara: "))
                if indice in camaras:
                    break
                print("Selecciona uno de los indices disponibles.")
            except ValueError:
                print("Introduce un numero valido.")

        iniciar_camara(indice)
