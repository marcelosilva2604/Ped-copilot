#!/usr/bin/env python3
"""
Script simplificado do Assistente Médico com IA.
Este script demonstra a funcionalidade principal usando apenas a API da Anthropic.
"""

import os
import sys
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
import threading

# Importar o cliente da Anthropic
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "medical_assistant"))
from ai_integration.anthropic_client import AnthropicClient

class SimpleMedicalEditor:
    def __init__(self, api_key):
        """
        Inicializa o editor médico simplificado.
        
        Args:
            api_key (str): Chave de API da Anthropic
        """
        self.ai_client = AnthropicClient(api_key)
        self.root = None
        self.text_area = None
        self.suggestion_area = None
        self.status_bar = None
        self.patient_context = ""
        self.last_text = ""
        self.suggestion_thread = None
        
    def setup_ui(self):
        """
        Configura a interface do usuário.
        """
        self.root = tk.Tk()
        self.root.title("Assistente Médico Simplificado")
        self.root.geometry("1200x800")
        
        # Área principal dividida em duas partes
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de texto principal
        text_frame = tk.LabelFrame(main_frame, text="Anotações do Paciente")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_area.bind("<KeyRelease>", self.on_text_change)
        
        # Área de sugestões
        suggestion_frame = tk.LabelFrame(main_frame, text="Sugestões Médicas")
        suggestion_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.suggestion_area = scrolledtext.ScrolledText(suggestion_frame, wrap=tk.WORD, font=("Arial", 12), bg="#f0f0f0")
        self.suggestion_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.suggestion_area.config(state=tk.DISABLED)
        
        # Barra de status
        self.status_bar = tk.Label(self.root, text="Pronto", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Botões
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="Definir Contexto do Paciente", command=self.set_patient_context).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Analisar Dados do Paciente", command=self.analyze_patient_data).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Atualizar Sugestões", command=self.update_suggestions).pack(side=tk.LEFT, padx=5)
        
    def set_patient_context(self):
        """
        Abre uma janela para definir o contexto do paciente.
        """
        context_window = tk.Toplevel(self.root)
        context_window.title("Contexto do Paciente")
        context_window.geometry("600x400")
        
        tk.Label(context_window, text="Insira informações relevantes sobre o paciente:").pack(pady=10)
        
        context_text = scrolledtext.ScrolledText(context_window, wrap=tk.WORD, font=("Arial", 12))
        context_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        context_text.insert(tk.END, self.patient_context)
        
        def save_context():
            self.patient_context = context_text.get(1.0, tk.END).strip()
            context_window.destroy()
            self.update_status("Contexto do paciente atualizado")
            self.update_suggestions()
        
        tk.Button(context_window, text="Salvar", command=save_context).pack(pady=10)
    
    def analyze_patient_data(self):
        """
        Analisa os dados do paciente usando a IA.
        """
        if not self.patient_context:
            messagebox.showinfo("Informação", "Por favor, defina o contexto do paciente primeiro.")
            self.set_patient_context()
            return
        
        self.update_status("Analisando dados do paciente...")
        
        def analyze():
            analysis = self.ai_client.analyze_patient_data(self.patient_context)
            
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Análise do Paciente")
            analysis_window.geometry("800x600")
            
            analysis_text = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD, font=("Arial", 12))
            analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            analysis_text.insert(tk.END, analysis)
            analysis_text.config(state=tk.DISABLED)
            
            self.update_status("Análise do paciente concluída")
        
        threading.Thread(target=analyze).start()
    
    def on_text_change(self, event=None):
        """
        Manipula eventos de alteração de texto.
        """
        current_text = self.text_area.get(1.0, tk.END).strip()
        
        # Só atualiza se o texto mudou significativamente
        if abs(len(current_text) - len(self.last_text)) > 10:
            self.last_text = current_text
            self.update_suggestions()
    
    def update_suggestions(self):
        """
        Atualiza as sugestões médicas com base no texto atual.
        """
        if self.suggestion_thread and self.suggestion_thread.is_alive():
            return  # Já está atualizando
        
        current_text = self.text_area.get(1.0, tk.END).strip()
        if not current_text:
            return  # Não há texto para analisar
        
        self.update_status("Gerando sugestões médicas...")
        
        def get_suggestions():
            suggestions = self.ai_client.get_medical_suggestions(current_text, self.patient_context)
            
            self.suggestion_area.config(state=tk.NORMAL)
            self.suggestion_area.delete(1.0, tk.END)
            self.suggestion_area.insert(tk.END, suggestions)
            self.suggestion_area.config(state=tk.DISABLED)
            
            self.update_status("Sugestões médicas atualizadas")
        
        self.suggestion_thread = threading.Thread(target=get_suggestions)
        self.suggestion_thread.start()
    
    def update_status(self, message):
        """
        Atualiza a barra de status.
        
        Args:
            message (str): Mensagem a ser exibida
        """
        self.status_bar.config(text=message)
    
    def run(self):
        """
        Inicia o editor.
        """
        self.setup_ui()
        self.root.mainloop()

def get_api_key():
    """
    Obtém a chave de API da Anthropic.
    
    Returns:
        str: Chave de API
    """
    # Verificar se a chave foi passada como argumento
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Caso contrário, solicitar ao usuário
    root = tk.Tk()
    root.withdraw()
    
    api_key = simpledialog.askstring(
        "Chave de API da Anthropic", 
        "Por favor, insira sua chave de API da Anthropic:",
        show='*'
    )
    
    if not api_key:
        messagebox.showwarning("Aviso", "Nenhuma chave de API fornecida. O programa será encerrado.")
        sys.exit(1)
    
    return api_key

def main():
    """
    Função principal.
    """
    # Obter a chave de API
    api_key = get_api_key()
    
    # Iniciar o editor
    editor = SimpleMedicalEditor(api_key)
    editor.run()

if __name__ == "__main__":
    main() 