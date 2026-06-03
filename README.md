# Agentes Ollama

Estructura del proyecto:

- `correo/` → agente de correo electrónico
- `facturacion/` → agente de facturación y Excel
- `archivos/` → agente de organización de archivos

Cada carpeta contiene:

- `venv/` → entorno virtual Python aislado
- `main.py` → script principal
- `config.json` → parámetros de configuración
- `Modelfile` → definición de rol para Ollama

## Uso básico

1. Abre una terminal en la carpeta del agente:
   - `cd correo`
   - `cd facturacion`
   - `cd archivos`

2. Activa el entorno virtual en Windows desde la carpeta del agente:
   - `cd correo`
   - `.`\venv\Scripts\Activate.ps1`

3. Ejecuta el script:
   - `python main.py`

## Notas importantes

- Si PowerShell bloquea la activación, ejecuta como administrador:
  - `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

- El archivo `config.json` contiene valores de ejemplo. Cámbialos por tus rutas, credenciales o nombres reales.

- El `Modelfile` define el rol del agente para Ollama.

- Para crear un modelo local con Ollama, sigue estas instrucciones dentro de la carpeta del agente:
  - `ollama create agente_correo`
  - `ollama create agente_facturacion`
  - `ollama create agente_archivos`

## Configuración rápida de entornos y aceleración

- Crear entornos y instalar dependencias (PowerShell):

```
.\scripts\setup_envs.ps1
```

- Ejecutar un agente (activa su venv y lanza `main.py`):

```
.\scripts\run_agent.ps1 -agent correo
```

- OpenVINO: si tienes OpenVINO instalado en el sistema, los agentes pueden intentar usarlo
   como acelerador. `agente_common.py` actúa como un punto único para integrar OpenVINO y Ollama.

## Optimizar Ollama local y recursos

- Usa un modelo más pequeño para tareas de correo y facturación: por ejemplo `llama3-mini`, `llama3-small` o un modelo quantizado.
- Configura `ollama_options` en `config.json` para forzar opciones de carga más ligeras:
  - `num_gpu`: 1
  - `main_gpu`: 0
  - `low_vram`: true
  - `num_thread`: 4
- Evita enviar textos muy largos: resume o recorta el cuerpo antes de enviarlo a la LLM.
- Si la GPU se queda en ~2% y la RAM se dispara, probablemente Ollama está usando CPU y un modelo grande.
- Para que la NPU sea útil necesitas un modelo compatible y ejecutar inferencia con OpenVINO/Intel en vez de solo
  llamar a `ollama.chat()`. Actualmente `use_openvino: true` en el config solo activa la detección; no hay una ruta
  completa de inferencia OpenVINO integrada todavía.
- En Windows, si quieres usar GPU en Ollama local, comprueba primero la documentación de Ollama y ejecuta con
  `options` como las anteriores, o usa un comando/servicio con soporte GPU.

## Guía paso a paso para mejores recursos

1. Elige un modelo ligero local de Ollama:
   - Ejecuta en PowerShell:
     ```powershell
     ollama pull llama3-mini
     ```
   - O crea un modelo local más pequeño:
     ```powershell
     ollama create agente_correo --base llama3-mini
     ```
   - En `correo/config.json` y `facturacion/config.json`, pon:
     ```json
     "ollama_model": "llama3-mini"
     ```

2. Configura los ajustes de rendimiento:
   - En cada `config.json` que use LLM, agrega o edita:
     ```json
     "ollama_options": {
       "num_gpu": 1,
       "main_gpu": 0,
       "low_vram": true,
       "num_thread": 4
     }
     ```
   - Esto le dice a Ollama que trate de usar GPU y memoria baja.

3. Reduce el tamaño del prompt:
   - En `correo/main.py`, procesa solo el texto plano esencial del correo.
   - En `facturacion/main.py`, manda solo las filas clave o un resumen de la tabla.
   - Menos tokens = menos uso de RAM y menos tiempo de inferencia.

4. Comprueba el estado de GPU/NPU:
   - En Windows, abre el Administrador de tareas y revisa:
     - Uso de GPU por proceso Python/Ollama.
     - Memoria usada por Python.
   - Si la GPU sigue en 2%, puede deberse a que Ollama no está configurado para usarla o el modelo no la admite.

5. Si quieres usar NPU con OpenVINO, instala y prueba el runtime:
   - En el entorno del agente:
     ```powershell
     .\venv\Scripts\Activate.ps1
     pip install openvino-dev
     ```
   - Luego, utiliza un modelo convertido a OpenVINO y modifica `agente_common.py` para ejecutar inferencia con
     `openvino.runtime.Core` en lugar de solo `ollama.chat()`.

6. Ejecuta y compara:
   - Prueba con un modelo grande y con uno pequeño.
   - Mide con:
     ```powershell
     .\scripts\run_agent.ps1 -agent correo
     ```
   - Observa si la memoria baja y la GPU sube su uso.

## Recomendación rápida de instalación

1. Si necesitas velocidad y menor RAM, instala un modelo ligero local de Ollama.
2. Para NPU: instala `openvino` / `openvino-dev` y convierte un modelo compatible a OpenVINO.
3. Para GPU: usa Ollama con `num_gpu` y `low_vram` en `ollama_options`, y asegúrate de que tu driver está activo.

## Scheduler (Windows Task Scheduler)

- Para ejecutar diariamente un agente, crea una tarea programada que ejecute PowerShell:

```
powershell -NoProfile -ExecutionPolicy Bypass -Command "C:\path\to\repo\scripts\run_agent.ps1 -agent correo"
```

**Cómo funciona el programa (flujo general)**

- **Estructura:** cada agente está en su carpeta (`correo`, `facturacion`, `archivos`) con `main.py` y `config.json`.
- **Inicio:** ejecutar `scripts/run_agent.ps1 -agent <nombre>` activa el `venv` del agente y ejecuta su `main.py`.
- **Resumen / LLM:** cuando un agente necesita generar texto (por ejemplo, resúmenes de correo o de facturación),
   llama a `agente_common.generate_with_acceleration()` que centraliza la llamada a la LLM.
   - Por defecto usa la API local de Ollama (`ollama.chat`).
   - Si activas `use_openvino: true` en `config.json`, el helper intenta detectar `openvino.runtime`.
      Actualmente `agente_common` usa OpenVINO como marcador: muestra detección y por defecto hace fallback a Ollama.
      Integrar OpenVINO completamente requiere convertir/optimizar un modelo compatible y añadir la lógica de tokenización
      y ejecución (éste helper es el lugar para hacerlo).
- **OpenVINO:** pensado para acelerar cargas pesadas (CPU/GPU/NPU Intel). Requiere:
   1. Modelo compatible (convertido a OpenVINO IR/OV format).
   2. Pipeline de tokenización/decodificación compatible con el modelo.
   3. Código de inferencia en `agente_common` que use `openvino.runtime.Core`.
- **Seguridad:** `config.json` puede contener credenciales (ej. IMAP). Recomiendo usar variables de entorno
   o un `.env` no versionado para almacenar secretos.
