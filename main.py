#!/usr/bin/env python3
"""
main.py — Ponto de Entrada do PDF Generator
---------------------------------------------
Este é o arquivo que o usuário executa: python3 main.py modelo.txt

Responsabilidades:
  1. Receber argumentos da linha de comando (argparse)
  2. Orquestrar o fluxo: ler → parsear → validar → gerar
  3. Exibir mensagens amigáveis para o usuário

Fluxo completo:
  terminal → main.py → parser.py → gerador.py → output/arquivo.pdf
"""

import sys
import argparse
from pathlib import Path

# Importa os módulos do nosso projeto
from parser import ler_arquivo, parsear_txt
from gerador import gerar_pdf
from utils import (
    log_info, log_ok, log_erro,
    titulo_para_nome_arquivo,
    validar_dados,
)


# ── Versão do programa ───────────────────────────────────────────────────────
VERSAO = "1.0.0"

# ── Diretório de saída padrão ────────────────────────────────────────────────
# Path(__file__) → caminho deste arquivo (main.py)
# .parent → diretório onde main.py está
# / 'output' → subdiretório 'output' dentro do projeto
DIR_SAIDA = Path(__file__).parent / 'output'


def criar_parser_argumentos() -> argparse.ArgumentParser:
    """
    Configura o parser de argumentos da linha de comando.

    argparse é a biblioteca padrão do Python para isso.
    Ele lida automaticamente com:
      - --help / -h (mostra uso e sai)
      - --version (mostra versão e sai)
      - Mensagens de erro quando argumentos obrigatórios faltam
    """
    parser = argparse.ArgumentParser(
        prog='pdf-generator',
        description=(
            '📄 PDF Generator — Cria PDFs profissionais a partir de arquivos .txt\n'
            'Preencha o modelo.txt e execute: python3 main.py modelo.txt'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Exemplos de uso:\n'
            '  python3 main.py modelo.txt\n'
            '  python3 main.py relatorio.txt --saida meus_pdfs/\n'
            '  python3 main.py modelo.txt --nome meu_relatorio\n'
        )
    )

    # Argumento posicional (obrigatório): o arquivo .txt de entrada
    parser.add_argument(
        'arquivo',
        metavar='ARQUIVO.txt',
        help='Caminho para o arquivo .txt com o conteúdo do documento',
    )

    # Argumento opcional: diretório de saída
    parser.add_argument(
        '--saida', '-s',
        metavar='DIRETORIO',
        default=str(DIR_SAIDA),
        help=f'Diretório onde o PDF será salvo (padrão: {DIR_SAIDA})',
    )

    # Argumento opcional: nome personalizado para o PDF
    parser.add_argument(
        '--nome', '-n',
        metavar='NOME',
        default=None,
        help='Nome do arquivo PDF (sem extensão). Padrão: gerado a partir do TITULO',
    )

    # Argumento de versão
    parser.add_argument(
        '--versao', '-v',
        action='version',
        version=f'PDF Generator v{VERSAO}',
    )

    return parser


def determinar_nome_pdf(dados: dict, nome_manual: str | None) -> str:
    """
    Decide o nome do arquivo PDF final.

    Prioridade:
      1. Nome passado via --nome (se fornecido)
      2. Nome gerado a partir do TITULO do documento
      3. 'documento' (fallback se não houver título)

    Exemplos:
      --nome relatorio_final       → relatorio_final.pdf
      TITULO: Análise de Mercado   → analise_de_mercado.pdf
      (sem título)                 → documento.pdf
    """
    if nome_manual:
        # Remove .pdf se o usuário acidentalmente colocou a extensão
        nome = nome_manual.removesuffix('.pdf')
        return nome

    titulo = dados.get('TITULO', '')
    if titulo:
        return titulo_para_nome_arquivo(titulo)

    return 'documento'


def main():
    """
    Função principal — orquestra todo o fluxo do programa.
    """
    # ── Parse dos argumentos ─────────────────────────────────────────────────
    parser = criar_parser_argumentos()
    args = parser.parse_args()

    print()  # linha em branco para separar do prompt do terminal
    print("=" * 55)
    print(f"  📄 PDF Generator v{VERSAO}")
    print("=" * 55)
    print()

    # ── Passo 1: Ler o arquivo .txt ──────────────────────────────────────────
    conteudo_bruto = ler_arquivo(args.arquivo)

    # ── Passo 2: Parsear o conteúdo ──────────────────────────────────────────
    dados = parsear_txt(conteudo_bruto)

    # ── Passo 3: Validar os dados ────────────────────────────────────────────
    log_info("Validando campos...")
    erros = validar_dados(dados)

    if erros:
        print()
        log_erro("Não foi possível gerar o PDF. Corrija os erros abaixo:")
        for erro in erros:
            print(f"  ✗ {erro}")
        print()
        log_erro(f"Edite o arquivo '{args.arquivo}' e tente novamente.")
        sys.exit(1)

    # ── Passo 4: Determinar o nome e caminho do PDF ──────────────────────────
    nome_pdf = determinar_nome_pdf(dados, args.nome)
    caminho_saida = Path(args.saida) / f"{nome_pdf}.pdf"

    # ── Passo 5: Gerar o PDF ─────────────────────────────────────────────────
    caminho_final = gerar_pdf(dados, str(caminho_saida))

    # ── Sucesso! ─────────────────────────────────────────────────────────────
    print()
    log_ok(f"PDF criado com sucesso!")
    print(f"  📁 {caminho_final}")
    print()


# ── Proteção do ponto de entrada ─────────────────────────────────────────────
# Este bloco garante que main() só seja chamado quando o arquivo for
# executado diretamente (python3 main.py), não quando for importado
# por outro módulo Python.
if __name__ == '__main__':
    main()
