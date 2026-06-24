"""
parser.py — Leitor e Interpretador do arquivo .txt
----------------------------------------------------
Responsabilidade única: transformar o texto bruto do .txt
em um dicionário Python estruturado e limpo.

Fluxo:
  arquivo .txt  →  ler_arquivo()  →  texto bruto
  texto bruto   →  parsear_txt()  →  dicionário de dados
"""

from pathlib import Path
from utils import log_info, log_erro


# Campos reconhecidos pelo parser (ordem define prioridade de detecção)
# A chave é o prefixo no .txt, o valor é a chave no dicionário resultado.
CAMPOS_CONHECIDOS = {
    'TITULO':    'TITULO',
    'AUTOR':     'AUTOR',
    'DATA':      'DATA',
    'RESUMO':    'RESUMO',
    'CONTEUDO':  'CONTEUDO',
    'CONCLUSAO': 'CONCLUSAO',
}


def ler_arquivo(caminho_arquivo: str) -> str:
    """
    Lê o arquivo .txt e retorna seu conteúdo como string.

    Parâmetro:
        caminho_arquivo: caminho para o arquivo (ex: 'modelo.txt')

    Retorna:
        String com o conteúdo completo do arquivo

    Levanta:
        SystemExit se o arquivo não existir, estiver vazio, ou
        ocorrer erro de leitura — com mensagem amigável.
    """
    log_info("Lendo arquivo...")

    # pathlib.Path é a forma moderna de trabalhar com arquivos em Python.
    # É mais seguro e legível do que usar strings diretamente.
    caminho = Path(caminho_arquivo)

    # Verifica se o arquivo existe
    if not caminho.exists():
        log_erro(f"Arquivo não encontrado: '{caminho_arquivo}'")
        log_erro("Verifique se o caminho está correto e tente novamente.")
        raise SystemExit(1)

    # Verifica se é realmente um arquivo (não uma pasta)
    if not caminho.is_file():
        log_erro(f"'{caminho_arquivo}' não é um arquivo válido.")
        raise SystemExit(1)

    # Tenta ler o conteúdo
    try:
        # encoding='utf-8' garante suporte a acentos e caracteres especiais
        # errors='ignore' evita crash em caracteres incomuns
        conteudo = caminho.read_text(encoding='utf-8', errors='ignore')
    except PermissionError:
        log_erro(f"Sem permissão para ler '{caminho_arquivo}'.")
        log_erro("Tente: chmod +r modelo.txt")
        raise SystemExit(1)
    except Exception as e:
        log_erro(f"Erro inesperado ao ler o arquivo: {e}")
        raise SystemExit(1)

    # Verifica se o arquivo tem conteúdo
    if not conteudo.strip():
        log_erro(f"O arquivo '{caminho_arquivo}' está vazio.")
        log_erro("Preencha o modelo antes de executar o programa.")
        raise SystemExit(1)

    return conteudo


def parsear_txt(conteudo: str) -> dict:
    """
    Interpreta o conteúdo do arquivo .txt e retorna um dicionário.

    Como funciona o algoritmo (linha por linha):

    O arquivo .txt tem dois tipos de campos:
      1. Campo de uma linha:  TITULO: Relatório de Vendas
      2. Campo multilinha:    RESUMO:
                              Linha 1 do resumo
                              Linha 2 do resumo

    O parser usa uma "máquina de estados":
      - campo_atual: qual campo estamos lendo agora (ex: 'RESUMO')
      - linhas_campo: acumula as linhas do campo atual

    Para cada linha do arquivo:
      - Se for um comentário (#) → ignora
      - Se reconhecer "CAMPO: valor" → muda de campo
      - Caso contrário → adiciona à lista do campo atual

    Parâmetro:
        conteudo: string com o texto bruto do arquivo

    Retorna:
        Dicionário com chaves: TITULO, AUTOR, DATA, RESUMO, CONTEUDO, CONCLUSAO
        Valores ausentes ficam como string vazia ''
    """
    log_info("Interpretando conteúdo...")

    # Inicializa o dicionário com todos os campos como string vazia.
    # Isso evita KeyError se algum campo não existir no .txt.
    dados: dict = {campo: '' for campo in CAMPOS_CONHECIDOS.values()}

    # Estado da máquina: qual campo estamos lendo agora
    campo_atual = None

    # Acumula as linhas do campo multilinha em curso
    linhas_campo: list[str] = []

    def salvar_campo_atual():
        """
        Função auxiliar interna: salva as linhas acumuladas no dicionário.
        Usamos .strip() para remover espaços e quebras de linha extras.
        """
        if campo_atual is not None:
            texto = '\n'.join(linhas_campo).strip()
            dados[campo_atual] = texto

    # Divide o conteúdo em linhas e processa uma por uma
    for linha in conteudo.splitlines():

        # Remove espaços no início e fim da linha
        linha_limpa = linha.strip()

        # Ignora linhas em branco e comentários (começam com #)
        if not linha_limpa or linha_limpa.startswith('#'):
            # Se estamos dentro de um campo multilinha, preserva a linha vazia
            # para manter a formatação dos parágrafos do usuário
            if campo_atual and not linha_limpa.startswith('#'):
                linhas_campo.append('')
            continue

        # Verifica se a linha começa com algum dos campos conhecidos
        # Exemplo: "RESUMO:" ou "RESUMO: texto na mesma linha"
        campo_detectado = None
        for prefixo, chave in CAMPOS_CONHECIDOS.items():
            # Testa se a linha começa com "CAMPO:" (case-insensitive)
            if linha_limpa.upper().startswith(prefixo + ':'):
                campo_detectado = chave

                # Extrai o valor que vem depois do ":"
                # Ex: "TITULO: Relatório" → valor = "Relatório"
                partes = linha_limpa.split(':', 1)
                valor_inline = partes[1].strip() if len(partes) > 1 else ''

                # Antes de mudar de campo, salva o campo anterior
                salvar_campo_atual()

                # Atualiza o estado: agora estamos lendo este novo campo
                campo_atual = chave
                linhas_campo = [valor_inline] if valor_inline else []
                break

        # Se não detectou nenhum campo, é continuação do campo atual
        if campo_detectado is None and campo_atual is not None:
            linhas_campo.append(linha_limpa)

    # Ao terminar o arquivo, salva o último campo que estava sendo lido
    salvar_campo_atual()

    return dados
