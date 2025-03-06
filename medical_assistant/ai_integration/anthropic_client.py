import anthropic
import os

class AnthropicClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-opus-20240229"  # Podemos ajustar para outros modelos conforme necessário
        self.max_tokens = 1000
        self.medical_context = ""
    
    def set_medical_context(self, context):
        """
        Define o contexto médico extraído dos livros para ser usado nas consultas.
        """
        self.medical_context = context
    
    def get_completion(self, prompt, temperature=0.7):
        """
        Obtém uma resposta do modelo Claude baseada no prompt fornecido.
        """
        try:
            system_prompt = f"Você é um assistente médico especializado. Use o seguinte conhecimento médico como referência: {self.medical_context}"
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Erro ao comunicar com a API da Anthropic: {e}")
            return "Não foi possível obter uma resposta. Verifique sua conexão ou chave de API."
    
    def get_medical_suggestions(self, current_text, patient_context=""):
        """
        Gera sugestões médicas com base no texto atual e no contexto do paciente.
        """
        prompt = f"""
        Contexto do paciente: {patient_context}
        
        Texto atual: {current_text}
        
        Com base no texto atual e no contexto do paciente, forneça sugestões médicas relevantes 
        para continuar o texto. Considere diagnósticos possíveis, tratamentos recomendados, 
        exames adicionais ou observações importantes a serem incluídas.
        """
        return self.get_completion(prompt)
    
    def analyze_patient_data(self, patient_data):
        """
        Analisa dados do paciente para fornecer insights médicos.
        """
        prompt = f"""
        Analise os seguintes dados do paciente e forneça insights médicos relevantes:
        
        {patient_data}
        
        Considere possíveis diagnósticos, recomendações de tratamento, e quaisquer 
        sinais de alerta que devam ser investigados.
        """
        return self.get_completion(prompt)
