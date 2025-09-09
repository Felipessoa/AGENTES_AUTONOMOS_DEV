import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def configurar_cliente():
    """Configura e retorna o cliente da API Gemini."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("A variável de ambiente GEMINI_API_KEY não foi encontrada.")
        
        genai.configure(api_key=api_key)
        return genai
    except Exception as e:
        print(f"Erro ao configurar o cliente: {e}")
        return None

def gerar_conteudo(cliente_genai, prompt_usuario: str):
    """
    Gera conteúdo usando o modelo Gemini em modo streaming.
    
    Args:
        cliente_genai: O cliente genai configurado.
        prompt_usuario: O texto de entrada do usuário.
    """
    if not cliente_genai:
        print("Cliente não configurado. Abortando a geração.")
        return

    # Modelo atualizado para um disponível e poderoso
    model_name = "gemini-2.5-pro" 
    
    print(f"--- Usando o modelo: {model_name} ---")
    print(f"--- Prompt: {prompt_usuario} ---\n")
    
    model = cliente_genai.GenerativeModel(model_name)

    # Configurações de geração
    generation_config = types.GenerationConfig(
        temperature=0.5, # Um pouco mais de criatividade
    )

    try:
        # Usando o método mais simples e direto do SDK para streaming
        response_stream = model.generate_content(
            prompt_usuario,
            generation_config=generation_config,
            stream=True
        )

        print("Resposta do Gemini:\n")
        # Itera sobre os chunks da resposta em streaming
        for chunk in response_stream:
            # O 'end=""' evita que o print crie uma nova linha a cada chunk
            print(chunk.text, end="", flush=True) 
        
        print("\n\n--- Fim da Geração ---")

    except Exception as e:
        print(f"\nOcorreu um erro durante a geração de conteúdo: {e}")


if __name__ == "__main__":
    # 1. Configura o cliente
    cliente = configurar_cliente()

    # 2. Define o prompt
    meu_prompt = "Explique o que é um ambiente virtual em Python e por que é uma boa prática usá-lo, como se estivesse falando com um desenvolvedor júnior."
    
    # 3. Chama a função para gerar o conteúdo
    gerar_conteudo(cliente, meu_prompt)