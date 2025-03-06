import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from book_processor.processor import BookProcessor
from text_editor.editor import MedicalTextEditor
from ai_integration.anthropic_client import AnthropicClient

def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos analisados
    """
    # Definir o caminho padrão para a pasta lib
    default_lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
    
    parser = argparse.ArgumentParser(description="Assistente Médico com IA")
    parser.add_argument("--library", "-l", help="Caminho para a biblioteca de livros médicos", default=default_lib_path)
    parser.add_argument("--api-key", "-k", help="Chave de API da Anthropic")
    parser.add_argument("--process-only", action="store_true", help="Apenas processar livros sem iniciar o editor")
    parser.add_argument("--knowledge-base", "-kb", help="Caminho para a base de conhecimento pré-processada")
    
    return parser.parse_args()

def select_library_path():
    """
    Solicita ao usuário que selecione o caminho da biblioteca.
    
    Returns:
        str: Caminho selecionado ou None se cancelado
    """
    root = tk.Tk()
    root.withdraw()
    
    # Definir o caminho padrão para a pasta lib
    default_lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
    
    messagebox.showinfo(
        "Selecionar Biblioteca", 
        "Por favor, selecione a pasta que contém seus livros médicos.\n\nA pasta padrão 'lib' já foi criada para você."
    )
    
    path = filedialog.askdirectory(title="Selecione a pasta da biblioteca médica", initialdir=default_lib_path)
    
    if not path:
        # Se o usuário cancelar, usar o caminho padrão
        messagebox.showinfo("Informação", "Usando a pasta padrão 'lib' para a biblioteca médica.")
        return default_lib_path
    
    return path

def get_api_key():
    """
    Solicita ao usuário que insira a chave de API da Anthropic.
    
    Returns:
        str: Chave de API ou None se cancelado
    """
    root = tk.Tk()
    root.withdraw()
    
    api_key = tk.simpledialog.askstring(
        "Chave de API da Anthropic", 
        "Por favor, insira sua chave de API da Anthropic:",
        show='*'
    )
    
    if not api_key:
        messagebox.showwarning("Aviso", "Nenhuma chave de API fornecida. O programa será encerrado.")
        return None
    
    return api_key

def process_library(library_path):
    """
    Processa a biblioteca de livros médicos.
    
    Args:
        library_path (str): Caminho para a biblioteca
        
    Returns:
        str: Caminho para a base de conhecimento gerada
    """
    print(f"Processando biblioteca em: {library_path}")
    
    processor = BookProcessor(library_path)
    processor.process_all_books()
    
    # Criar diretório para armazenar a base de conhecimento
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
    os.makedirs(output_dir, exist_ok=True)
    
    # Extrair e salvar a base de conhecimento
    processor.extract_medical_knowledge()
    kb_path = os.path.join(output_dir, "medical_knowledge.txt")
    processor.save_knowledge_base(kb_path)
    
    # Salvar conteúdo processado de cada livro
    books_dir = os.path.join(output_dir, "books")
    processor.save_processed_content(books_dir)
    
    return kb_path

def load_knowledge_base(kb_path):
    """
    Carrega a base de conhecimento de um arquivo.
    
    Args:
        kb_path (str): Caminho para o arquivo da base de conhecimento
        
    Returns:
        str: Conteúdo da base de conhecimento
    """
    try:
        with open(kb_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Erro ao carregar a base de conhecimento: {e}")
        return ""

def main():
    """
    Função principal do programa.
    """
    # Analisar argumentos da linha de comando
    args = parse_arguments()
    
    # Obter caminho da biblioteca
    library_path = args.library
    if not library_path:
        library_path = select_library_path()
        if not library_path:
            return
    
    # Obter chave de API
    api_key = args.api_key
    if not api_key:
        api_key = get_api_key()
        if not api_key:
            return
    
    # Inicializar cliente da API
    ai_client = AnthropicClient(api_key)
    
    # Processar biblioteca ou carregar base de conhecimento existente
    kb_path = args.knowledge_base
    if not kb_path:
        kb_path = process_library(library_path)
    
    # Carregar base de conhecimento
    knowledge_base = load_knowledge_base(kb_path)
    ai_client.set_medical_context(knowledge_base)
    
    print(f"Base de conhecimento carregada de: {kb_path}")
    
    # Se a flag --process-only estiver definida, encerrar após o processamento
    if args.process_only:
        print("Processamento concluído. Encerrando.")
        return
    
    # Iniciar o editor de texto
    print("Iniciando o editor de texto...")
    editor = MedicalTextEditor(ai_client)
    editor.run()

if __name__ == "__main__":
    main()
