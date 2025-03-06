#!/usr/bin/env python3
"""
Versão de terminal do Assistente Médico com IA.
Este script demonstra a funcionalidade principal usando apenas a API da Anthropic em um ambiente de terminal.
"""

import os
import sys
import time

# Importar o cliente da Anthropic
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "medical_assistant"))
from ai_integration.anthropic_client import AnthropicClient

class TerminalMedicalAssistant:
    def __init__(self, api_key):
        """
        Inicializa o assistente médico de terminal.
        
        Args:
            api_key (str): Chave de API da Anthropic
        """
        self.ai_client = AnthropicClient(api_key)
        self.patient_context = ""
        
    def set_patient_context(self):
        """
        Define o contexto do paciente.
        """
        print("\n=== DEFINIR CONTEXTO DO PACIENTE ===")
        print("Insira informações relevantes sobre o paciente (digite 'FIM' em uma linha separada para terminar):")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "FIM":
                break
            lines.append(line)
        
        self.patient_context = "\n".join(lines)
        print("\nContexto do paciente atualizado.")
    
    def analyze_patient_data(self):
        """
        Analisa os dados do paciente usando a IA.
        """
        if not self.patient_context:
            print("\nPor favor, defina o contexto do paciente primeiro.")
            self.set_patient_context()
        
        print("\n=== ANALISANDO DADOS DO PACIENTE ===")
        print("Aguarde enquanto a IA analisa os dados...")
        
        analysis = self.ai_client.analyze_patient_data(self.patient_context)
        
        print("\n=== ANÁLISE DO PACIENTE ===")
        print(analysis)
    
    def get_medical_suggestions(self):
        """
        Obtém sugestões médicas com base no texto atual.
        """
        print("\n=== OBTER SUGESTÕES MÉDICAS ===")
        print("Digite o texto atual sobre o paciente (digite 'FIM' em uma linha separada para terminar):")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "FIM":
                break
            lines.append(line)
        
        current_text = "\n".join(lines)
        
        if not current_text:
            print("\nNenhum texto fornecido.")
            return
        
        print("\nGerando sugestões médicas... Aguarde...")
        
        suggestions = self.ai_client.get_medical_suggestions(current_text, self.patient_context)
        
        print("\n=== SUGESTÕES MÉDICAS ===")
        print(suggestions)
    
    def show_menu(self):
        """
        Exibe o menu principal.
        """
        print("\n=== ASSISTENTE MÉDICO COM IA ===")
        print("1. Definir contexto do paciente")
        print("2. Analisar dados do paciente")
        print("3. Obter sugestões médicas")
        print("4. Sair")
        
        choice = input("\nEscolha uma opção (1-4): ")
        
        if choice == "1":
            self.set_patient_context()
        elif choice == "2":
            self.analyze_patient_data()
        elif choice == "3":
            self.get_medical_suggestions()
        elif choice == "4":
            print("\nEncerrando o programa...")
            sys.exit(0)
        else:
            print("\nOpção inválida. Tente novamente.")
    
    def run(self):
        """
        Executa o assistente médico.
        """
        print("Bem-vindo ao Assistente Médico com IA!")
        print("Este programa utiliza a API da Anthropic Claude para fornecer assistência médica.")
        
        while True:
            self.show_menu()

def main():
    """
    Função principal.
    """
    # Verificar se a chave de API foi fornecida
    if len(sys.argv) < 2:
        print("Erro: Chave de API da Anthropic não fornecida.")
        print("Uso: python terminal_medical_assistant.py <chave_api>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Iniciar o assistente
    assistant = TerminalMedicalAssistant(api_key)
    assistant.run()

if __name__ == "__main__":
    main() 