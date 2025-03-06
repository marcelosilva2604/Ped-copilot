#!/usr/bin/env python3
"""
Medical Copilot - Um assistente médico que funciona como um copilot enquanto você escreve.
"""

import os
import sys
import time
import threading
import PyPDF2
import requests
import json

class MedicalCopilot:
    def __init__(self, api_key):
        """
        Inicializa o Medical Copilot.
        
        Args:
            api_key (str): Chave de API da Anthropic
        """
        self.api_key = api_key
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        self.model = "claude-3-opus-20240229"
        self.max_tokens = 1000
        self.medical_knowledge = ""
        self.current_text = ""
        self.current_file = None
        self.suggestion_thread = None
        self.running = True
        
    def process_pdf(self, pdf_path):
        """
        Extrai o texto de um arquivo PDF.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
            
        Returns:
            str: Texto extraído do PDF
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    # Mostrar progresso
                    print(f"Processando {os.path.basename(pdf_path)}: {page_num+1}/{len(reader.pages)} páginas", end="\r")
        except Exception as e:
            print(f"Erro ao processar o PDF {pdf_path}: {e}")
        
        return text
    
    def load_medical_books(self, books_path):
        """
        Carrega e processa os livros médicos.
        
        Args:
            books_path (str): Caminho para a pasta contendo os livros médicos
        """
        if not os.path.exists(books_path):
            print(f"O caminho '{books_path}' não existe.")
            return False
        
        print(f"Processando livros em: {books_path}")
        
        # Encontrar todos os PDFs na pasta
        pdfs = []
        for root, _, files in os.walk(books_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdfs.append(os.path.join(root, file))
        
        if not pdfs:
            print("Nenhum arquivo PDF encontrado.")
            return False
        
        print(f"Encontrados {len(pdfs)} arquivos PDF.")
        
        # Processar cada PDF
        all_text = ""
        for pdf_path in pdfs:
            print(f"Processando: {os.path.basename(pdf_path)}")
            text = self.process_pdf(pdf_path)
            all_text += f"\n\n--- CONTEÚDO DE {os.path.basename(pdf_path)} ---\n\n"
            all_text += text
            print(f"Concluído: {os.path.basename(pdf_path)}                    ")
        
        # Limitar o tamanho do conhecimento médico para evitar tokens excessivos
        max_chars = 100000  # Aproximadamente 25k tokens
        if len(all_text) > max_chars:
            print(f"Texto extraído muito grande ({len(all_text)} caracteres). Limitando a {max_chars} caracteres.")
            all_text = all_text[:max_chars]
        
        self.medical_knowledge = all_text
        print(f"Processamento concluído. Extraídos {len(all_text)} caracteres de texto.")
        return True
    
    def get_completion(self, prompt, system_prompt="", temperature=0.7):
        """
        Obtém uma resposta do modelo Claude baseada no prompt fornecido.
        
        Args:
            prompt (str): Prompt para o modelo
            system_prompt (str): Prompt do sistema
            temperature (float): Temperatura para geração de texto
            
        Returns:
            str: Resposta do modelo
        """
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            print(f"Erro ao comunicar com a API da Anthropic: {e}")
            if 'response' in locals() and response:
                print(f"Resposta da API: {response.text}")
            return "Não foi possível obter uma resposta. Verifique sua conexão ou chave de API."
    
    def get_medical_suggestions(self, current_text):
        """
        Obtém sugestões médicas com base no texto atual.
        
        Args:
            current_text (str): Texto atual
            
        Returns:
            str: Sugestões médicas
        """
        prompt = f"""
        Texto atual do prontuário médico:
        
        {current_text}
        
        Com base no texto acima, forneça sugestões para continuar o prontuário, incluindo:
        1. Possíveis diagnósticos baseados nos sintomas e informações apresentadas
        2. Condutas médicas recomendadas
        3. Exames que poderiam ser solicitados
        4. Medicações que poderiam ser prescritas com dosagens
        5. Recomendações de acompanhamento
        
        Forneça suas sugestões de forma concisa e direta, como um copilot médico que está auxiliando na escrita do prontuário.
        """
        
        system_prompt = f"""Você é um assistente médico especializado que funciona como um copilot para ajudar médicos a escrever prontuários.
        Use seu conhecimento médico e as seguintes informações extraídas de livros médicos como referência:
        
        {self.medical_knowledge[:10000]}  # Limitando para não exceder o limite de tokens
        """
        
        return self.get_completion(prompt, system_prompt)
    
    def create_new_file(self):
        """
        Cria um novo arquivo de texto.
        """
        file_path = input("Digite o nome do arquivo (ou caminho completo): ")
        if not file_path.endswith('.txt'):
            file_path += '.txt'
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("")
            self.current_file = file_path
            self.current_text = ""
            print(f"Arquivo criado: {file_path}")
            return True
        except Exception as e:
            print(f"Erro ao criar o arquivo: {e}")
            return False
    
    def open_file(self):
        """
        Abre um arquivo existente.
        """
        file_path = input("Digite o caminho do arquivo a ser aberto: ")
        if not os.path.exists(file_path):
            print(f"O arquivo '{file_path}' não existe.")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.current_text = file.read()
            self.current_file = file_path
            print(f"Arquivo aberto: {file_path}")
            return True
        except Exception as e:
            print(f"Erro ao abrir o arquivo: {e}")
            return False
    
    def save_file(self):
        """
        Salva o arquivo atual.
        """
        if not self.current_file:
            print("Nenhum arquivo aberto.")
            return False
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.current_text)
            print(f"Arquivo salvo: {self.current_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
            return False
    
    def edit_text(self):
        """
        Edita o texto atual com sugestões do copilot.
        """
        if not self.current_file:
            print("Nenhum arquivo aberto. Crie ou abra um arquivo primeiro.")
            return
        
        print("\n=== EDITOR DE TEXTO COM COPILOT MÉDICO ===")
        print("Digite o texto do prontuário. O copilot fornecerá sugestões.")
        print("Comandos especiais:")
        print("  :s - Salvar o arquivo")
        print("  :q - Sair do editor")
        print("  :c - Obter sugestões do copilot")
        print("\nTexto atual:")
        print("-" * 50)
        print(self.current_text)
        print("-" * 50)
        
        while True:
            line = input("> ")
            
            if line == ":q":
                break
            elif line == ":s":
                self.save_file()
            elif line == ":c":
                print("\nObtendo sugestões do copilot... Aguarde...")
                suggestions = self.get_medical_suggestions(self.current_text)
                print("\n=== SUGESTÕES DO COPILOT ===")
                print(suggestions)
                print("=" * 50)
            else:
                if self.current_text and not self.current_text.endswith("\n"):
                    self.current_text += "\n"
                self.current_text += line
                
                # Obter sugestões automaticamente após cada parágrafo
                if line.strip() == "":
                    print("\nObtendo sugestões do copilot... Aguarde...")
                    suggestions = self.get_medical_suggestions(self.current_text)
                    print("\n=== SUGESTÕES DO COPILOT ===")
                    print(suggestions)
                    print("=" * 50)
    
    def show_menu(self):
        """
        Exibe o menu principal.
        """
        print("\n=== MEDICAL COPILOT ===")
        print("1. Carregar livros médicos")
        print("2. Criar novo arquivo")
        print("3. Abrir arquivo existente")
        print("4. Editar arquivo atual")
        print("5. Salvar arquivo")
        print("6. Sair")
        
        choice = input("\nEscolha uma opção (1-6): ")
        
        if choice == "1":
            books_path = input("Digite o caminho para a pasta contendo os livros médicos: ")
            self.load_medical_books(books_path)
        elif choice == "2":
            self.create_new_file()
        elif choice == "3":
            self.open_file()
        elif choice == "4":
            self.edit_text()
        elif choice == "5":
            self.save_file()
        elif choice == "6":
            print("\nEncerrando o programa...")
            self.running = False
        else:
            print("\nOpção inválida. Tente novamente.")
    
    def run(self):
        """
        Executa o Medical Copilot.
        """
        print("Bem-vindo ao Medical Copilot!")
        print("Este programa utiliza a API da Anthropic Claude para fornecer assistência médica enquanto você escreve.")
        
        while self.running:
            self.show_menu()

def main():
    """
    Função principal.
    """
    # Verificar se a chave de API foi fornecida
    if len(sys.argv) < 2:
        print("Erro: Chave de API da Anthropic não fornecida.")
        print("Uso: python medical_copilot.py <chave_api>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Verificar se o PyPDF2 está instalado
    try:
        import PyPDF2
    except ImportError:
        print("Erro: A biblioteca PyPDF2 não está instalada.")
        print("Instale-a com: pip install PyPDF2==3.0.1")
        sys.exit(1)
    
    # Iniciar o copilot
    copilot = MedicalCopilot(api_key)
    copilot.run()

if __name__ == "__main__":
    main() 