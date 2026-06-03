import json
import os
import shutil
from pathlib import Path
import ollama

ROOT = Path(__file__).parent


def load_config():
    config_path = ROOT / "config.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def organizar_archivos(origen, destino):
    tipos = {
        ".txt": "documentos",
        ".pdf": "documentos",
        ".xlsx": "excel",
        ".xls": "excel",
        ".jpg": "imagenes",
        ".jpeg": "imagenes",
        ".png": "imagenes",
        ".mp3": "audio",
        ".mp4": "video",
    }

    for archivo in os.listdir(origen):
        ruta_archivo = Path(origen) / archivo
        if not ruta_archivo.is_file():
            continue

        ext = ruta_archivo.suffix.lower()
        categoria = tipos.get(ext, "otros")
        carpeta_destino = Path(destino) / categoria
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ruta_archivo), carpeta_destino / archivo)
        print(f"Movido {archivo} -> {categoria}")


def main():
    config = load_config()
    watch_folder = config.get("watch_folder")
    archive_folder = config.get("archive_folder")

    print("Cargando agente archivos...")
    print(f"Organizando archivos de {watch_folder}")

    if not watch_folder or not archive_folder:
        print("Actualiza config.json con watch_folder y archive_folder.")
        return

    if not Path(watch_folder).exists():
        print(f"La carpeta de origen no existe: {watch_folder}")
        return

    Path(archive_folder).mkdir(parents=True, exist_ok=True)
    organizar_archivos(watch_folder, archive_folder)


if __name__ == "__main__":
    main()
