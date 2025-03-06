import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, Menu
import threading
import time

class MedicalTextEditor:
    def __init__(self, ai_client):
        """
        Inicializa o editor de texto médico.
        
        Args:
            ai_client: Cliente da API da Anthropic para obter sugestões
        """
        self.ai_client = ai_client
        self.root = None
        self.text_area = None
        self.suggestion_area = None
        self.status_bar = None
        self.current_file = None
        self.patient_context = ""
        self.last_text = ""
        self.suggestion_thread = None
        self.running = False
        
    def setup_ui(self):
        """
        Configura a interface do usuário do editor.
        """
        self.root = tk.Tk()
        self.root.title("Assistente Médico - Editor de Texto")
        self.root.geometry("1200x800")
        
        # Configurar menu
        menu_bar = Menu(self.root)
        
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Novo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Salvar", command=self.save_file)
        file_menu.add_command(label="Salvar como", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        
        patient_menu = Menu(menu_bar, tearoff=0)
        patient_menu.add_command(label="Definir contexto do paciente", command=self.set_patient_context)
        patient_menu.add_command(label="Analisar dados do paciente", command=self.analyze_patient_data)
        menu_bar.add_cascade(label="Paciente", menu=patient_menu)
        
        self.root.config(menu=menu_bar)
        
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
        
    def new_file(self):
        """
        Cria um novo arquivo.
        """
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Assistente Médico - Editor de Texto")
        self.update_status("Novo arquivo criado")
        
    def open_file(self):
        """
        Abre um arquivo existente.
        """
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                    self.current_file = file_path
                    self.root.title(f"Assistente Médico - {file_path}")
                    self.update_status(f"Arquivo aberto: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")
    
    def save_file(self):
        """
        Salva o arquivo atual.
        """
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.update_status(f"Arquivo salvo: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """
        Salva o arquivo com um novo nome.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"Assistente Médico - {file_path}")
                self.update_status(f"Arquivo salvo como: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")
    
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
        
        self.update_status("Gerando sugestões médicas...")
        
        def get_suggestions():
            current_text = self.text_area.get(1.0, tk.END).strip()
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
        Inicia o editor de texto.
        """
        self.setup_ui()
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        """
        Manipula o evento de fechamento da janela.
        """
        self.running = False
        self.root.destroy()
