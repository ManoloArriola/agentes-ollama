import logging
from typing import List, Dict, Any

try:
    import ollama
except Exception:
    ollama = None


def generate_with_acceleration(messages: List[Dict[str, Any]], model: str = "llama3", use_openvino: bool = False, options: Dict[str, Any] | None = None):
    """Wrapper que selecciona motor de inferencia: Ollama por defecto.

    Si `use_openvino` es True e `openvino.runtime` está disponible, intenta usarlo
    como acelerador (actualmente actúa como un placeholder que cae de vuelta a Ollama).
    """
    if use_openvino:
        try:
            from openvino.runtime import Core
            logging.info("OpenVINO detectado: se podría acelerar aquí la tarea.")
        except Exception:
            logging.info("OpenVINO no disponible: se usará Ollama como fallback.")

    if ollama is None:
        raise RuntimeError("La librería 'ollama' no está disponible. Instálala y configura el entorno.")

    if options is None:
        options = {}

    respuesta = ollama.chat(model=model, messages=messages, options=options)
    return respuesta["message"]["content"]
