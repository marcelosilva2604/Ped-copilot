#!/usr/bin/env python3
"""
Script de inicialização para o Assistente Médico com IA.
"""

import os
import sys
import subprocess

def main():
    # Verificar se as dependências estão instaladas
    try:
        import anthropic
        import PyPDF2
        import ebooklib
        import nltk
        import numpy
    except ImportError:
        print("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependências instaladas com sucesso!")
    
    # Executar o programa principal
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "medical_assistant", "main.py")
    
    # Passar argumentos da linha de comando para o script principal
    args = sys.argv[1:]
    cmd = [sys.executable, main_script] + args
    
    try:
        subprocess.call(cmd)
    except Exception as e:
        print(f"Erro ao executar o programa: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 