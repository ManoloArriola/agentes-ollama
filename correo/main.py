import json
from pathlib import Path
import ollama
import imaplib
import email
from datetime import date

ROOT = Path(__file__).parent
import sys
sys.path.append(str(ROOT.parent))
from agente_common import generate_with_acceleration

# 🔧 Configuración
def load_config():
    with open(ROOT / "config.json", encoding="utf-8") as f:
        return json.load(f)

def load_prioridad():
    path = ROOT / "prioridad.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {
        "dominios_prioritarios": [],
        "dominios_medios": [],
        "excepciones_prioritarias": [],
        "ignorar": []
    }

# 🧠 Resumir texto con Ollama
def resumir_correo(texto, modelo="llama3", use_openvino=False, options=None):
    messages = [
        {"role": "system", "content": "Eres un asistente que resume correos en español."},
        {"role": "user", "content": texto},
    ]
    return generate_with_acceleration(messages, model=modelo, use_openvino=use_openvino, options=options)

# 📬 Obtener correos vía IMAP
def obtener_correos(config, reglas, cantidad=20):
    mail = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
    mail.login(config["email"], config["password"])
    mail.select("inbox")

    status, data = mail.search(None, "UNSEEN")
    correo_ids = data[0].split()

    correos = []
    for cid in correo_ids[-cantidad:]:
        status, msg_data = mail.fetch(cid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        remitente = msg["From"] or ""
        asunto = msg["Subject"] or ""

        # Clasificación
        prioridad = None
        if any(rem in remitente for rem in reglas["ignorar"]):
            continue
        elif remitente in reglas["excepciones_prioritarias"]:
            prioridad = "prioritario"
        elif any(rem in remitente for rem in reglas["dominios_prioritarios"]):
            prioridad = "prioritario"
        elif any(rem in remitente for rem in reglas["dominios_medios"]):
            prioridad = "medio"
        else:
            continue  # ignorar normales

        cuerpo = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    cuerpo += part.get_payload(decode=True).decode(errors="ignore")
        else:
            cuerpo = msg.get_payload(decode=True).decode(errors="ignore")

        correos.append({"de": remitente, "asunto": asunto, "cuerpo": cuerpo, "prioridad": prioridad})

    return correos

# 🚀 Programa principal
def main():
    config = load_config()
    reglas = load_prioridad()
    print("Cargando agente correo...")

    correos = obtener_correos(config, reglas)

    # Separar por prioridad
    prioritarios = [c for c in correos if c["prioridad"] == "prioritario"]
    medios = [c for c in correos if c["prioridad"] == "medio"]

    archivo = ROOT / f"resumen_{date.today()}.txt"
    with open(archivo, "w", encoding="utf-8") as f:
        # Guardar primero los prioritarios
        f.write("=== 📌 CORREOS PRIORITARIOS ===\n")
        for i, correo in enumerate(prioritarios, 1):
            resumen = resumir_correo(
                correo["cuerpo"],
                modelo=config.get("ollama_model", "llama3"),
                use_openvino=config.get("use_openvino", False),
                options=config.get("ollama_options"),
            )
            salida = f"\n📩 Correo {i}: {correo['asunto']} (de {correo['de']})\nResumen: {resumen}\n"
            print(salida)
            f.write(salida)

        # Luego los medios
        f.write("\n=== 📂 CORREOS PRIORIDAD MEDIA ===\n")
        for i, correo in enumerate(medios, 1):
            resumen = resumir_correo(
                correo["cuerpo"],
                modelo=config.get("ollama_model", "llama3"),
                use_openvino=config.get("use_openvino", False),
                options=config.get("ollama_options"),
            )
            salida = f"\n📩 Correo {i}: {correo['asunto']} (de {correo['de']})\nResumen: {resumen}\n"
            print(salida)
            f.write(salida)

    print(f"\n✅ Resúmenes guardados en {archivo}")

if __name__ == "__main__":
    main()
