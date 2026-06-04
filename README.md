# 🚀 Integración de Ollama + OpenVINO para Agentes Locales

## 📌 Función central de inferencia

```python
import logging
from typing import List, Dict, Any

try:
    import ollama
except Exception:
    ollama = None


def generate_with_acceleration(
    messages: List[Dict[str, Any]],
    model: str = "llama3",
    use_openvino: bool = False,
    options: Dict[str, Any] | None = None
):
    """
    Wrapper que selecciona el motor de inferencia.

    - Usa Ollama por defecto.
    - Si `use_openvino=True` y OpenVINO está disponible,
      intenta utilizar OpenVINO como acelerador.
    - Actualmente OpenVINO funciona como placeholder y hace fallback a Ollama.
    """

    if use_openvino:
        try:
            from openvino.runtime import Core
            logging.info(
                "OpenVINO detectado: se podría acelerar aquí la tarea."
            )
        except Exception:
            logging.info(
                "OpenVINO no disponible: se usará Ollama como fallback."
            )

    if ollama is None:
        raise RuntimeError(
            "La librería 'ollama' no está disponible. "
            "Instálala y configura el entorno."
        )

    if options is None:
        options = {}

    respuesta = ollama.chat(
        model=model,
        messages=messages,
        options=options
    )

    return respuesta["message"]["content"]
```

---

# ▶️ Ejecución básica

## Activar el entorno virtual (Windows)

```powershell
.\venv\Scripts\Activate.ps1
```

## Ejecutar el agente

```powershell
python main.py
```

---

# ⚠️ Notas importantes

## Si PowerShell bloquea la activación

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Configuración inicial

- El archivo `config.json` contiene valores de ejemplo.
- Sustituye dichos valores por:
  - Credenciales reales
  - Rutas reales
  - Nombres de recursos reales

## Modelfile

El archivo `Modelfile` define:

- El rol del agente
- El comportamiento base del modelo en Ollama

---

# 🤖 Crear modelos locales en Ollama

```powershell
ollama create agente_correo
ollama create agente_facturacion
ollama create agente_archivos
```

---

# ⚡ Configuración rápida y aceleración

## Crear entornos e instalar dependencias

```powershell
.\scripts\setup_envs.ps1
```

## Ejecutar un agente

```powershell
.\scripts\run_agent.ps1 -agent correo
```

## Soporte OpenVINO

Si OpenVINO está instalado:

- Los agentes intentarán usarlo como acelerador.
- La integración se centraliza en:

```text
agente_common.py
```

---

# 🔧 Optimización de Ollama Local

## Utilizar modelos ligeros

Recomendados:

- `llama3-mini`
- `llama3-small`
- Modelos quantizados (Q4, Q5, etc.)

---

## Configurar opciones de rendimiento

En `config.json`:

```json
{
  "ollama_options": {
    "num_gpu": 1,
    "main_gpu": 0,
    "low_vram": true,
    "num_thread": 4
  }
}
```

### Parámetros

| Opción | Descripción |
|----------|------------|
| `num_gpu` | Número de GPUs utilizadas |
| `main_gpu` | GPU principal |
| `low_vram` | Reduce consumo de VRAM |
| `num_thread` | Hilos CPU para inferencia |

---

## Reducir el tamaño de los prompts

### Correo

Enviar únicamente:

- Texto relevante
- Fragmentos importantes

### Facturación

Enviar únicamente:

- Filas clave
- Resúmenes de tablas

Evita enviar documentos completos cuando no sea necesario.

---

## Detectar cuellos de botella

Si observas:

- GPU ≈ 2%
- RAM creciendo constantemente

Entonces:

- Ollama probablemente está usando CPU.
- El modelo puede ser demasiado grande para tu hardware.

---

## Uso de NPU con OpenVINO

Instalar:

```powershell
pip install openvino-dev
```

Posteriormente modificar:

```text
agente_common.py
```

para utilizar:

```python
from openvino import Core
```

---

# 📈 Guía de rendimiento paso a paso

## 1. Elegir un modelo ligero

```powershell
ollama pull llama3-mini
```

```powershell
ollama create agente_correo --base llama3-mini
```

---

## 2. Configurar rendimiento

```json
{
  "ollama_model": "llama3-mini",
  "ollama_options": {
    "num_gpu": 1,
    "main_gpu": 0,
    "low_vram": true,
    "num_thread": 4
  }
}
```

---

## 3. Reducir el prompt

### correo/main.py

Mantener únicamente:

- Asunto
- Remitente
- Texto relevante

### facturacion/main.py

Mantener únicamente:

- Totales
- Filas importantes
- Resúmenes

---

## 4. Monitorear recursos

Herramientas recomendadas:

- Administrador de tareas de Windows
- Monitor de recursos

Revisar:

- Uso de GPU
- Uso de CPU
- Consumo de RAM

---

## 5. Activar aceleración con OpenVINO

```powershell
pip install openvino-dev
```

Luego adaptar la lógica de inferencia para aprovechar:

- CPU Intel
- GPU Intel
- NPU Intel AI Boost

---

# 🗓️ Automatización con Windows Task Scheduler

Para ejecutar diariamente un agente:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "C:\path\to\repo\scripts\run_agent.ps1 -agent correo"
```

### Flujo recomendado

1. Crear tarea programada.
2. Configurar frecuencia diaria.
3. Ejecutar el comando anterior.
4. Registrar logs de salida.

---

# 🔄 Flujo general del programa

## Estructura

Cada agente tiene:

```text
agente/
├── main.py
├── config.json
└── Modelfile
```

---

## Inicio

El script:

```powershell
scripts/run_agent.ps1 -agent <nombre>
```

realiza:

1. Activación del entorno virtual.
2. Carga de configuración.
3. Ejecución del agente.

---

## Generación LLM

Toda la inferencia se centraliza en:

```python
agente_common.generate_with_acceleration()
```

### Comportamiento

#### Por defecto

```python
ollama.chat(...)
```

#### Si está habilitado OpenVINO

```python
use_openvino = True
```

Se intenta detectar OpenVINO disponible en el entorno.

---

## OpenVINO

Pensado para acelerar cargas pesadas en:

- CPU Intel
- GPU Intel
- NPU Intel

---

## Seguridad

### Evitar

```json
{
  "password": "...",
  "api_key": "..."
}
```

en:

```text
config.json
```

### Recomendado

Variables de entorno:

```bash
API_KEY=xxxxx
```

o archivos:

```text
.env
```

---

# ✅ Recomendaciones rápidas

- Utiliza modelos ligeros (`llama3-mini`, `llama3-small`).
- Instala `openvino-dev` para aprovechar CPU/GPU/NPU Intel.
- Ajusta `ollama_options` según tu hardware.
- Reduce el tamaño de los prompts.
- Monitoriza GPU, CPU y RAM durante las pruebas.
- Automatiza la ejecución mediante Windows Task Scheduler.
- Mantén credenciales fuera de `config.json`.