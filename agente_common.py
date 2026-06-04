import logging
from typing import List, Dict, Any

try:
    import ollama
except Exception:
    ollama = None

try:
    from openvino import Core
except Exception:
    Core = None

try:
    from transformers import AutoTokenizer
except Exception:
    AutoTokenizer = None

try:
    import numpy as np
except Exception:
    np = None


def _openvino_infer(model_path: str, prompt: str, tokenizer_name: str, max_length: int = 256, device: str = "CPU") -> str:
    """Inferencia básica con OpenVINO para un modelo de texto convertido.

    Esta función requiere:
    - un modelo OpenVINO convertido compatible con el tokenizer usado.
    - un tokenizer de Hugging Face que coincida con el modelo.
    - la ruta `model_path` debe apuntar al archivo .xml o .onnx convertido.
    """
    if Core is None:
        raise RuntimeError("OpenVINO no está instalado en este entorno.")
    if AutoTokenizer is None:
        raise RuntimeError("Transformers no está instalado. Instálalo para usar OpenVINO.")
    if np is None:
        raise RuntimeError("NumPy no está instalado. Instálalo para usar OpenVINO.")

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    model = Core().read_model(model_path)
    compiled_model = Core().compile_model(model, device)
    infer_request = compiled_model.create_infer_request()

    inputs = tokenizer(prompt, return_tensors="np", truncation=True, padding="max_length", max_length=max_length)
    for name, tensor in inputs.items():
        if name not in compiled_model.inputs:
            continue
        infer_request.set_tensor(name, tensor)

    infer_request.infer()

    output_name = compiled_model.outputs[0].get_any_name()
    output = infer_request.get_tensor(output_name).data
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded


def generate_with_acceleration(messages: List[Dict[str, Any]], model: str = "llama3", use_openvino: bool = False, options: Dict[str, Any] | None = None, openvino_model_path: str | None = None, tokenizer_name: str | None = None, openvino_device: str = "CPU"):
    """Selecciona motor de inferencia y aplica aceleración si está disponible."""
    if use_openvino:
        if openvino_model_path and tokenizer_name:
            prompt = "\n".join([item["content"] for item in messages])
            return _openvino_infer(
                openvino_model_path,
                prompt,
                tokenizer_name,
                max_length=options.get("max_length", 256) if options else 256,
                device=openvino_device,
            )
        logging.warning("use_openvino está activado, pero faltan openvino_model_path o tokenizer_name en la configuración.")

    if ollama is None:
        raise RuntimeError("La librería 'ollama' no está disponible. Instálala y configura el entorno.")

    if options is None:
        options = {}

    respuesta = ollama.chat(model=model, messages=messages, options=options)
    return respuesta["message"]["content"]
