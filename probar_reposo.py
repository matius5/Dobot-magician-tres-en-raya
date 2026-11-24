
import json
import pydobot
import traceback

with open("calibracion_dobot.json", encoding="utf-8") as f:
    cfg = json.load(f)

destino = cfg["pos_reposo"]

z_libre = max(
    c[2] for c in cfg["casillas"].values()
) + cfg["altura_seguridad_mm"]

robot = None

print("=== PRUEBA DE REPOSO ===")
print("Destino:", destino)
print("Altura libre:", z_libre)

respuesta = input(
    "Escribe REPOSO para autorizar: "
).strip()

if respuesta != "REPOSO":
    raise SystemExit("Cancelado")

try:
    robot = pydobot.Dobot(
        port=cfg["puerto"],
        verbose=False
    )

    robot.speed(25, 25)

    x, y, z, r, *_ = robot.pose()

    # Elevar a una altura de traslado segura
    z_traslado = max(z, z_libre, destino[2])

    if z < z_traslado:
        robot.move_to(
            x, y, z_traslado, r,
            wait=True
        )

    # Desplazar hacia reposo
    robot.move_to(
        destino[0],
        destino[1],
        z_traslado,
        destino[3],
        wait=True
    )

    # Ajustar altura final
    robot.move_to(
        destino[0],
        destino[1],
        destino[2],
        destino[3],
        wait=True
    )

    print("\nPOSICION FINAL:")
    print(robot.pose()[:4])

    print("\nComprueba que el robot:")
    print("- Este fuera del campo de vision.")
    print("- No haya tocado ningun obstaculo.")
    print("- Haya completado el movimiento suavemente.")

except Exception:
    traceback.print_exc()

finally:
    if robot is not None:
        robot.close()
        print("Conexion cerrada.")
