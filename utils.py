"""
utils.py — Funções utilitárias do PDF Generator
------------------------------------------------
Contém funções auxiliares reutilizáveis em todo o projeto:
  - Limpeza de strings
  - Conversão de títulos em nomes de arquivo
  - Impressão de mensagens coloridas no terminal
  - Validação básica de dados
"""

import re
import unicodedata
from datetime import datetime


# ── Cores ANSI para o terminal ──────────────────────────────────────────────
# Esses códigos especiais colorem o texto no terminal Linux/macOS.
# "\033[" inicia um "escape sequence", o número define a cor, "m" fecha.
COLOR_RESET  = "\033[0m"
COLOR_INFO   = "\033[94m"   # Azul
COLOR_OK     = "\033[92m"   # Verde
COLOR_WARN   = "\033[93m"   # Amarelo
COLOR_ERROR  = "\033[91m"   # Vermelho


def log_info(mensagem: str) -> None:
    """Exibe uma mensagem informativa azul no terminal."""
    print(f"{COLOR_INFO}[INFO]{COLOR_RESET} {mensagem}")


def log_ok(mensagem: str) -> None:
    """Exibe uma mensagem de sucesso verde no terminal."""
    print(f"{COLOR_OK}[SUCCESS]{COLOR_RESET} {mensagem}")


def log_warn(mensagem: str) -> None:
    """Exibe um aviso amarelo no terminal."""
    print(f"{COLOR_WARN}[AVISO]{COLOR_RESET} {mensagem}")


def log_erro(mensagem: str) -> None:
    """Exibe uma mensagem de erro vermelha no terminal."""
    print(f"{COLOR_ERROR}[ERRO]{COLOR_RESET} {mensagem}")


def remover_acentos(texto: str) -> str:
    """
    Remove acentos de uma string.

    Exemplo:
        'Relatório' → 'Relatorio'
        'Ação' → 'Acao'

    Como funciona:
        1. unicodedata.normalize('NFD', ...) decompõe cada letra acentuada
           em letra-base + acento separados (ex: 'é' → 'e' + acento agudo)
        2. O loop filtra apenas os caracteres que NÃO são acentos (categoria 'Mn')
    """
    nfd = unicodedata.normalize('NFD', texto)
    sem_acento = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return sem_acento


def titulo_para_nome_arquivo(titulo: str) -> str:
    """
    Converte um título legível em um nome de arquivo seguro.

    Exemplos:
        'Relatório de Vendas' → 'relatorio_de_vendas'
        'Análise #1 - Dados!' → 'analise_1_dados'

    Passos:
        1. Remove acentos
        2. Converte para minúsculas
        3. Substitui espaços e hífens por underscore
        4. Remove caracteres especiais (mantém apenas letras, números e _)
        5. Remove underscores duplicados
        6. Remove underscores no início/fim
    """
    nome = remover_acentos(titulo)
    nome = nome.lower()
    nome = re.sub(r'[\s\-]+', '_', nome)          # espaços/hífens → _
    nome = re.sub(r'[^\w]', '', nome)              # remove caracteres especiais
    nome = re.sub(r'_+', '_', nome)                # __ → _
    nome = nome.strip('_')                         # remove _ nas bordas
    return nome or "documento"                     # fallback se ficar vazio


def data_atual_formatada() -> str:
    """
    Retorna a data e hora atual formatada para o rodapé do PDF.

    Exemplo de retorno: 'Gerado em 24/06/2026 às 14:35'
    """
    agora = datetime.now()
    return agora.strftime("Gerado em %d/%m/%Y às %H:%M")


def validar_dados(dados: dict) -> list[str]:
    """
    Verifica se os campos obrigatórios estão presentes e não estão vazios.

    Recebe: dicionário com os dados parseados do .txt
    Retorna: lista de erros encontrados (lista vazia = tudo ok)

    Campos obrigatórios: TITULO, CONTEUDO
    Campos opcionais (apenas aviso): AUTOR, DATA, RESUMO, CONCLUSAO
    """
    erros = []
    avisos = []

    # Campos que PRECISAM estar presentes
    obrigatorios = ['TITULO', 'CONTEUDO']
    for campo in obrigatorios:
        if not dados.get(campo, '').strip():
            erros.append(f"Campo obrigatório ausente ou vazio: '{campo}'")

    # Campos recomendados (geram aviso, não erro)
    opcionais = ['AUTOR', 'DATA', 'RESUMO', 'CONCLUSAO']
    for campo in opcionais:
        if not dados.get(campo, '').strip():
            avisos.append(campo)

    # Exibe avisos mas não interrompe o programa
    if avisos:
        log_warn(f"Campos opcionais não preenchidos: {', '.join(avisos)}")
        log_warn("O PDF será gerado, mas esses campos aparecerão em branco.")

    return erros
