#!/usr/bin/env python3
"""
Assistente Médico Simplificado usando requisições HTTP diretas para a API da Anthropic.
"""

import os
import sys
from simple_anthropic_client import SimpleAnthropicClient

class SimpleMedicalAssistant:
    def __init__(self, api_key):
        """
        Inicializa o assistente médico simplificado.
        
        Args:
            api_key (str): Chave de API da Anthropic
        """
        self.client = SimpleAnthropicClient(api_key)
        self.patient_context = ""
        self.medical_knowledge = ""
        
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
            return
        
        print("\n=== ANALISANDO DADOS DO PACIENTE ===")
        print("Aguarde enquanto a IA analisa os dados...")
        
        prompt = f"""
        Analise os seguintes dados do paciente e forneça insights médicos relevantes:
        
        {self.patient_context}
        
        Considere possíveis diagnósticos, recomendações de tratamento, e quaisquer 
        sinais de alerta que devam ser investigados.
        """
        
        system_prompt = f"Você é um assistente médico especializado. {self.medical_knowledge}"
        
        analysis = self.client.get_completion(prompt, system_prompt)
        
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
        
        prompt = f"""
        Contexto do paciente: {self.patient_context}
        
        Texto atual: {current_text}
        
        Com base no texto atual e no contexto do paciente, forneça sugestões médicas relevantes 
        para continuar o texto. Considere diagnósticos possíveis, tratamentos recomendados, 
        exames adicionais ou observações importantes a serem incluídas.
        """
        
        system_prompt = f"Você é um assistente médico especializado. {self.medical_knowledge}"
        
        suggestions = self.client.get_completion(prompt, system_prompt)
        
        print("\n=== SUGESTÕES MÉDICAS ===")
        print(suggestions)
    
    def load_medical_books(self):
        """
        Carrega informações dos livros médicos.
        """
        print("\n=== CARREGAR LIVROS MÉDICOS ===")
        print("Digite o caminho para a pasta contendo os livros médicos:")
        
        books_path = input().strip()
        if not os.path.exists(books_path):
            print(f"\nO caminho '{books_path}' não existe.")
            return
        
        print("\nProcessando livros... (Simulado)")
        
        # Simulamos o processamento dos livros
        self.medical_knowledge = "Use seu conhecimento médico para fornecer informações precisas e úteis."
        
        print("\nLivros médicos carregados com sucesso.")
    
    def show_menu(self):
        """
        Exibe o menu principal.
        """
        print("\n=== ASSISTENTE MÉDICO COM IA ===")
        print("1. Definir contexto do paciente")
        print("2. Analisar dados do paciente")
        print("3. Obter sugestões médicas")
        print("4. Carregar livros médicos")
        print("5. Sair")
        
        choice = input("\nEscolha uma opção (1-5): ")
        
        if choice == "1":
            self.set_patient_context()
        elif choice == "2":
            self.analyze_patient_data()
        elif choice == "3":
            self.get_medical_suggestions()
        elif choice == "4":
            self.load_medical_books()
        elif choice == "5":
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
        print("Uso: python simple_terminal_assistant.py <chave_api>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Iniciar o assistente
    assistant = SimpleMedicalAssistant(api_key)
    assistant.run()

if __name__ == "__main__":
    main() 