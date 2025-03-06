#!/usr/bin/env python3
"""
Cliente simples para a API da Anthropic usando requisições HTTP diretas.
"""

import requests
import json
import sys

class SimpleAnthropicClient:
    def __init__(self, api_key):
        """
        Inicializa o cliente simples da API da Anthropic.
        
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
            if response:
                print(f"Resposta da API: {response.text}")
            return "Não foi possível obter uma resposta. Verifique sua conexão ou chave de API."

def main():
    """
    Função principal para testar o cliente.
    """
    if len(sys.argv) < 2:
        print("Uso: python simple_anthropic_client.py <chave_api>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    client = SimpleAnthropicClient(api_key)
    
    print("Cliente simples da API da Anthropic")
    print("Digite 'sair' para encerrar")
    
    while True:
        prompt = input("\nPrompt: ")
        if prompt.lower() == "sair":
            break
        
        system_prompt = "Você é um assistente médico especializado."
        response = client.get_completion(prompt, system_prompt)
        
        print("\nResposta:")
        print(response)

if __name__ == "__main__":
    main() 