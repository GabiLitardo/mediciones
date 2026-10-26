from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parent
FECHA_CORTE = date(2026, 9, 9)

for carpeta in BASE.iterdir():

    if not carpeta.is_dir():
        continue

    try:
        fecha = date.fromisoformat(carpeta.name)
    except ValueError:
        continue

    tanda = "tanda1" if fecha < FECHA_CORTE else "tanda2"

    for archivo in carpeta.rglob("*.ri"):

        if not all(x in archivo.name for x in [
            "_IV_VD=5V_postrad",
            "_FFC"
        ]) and not (
            "_IV_VD=5V_postrad" in archivo.name
            and any(f"_{d}_" in archivo.name for d in ["FFL", "FFS"])
        ):
            continue

        if archivo.stem.endswith(("_tanda1", "_tanda2")):
            continue

        nuevo = archivo.with_name(
            f"{archivo.stem}_{tanda}{archivo.suffix}"
        )

        if nuevo.exists():
            print(f"CONFLICTO: {nuevo}")
            continue

        print(f"{archivo.name} -> {nuevo.name}")
        archivo.rename(nuevo)