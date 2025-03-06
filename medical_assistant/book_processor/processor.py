import os
import PyPDF2
import ebooklib
from ebooklib import epub
import nltk
from nltk.tokenize import sent_tokenize
import re
import json

class BookProcessor:
    def __init__(self, library_path):
        """
        Inicializa o processador de livros com o caminho para a biblioteca.
        
        Args:
            library_path (str): Caminho para a pasta contendo os livros médicos
        """
        self.library_path = library_path
        self.processed_content = {}
        self.knowledge_base = ""
        
        # Garantir que os recursos do NLTK estejam disponíveis
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def scan_library(self):
        """
        Escaneia a biblioteca em busca de livros em formatos suportados.
        
        Returns:
            list: Lista de caminhos para os livros encontrados
        """
        supported_extensions = ['.pdf', '.epub', '.txt']
        books = []
        
        for root, _, files in os.walk(self.library_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_extensions:
                    books.append(os.path.join(root, file))
        
        print(f"Encontrados {len(books)} livros na biblioteca.")
        return books
    
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
        except Exception as e:
            print(f"Erro ao processar o PDF {pdf_path}: {e}")
        
        return text
    
    def process_epub(self, epub_path):
        """
        Extrai o texto de um arquivo EPUB.
        
        Args:
            epub_path (str): Caminho para o arquivo EPUB
            
        Returns:
            str: Texto extraído do EPUB
        """
        text = ""
        try:
            book = epub.read_epub(epub_path)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content().decode('utf-8')
                    # Remover tags HTML
                    text += re.sub('<[^<]+?>', '', content) + "\n"
        except Exception as e:
            print(f"Erro ao processar o EPUB {epub_path}: {e}")
        
        return text
    
    def process_txt(self, txt_path):
        """
        Lê o conteúdo de um arquivo de texto.
        
        Args:
            txt_path (str): Caminho para o arquivo de texto
            
        Returns:
            str: Conteúdo do arquivo de texto
        """
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(txt_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Erro ao processar o arquivo de texto {txt_path}: {e}")
                return ""
    
    def process_book(self, book_path):
        """
        Processa um livro com base em sua extensão.
        
        Args:
            book_path (str): Caminho para o livro
            
        Returns:
            str: Texto extraído do livro
        """
        ext = os.path.splitext(book_path)[1].lower()
        book_name = os.path.basename(book_path)
        
        print(f"Processando: {book_name}")
        
        if ext == '.pdf':
            content = self.process_pdf(book_path)
        elif ext == '.epub':
            content = self.process_epub(book_path)
        elif ext == '.txt':
            content = self.process_txt(book_path)
        else:
            print(f"Formato não suportado: {ext}")
            return None
        
        self.processed_content[book_name] = content
        return content
    
    def process_all_books(self):
        """
        Processa todos os livros na biblioteca.
        
        Returns:
            dict: Dicionário com o conteúdo processado de cada livro
        """
        books = self.scan_library()
        for book_path in books:
            self.process_book(book_path)
        
        return self.processed_content
    
    def extract_medical_knowledge(self):
        """
        Extrai conhecimento médico dos livros processados.
        
        Returns:
            str: Base de conhecimento médico extraída
        """
        all_text = ""
        for book_name, content in self.processed_content.items():
            all_text += f"\n\n--- CONTEÚDO DE {book_name} ---\n\n"
            all_text += content
        
        # Aqui poderíamos implementar técnicas mais avançadas de NLP
        # para extrair apenas informações médicas relevantes
        
        self.knowledge_base = all_text
        return self.knowledge_base
    
    def save_knowledge_base(self, output_path):
        """
        Salva a base de conhecimento em um arquivo.
        
        Args:
            output_path (str): Caminho para salvar a base de conhecimento
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(self.knowledge_base)
        
        print(f"Base de conhecimento salva em: {output_path}")
    
    def save_processed_content(self, output_dir):
        """
        Salva o conteúdo processado de cada livro em arquivos separados.
        
        Args:
            output_dir (str): Diretório para salvar os arquivos
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for book_name, content in self.processed_content.items():
            safe_name = re.sub(r'[^\w\-_.]', '_', book_name)
            output_path = os.path.join(output_dir, f"{safe_name}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(content)
        
        print(f"Conteúdo processado salvo em: {output_dir}")
