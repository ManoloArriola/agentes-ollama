#!/usr/bin/env python3
"""
Test script to validate Ollama + llama3.2:3b integration
without needing real IMAP or email setup.
"""

import json
from pathlib import Path
import sys

# Add parent to path
ROOT = Path(__file__).parent
sys.path.append(str(ROOT))

from agente_common import generate_with_acceleration

def test_basic_chat():
    """Test basic chat with conservative options"""
    print("=" * 60)
    print("Test 1: Basic chat with Ollama + llama3.2:3b")
    print("=" * 60)
    
    messages = [
        {"role": "system", "content": "Eres un asistente útil en español."},
        {"role": "user", "content": "¿Cuál es la capital de Francia?"},
    ]
    
    options = {
        "num_gpu": 0,
        "num_thread": 2,
    }
    
    try:
        result = generate_with_acceleration(
            messages,
            model="llama3.2:3b",
            use_openvino=False,
            options=options
        )
        print(f"\n✅ Respuesta: {result}\n")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False

def test_email_summarization():
    """Test email summarization (core feature)"""
    print("=" * 60)
    print("Test 2: Email summarization (simulated)")
    print("=" * 60)
    
    # Simulated email body
    email_body = """
    Estimado,
    
    Quería confirmar la reunión de mañana a las 10 AM en la sala de conferencias.
    Por favor, trae los documentos del proyecto Q3.
    
    También necesito que revises el reporte de presupuesto que envié la semana pasada.
    Tengo algunas preguntas sobre las partidas de marketing.
    
    Saludos,
    Juan
    """
    
    messages = [
        {"role": "system", "content": "Eres un asistente que resume correos en español. Proporciona un resumen breve en máximo 3 puntos."},
        {"role": "user", "content": f"Resume este correo:\n\n{email_body}"},
    ]
    
    options = {
        "num_gpu": 0,
        "num_thread": 2,
    }
    
    try:
        result = generate_with_acceleration(
            messages,
            model="llama3.2:3b",
            use_openvino=False,
            options=options
        )
        print(f"\n✅ Resumen:\n{result}\n")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False

def main():
    print("\n" + "=" * 60)
    print("Validación de integración Ollama + llama3.2:3b")
    print("=" * 60 + "\n")
    
    test1_ok = test_basic_chat()
    test2_ok = test_email_summarization()
    
    print("=" * 60)
    if test1_ok and test2_ok:
        print("✅ Todos los tests pasaron. Sistema funcionando.")
    else:
        print("❌ Algunos tests fallaron. Revisar configuración.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
