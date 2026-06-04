import json
from pathlib import Path
import pandas as pd
import ollama

ROOT = Path(__file__).parent
import sys
sys.path.append(str(ROOT.parent))
from agente_common import generate_with_acceleration


def load_config():
    config_path = ROOT / "config.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def leer_excel(ruta_excel):
    return pd.read_excel(ruta_excel)


def resumir_facturacion(df, modelo="llama3", options=None, openvino_model_path=None, openvino_tokenizer=None, openvino_device="CPU"):
    texto = df.head(20).to_string(index=False)
    messages = [
        {"role": "system", "content": "Eres un asistente experto en facturación y Excel. Extrae los datos clave y responde en español."},
        {"role": "user", "content": f"Resumen de la tabla de facturación:\n{texto}"},
    ]
    return generate_with_acceleration(
        messages,
        model=modelo,
        use_openvino=False,
        options=options,
        openvino_model_path=openvino_model_path,
        tokenizer_name=openvino_tokenizer,
        openvino_device=openvino_device,
    )


def main():
    config = load_config()
    excel_path = config.get("excel_path", "data/facturas.xlsx")

    print("Cargando agente facturación...")
    print(f"Leyendo archivo: {excel_path}")
    try:
        df = leer_excel(excel_path)
    except FileNotFoundError:
        print("No se encontró el archivo Excel. Coloca el archivo en la ruta indicada o actualiza config.json.")
        return

    resumen = resumir_facturacion(
        df,
        modelo=config.get("ollama_model", "llama3"),
        options=config.get("ollama_options"),
        openvino_model_path=config.get("openvino_model_path"),
        openvino_tokenizer=config.get("openvino_tokenizer"),
        openvino_device=config.get("openvino_device", "CPU"),
    )
    print("Resumen de facturación:")
    print(resumen)


if __name__ == "__main__":
    main()
