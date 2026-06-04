import json
from pathlib import Path
import ollama
import imaplib
import email
from datetime import date
from bs4 import BeautifulSoup

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
def resumir_correo(texto, config, modelo="llama3"):
    if not texto.strip():
        return "⚠️ El correo no tiene contenido de texto para resumir."
    messages = [
        {"role": "system", "content": config.get("summary_prompt", "Eres un asistente que resume correos en español.")},
        {"role": "user", "content": texto},
    ]
    return generate_with_acceleration(
        messages,
        model=modelo,
        use_openvino=config.get("use_openvino", False),
        options=config.get("ollama_options"),
        openvino_model_path=config.get("openvino_model_path"),
        tokenizer_name=config.get("openvino_tokenizer"),
        openvino_device=config.get("openvino_device", "CPU"),
    )

# 📬 Obtener correos vía IMAP con prioridad
def obtener_correos(config, reglas, cantidad=20, filtro="ALL"):
    mail = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
    mail.login(config["email"], config["password"])
    mail.select("INBOX")

    status, data = mail.search(None, filtro)
    correo_ids = data[0].split()

    correos = []
    for cid in correo_ids[-cantidad:]:
        status, msg_data = mail.fetch(cid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        remitente = msg["From"] or ""
        asunto = msg["Subject"] or ""

        # Clasificación según reglas
        if any(rem in remitente for rem in reglas["ignorar"]):
            continue
        elif remitente in reglas["excepciones_prioritarias"]:
            prioridad = "prioritario"
        elif any(rem in remitente for rem in reglas["dominios_prioritarios"]):
            prioridad = "prioritario"
        elif any(rem in remitente for rem in reglas["dominios_medios"]):
            prioridad = "medio"
        else:
            prioridad = "normal"

        cuerpo = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    cuerpo += part.get_payload(decode=True).decode(errors="ignore")
                elif ctype == "text/html" and not cuerpo.strip():
                    html = part.get_payload(decode=True).decode(errors="ignore")
                    cuerpo = BeautifulSoup(html, "html.parser").get_text()
        else:
            cuerpo = msg.get_payload(decode=True).decode(errors="ignore")

        correos.append({"de": remitente, "asunto": asunto, "cuerpo": cuerpo, "prioridad": prioridad})

    return correos

# 🚀 Programa principal
def main():
    config = load_config()
    reglas = load_prioridad()
    print("Conectando a:", config["imap_server"], config["imap_port"])

    mail = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
    print("Login...")
    mail.login(config["email"], config["password"])
    print("Login OK")

    mail.select("INBOX")
    print("Carpeta seleccionada")
    print("Cargando agente correo...")

    correos = obtener_correos(config, reglas, filtro="ALL")

    # Separar por prioridad
    prioritarios = [c for c in correos if c["prioridad"] == "prioritario"]
    medios = [c for c in correos if c["prioridad"] == "medio"]
    normales = [c for c in correos if c["prioridad"] == "normal"]

    archivo = ROOT / f"resumen_{date.today()}.txt"
    with open(archivo, "w", encoding="utf-8") as f:
        # Guardar prioritarios
        f.write("=== 📌 CORREOS PRIORITARIOS ===\n")
        for i, correo in enumerate(prioritarios, 1):
            resumen = resumir_correo(correo["cuerpo"], config, modelo=config.get("ollama_model", "llama3"))
            salida = f"\n📩 Correo {i}: {correo['asunto']} (de {correo['de']})\nResumen: {resumen}\n"
            print(salida)
            f.write(salida)

        # Guardar medios
        f.write("\n=== 📂 CORREOS PRIORIDAD MEDIA ===\n")
        for i, correo in enumerate(medios, 1):
            resumen = resumir_correo(correo["cuerpo"], config, modelo=config.get("ollama_model", "llama3"))
            salida = f"\n📩 Correo {i}: {correo['asunto']} (de {correo['de']})\nResumen: {resumen}\n"
            print(salida)
            f.write(salida)

        # Guardar normales
        f.write("\n=== 📄 CORREOS NORMALES ===\n")
        for i, correo in enumerate(normales, 1):
            resumen = resumir_correo(correo["cuerpo"], config, modelo=config.get("ollama_model", "llama3"))
            salida = f"\n📩 Correo {i}: {correo['asunto']} (de {correo['de']})\nResumen: {resumen}\n"
            print(salida)
            f.write(salida)

        # Resumen global
        f.write("\n=== 📊 RESUMEN GLOBAL ===\n")
        f.write(f"Total de correos procesados: {len(correos)}\n")
        f.write(f"- Prioritarios: {len(prioritarios)}\n")
        f.write(f"- Medios: {len(medios)}\n")
        f.write(f"- Normales: {len(normales)}\n")

    print(f"\n✅ Resúmenes guardados en {archivo}")

if __name__ == "__main__":
    main()
