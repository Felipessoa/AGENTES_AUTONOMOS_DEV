def main():
    """
    Função principal que pede o nome do usuário e imprime uma saudação.
    """
    # Pede ao usuário para inserir seu nome e armazena na variável 'nome'
    nome = input("Por favor, digite seu nome: ")

    # Imprime a saudação personalizada usando uma f-string
    print(f"Olá, {nome}")

if __name__ == "__main__":
    # Garante que a função main() seja executada apenas quando o script é rodado diretamente
    main()
