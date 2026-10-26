from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parent
FECHA_CORTE = date(2026, 9, 9)

DISPOS = ["FFC1", "FFC2", "FFC3", "FFL", "FFS"]

for carpeta in BASE.iterdir():

    if not carpeta.is_dir():
        continue

    try:
        fecha = date.fromisoformat(carpeta.name)
    except ValueError:
        continue

    # Solo procesamos la tanda 1
    if fecha >= FECHA_CORTE:
        continue

    for archivo in carpeta.rglob("*.ri"):

        if "_IV_VD=5V_postrad" not in archivo.name:
            continue

        if not any(f"_{disp}_" in archivo.name for disp in DISPOS):
            continue

        if archivo.stem.endswith(("_tanda1", "_tanda2")):
            continue

        nuevo = archivo.with_name(
            f"{archivo.stem}_tanda1{archivo.suffix}"
        )

        if nuevo.exists():
            print(f"CONFLICTO: {nuevo}")
            continue

        print(f"{archivo.name} -> {nuevo.name}")

        archivo.rename(nuevo)