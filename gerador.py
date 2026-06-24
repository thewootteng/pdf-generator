"""
gerador.py — Motor de Geração do PDF
--------------------------------------
Responsabilidade: orquestrar a criação do PDF usando os dados
parseados e o layout definido em templates/layout.py.

Fluxo:
  dados (dict) → montar_story() → lista de elementos Platypus
  lista + caminho → gerar_pdf() → arquivo .pdf no disco
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer

from templates.layout import (
    criar_estilos,
    criar_callbacks_pagina,
    construir_cabecalho,
    construir_secao,
)
from utils import log_info, log_ok, log_erro, data_atual_formatada


def montar_story(dados: dict, estilos: dict) -> list:
    """
    Monta a lista de elementos Platypus que formam o PDF.

    No ReportLab Platypus, o documento é construído como uma
    lista de "flowables" (elementos que fluem pela página):
      - Paragraph: bloco de texto
      - Spacer: espaço em branco
      - HRFlowable: linha horizontal
      - Table: tabela
      - PageBreak: quebra de página forçada

    O ReportLab cuida automaticamente de:
      - Quebrar texto longo em múltiplas linhas
      - Criar novas páginas quando necessário
      - Aplicar estilos de forma consistente

    Parâmetros:
        dados:   dicionário retornado pelo parser
        estilos: dicionário retornado por criar_estilos()

    Retorna:
        Lista ordenada de elementos Platypus (o "story" do documento)
    """
    story = []

    # ── 1. Cabeçalho ────────────────────────────────────────────────────
    story.extend(construir_cabecalho(dados, estilos))
    story.append(Spacer(1, 0.6 * cm))

    # ── 2. Resumo ────────────────────────────────────────────────────────
    resumo = dados.get('RESUMO', '')
    if resumo.strip():
        story.extend(construir_secao(
            rotulo='RESUMO EXECUTIVO',
            titulo='Resumo',
            conteudo=resumo,
            estilos=estilos,
        ))
        story.append(Spacer(1, 0.3 * cm))

    # ── 3. Conteúdo Principal ────────────────────────────────────────────
    conteudo = dados.get('CONTEUDO', '')
    if conteudo.strip():
        story.extend(construir_secao(
            rotulo='CONTEÚDO PRINCIPAL',
            titulo='Conteúdo',
            conteudo=conteudo,
            estilos=estilos,
        ))
        story.append(Spacer(1, 0.3 * cm))

    # ── 4. Conclusão ─────────────────────────────────────────────────────
    conclusao = dados.get('CONCLUSAO', '')
    if conclusao.strip():
        story.extend(construir_secao(
            rotulo='CONSIDERAÇÕES FINAIS',
            titulo='Conclusão',
            conteudo=conclusao,
            estilos=estilos,
        ))

    return story


def gerar_pdf(dados: dict, caminho_saida: str) -> str:
    """
    Gera o PDF completo a partir dos dados e salva no caminho especificado.

    Parâmetros:
        dados:         dicionário com os dados do documento
        caminho_saida: caminho completo onde o PDF será salvo

    Retorna:
        String com o caminho do PDF gerado

    Levanta:
        SystemExit em caso de erro de escrita
    """
    log_info("Gerando PDF...")

    # Garante que o diretório de saída existe
    # parents=True: cria subdiretórios intermediários se necessário
    # exist_ok=True: não dá erro se o diretório já existir
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)

    # Data de geração (usada no rodapé de todas as páginas)
    data_geracao = data_atual_formatada()

    # Cria o documento com configurações de página
    # SimpleDocTemplate: o tipo mais simples de documento Platypus
    # pagesize: tamanho da página (A4 = 210mm x 297mm)
    # margens: espaço nas bordas da página (leftMargin, rightMargin, etc.)
    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.5 * cm,       # maior embaixo para o rodapé
        title=dados.get('TITULO', 'Documento'),
        author=dados.get('AUTOR', ''),
        subject='Documento gerado pelo PDF Generator',
        creator='PDF Generator v1.0 — Python + ReportLab',
    )

    # Cria os estilos visuais
    estilos = criar_estilos()

    # Monta a lista de elementos (o "story")
    story = montar_story(dados, estilos)

    # Cria as funções de callback para cabeçalho/rodapé
    primeira_pag, proximas_pags = criar_callbacks_pagina(data_geracao)

    # Gera o PDF — este é o passo que realmente escreve o arquivo
    try:
        doc.build(
            story,
            onFirstPage=primeira_pag,    # função chamada na 1ª página
            onLaterPages=proximas_pags,  # função chamada nas demais páginas
        )
    except PermissionError:
        log_erro(f"Sem permissão para escrever em '{caminho_saida}'.")
        raise SystemExit(1)
    except Exception as e:
        log_erro(f"Erro ao gerar o PDF: {e}")
        raise SystemExit(1)

    return caminho_saida
