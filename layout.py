"""
templates/layout.py — Layout Visual do PDF
--------------------------------------------
Define toda a aparência do PDF: cores, fontes, estilos e estrutura.

Este arquivo é o "designer" do projeto. Aqui você pode personalizar:
  - Paleta de cores
  - Tamanhos de fonte
  - Espaçamentos
  - Elementos gráficos (linhas, retângulos)

Tecnologia: ReportLab Platypus (sistema de "peças" que compõem o PDF)
  - Paragraph: bloco de texto com estilo
  - Spacer: espaço vazio (equivale a uma linha em branco)
  - HRFlowable: linha horizontal decorativa
  - Table: tabela (usamos para o cabeçalho colorido)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, PageBreak
)
from reportlab.lib.colors import HexColor


# ══════════════════════════════════════════════════════════════════
#  PALETA DE CORES
#  Para personalizar: troque os códigos hex pelas suas cores.
#  Use um site como https://coolors.co para criar paletas.
# ══════════════════════════════════════════════════════════════════

COR_PRIMARIA    = HexColor('#1a1a2e')   # Azul-marinho escuro (cabeçalho)
COR_SECUNDARIA  = HexColor('#16213e')   # Azul-marinho médio
COR_DESTAQUE    = HexColor('#0f3460')   # Azul para títulos
COR_ACENTO      = HexColor('#e94560')   # Vermelho/rosa para detalhes
COR_TEXTO       = HexColor('#2c2c2c')   # Cinza escuro (texto principal)
COR_TEXTO_CLARO = HexColor('#6c757d')   # Cinza médio (metadados)
COR_FUNDO_SECAO = HexColor('#f0f4f8')   # Cinza azulado claro (fundo de seções)
COR_BRANCO      = colors.white


# ══════════════════════════════════════════════════════════════════
#  ESTILOS DE PARÁGRAFO
#  ParagraphStyle define como cada tipo de texto será renderizado.
#  Parâmetros principais:
#    fontName: nome da fonte (fontes built-in do ReportLab)
#    fontSize: tamanho em pontos
#    leading: altura da linha (espaçamento entre linhas)
#    textColor: cor do texto
#    alignment: alinhamento (TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY)
#    spaceBefore/spaceAfter: espaço antes/depois do parágrafo (em pontos)
# ══════════════════════════════════════════════════════════════════

def criar_estilos() -> dict:
    """
    Cria e retorna um dicionário com todos os estilos usados no PDF.

    Fontes built-in disponíveis no ReportLab (sem instalação extra):
      Helvetica, Helvetica-Bold, Helvetica-Oblique, Helvetica-BoldOblique
      Times-Roman, Times-Bold, Times-Italic, Times-BoldItalic
      Courier, Courier-Bold, Courier-Oblique, Courier-BoldOblique
    """
    estilos = {}

    # ── Título do documento (grande e centralizado) ──────────────────────
    estilos['titulo'] = ParagraphStyle(
        name='Titulo',
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,                  # altura da linha
        textColor=COR_BRANCO,        # texto branco (sobre fundo escuro)
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    # ── Subtítulo (autor + data no cabeçalho) ────────────────────────────
    estilos['subtitulo'] = ParagraphStyle(
        name='Subtitulo',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=HexColor('#b0c4de'),  # azul claro
        alignment=TA_CENTER,
    )

    # ── Rótulo de seção (ex: "RESUMO", "CONTEÚDO") ──────────────────────
    estilos['rotulo_secao'] = ParagraphStyle(
        name='RotuloSecao',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=COR_ACENTO,          # vermelho/rosa
        spaceBefore=16,
        spaceAfter=4,
        # letterSpacing: espaçamento entre letras (efeito "tracking")
        # Não disponível diretamente no ParagraphStyle — usamos tags XML
    )

    # ── Título de seção (ex: "Resumo Executivo") ─────────────────────────
    estilos['titulo_secao'] = ParagraphStyle(
        name='TituloSecao',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=COR_DESTAQUE,
        spaceBefore=6,
        spaceAfter=8,
    )

    # ── Texto do corpo principal ─────────────────────────────────────────
    estilos['corpo'] = ParagraphStyle(
        name='Corpo',
        fontName='Times-Roman',
        fontSize=11,
        leading=18,                   # leading generoso = texto mais legível
        textColor=COR_TEXTO,
        alignment=TA_JUSTIFY,         # justificado = visual mais profissional
        spaceAfter=8,
        firstLineIndent=18,           # recuo na primeira linha de cada parágrafo
    )

    # ── Texto de metadados (rodapé, datas) ──────────────────────────────
    estilos['meta'] = ParagraphStyle(
        name='Meta',
        fontName='Helvetica',
        fontSize=8,
        leading=12,
        textColor=COR_TEXTO_CLARO,
        alignment=TA_CENTER,
    )

    # ── Texto de rodapé com número de página ────────────────────────────
    estilos['rodape'] = ParagraphStyle(
        name='Rodape',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=COR_TEXTO_CLARO,
    )

    return estilos


# ══════════════════════════════════════════════════════════════════
#  FUNÇÕES DE CABEÇALHO E RODAPÉ
#  Essas funções são chamadas pelo ReportLab em CADA página.
#  São registradas via doc.build(story, onFirstPage=..., onLaterPages=...)
# ══════════════════════════════════════════════════════════════════

def _desenhar_rodape(canvas, doc, data_geracao: str):
    """
    Desenha o rodapé em todas as páginas.
    O ReportLab passa canvas (área de desenho) e doc (documento).
    """
    # Salva o estado gráfico atual (para não afetar o resto da página)
    canvas.saveState()

    largura, altura = A4
    margem = 2 * cm

    # Linha decorativa acima do rodapé
    canvas.setStrokeColor(HexColor('#dee2e6'))
    canvas.setLineWidth(0.5)
    canvas.line(margem, 1.5 * cm, largura - margem, 1.5 * cm)

    # Número da página (lado direito)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(COR_TEXTO_CLARO)
    numero_pagina = f"Página {doc.page}"
    canvas.drawRightString(largura - margem, 1.1 * cm, numero_pagina)

    # Data de geração (lado esquerdo)
    canvas.drawString(margem, 1.1 * cm, data_geracao)

    # Restaura o estado gráfico
    canvas.restoreState()


def criar_callbacks_pagina(data_geracao: str):
    """
    Retorna as funções de callback para cabeçalho/rodapé.
    Usamos closure (função dentro de função) para passar
    a data_geracao sem usar variável global.
    """
    def primeira_pagina(canvas, doc):
        _desenhar_rodape(canvas, doc, data_geracao)

    def paginas_seguintes(canvas, doc):
        _desenhar_rodape(canvas, doc, data_geracao)

    return primeira_pagina, paginas_seguintes


# ══════════════════════════════════════════════════════════════════
#  CONSTRUÇÃO DO CABEÇALHO (bloco visual no topo da 1ª página)
# ══════════════════════════════════════════════════════════════════

def construir_cabecalho(dados: dict, estilos: dict) -> list:
    """
    Constrói o bloco de cabeçalho do PDF usando uma Table do ReportLab.

    Por que usar Table para um bloco simples?
    → Tables permitem aplicar cor de fundo, bordas e padding facilmente.
    → É a forma mais prática de criar "caixas coloridas" com texto.

    Retorna: lista de elementos Platypus (adicionados ao story)
    """
    elementos = []

    titulo = dados.get('TITULO', 'Documento') or 'Documento'
    autor  = dados.get('AUTOR', '')
    data   = dados.get('DATA', '')

    # Monta a linha de metadados (autor | data)
    meta_partes = []
    if autor:
        meta_partes.append(f"Autor: {autor}")
    if data:
        meta_partes.append(f"Data: {data}")
    meta_texto = "   ·   ".join(meta_partes) if meta_partes else ""

    # Conteúdo interno da tabela (células)
    conteudo_cabecalho = [
        [Paragraph(titulo, estilos['titulo'])],
    ]
    if meta_texto:
        conteudo_cabecalho.append([Paragraph(meta_texto, estilos['subtitulo'])])

    # Cria a tabela com largura total da área de impressão
    largura_util = A4[0] - 4 * cm   # largura A4 menos as margens
    tabela = Table(conteudo_cabecalho, colWidths=[largura_util])

    # Aplica estilo visual à tabela
    tabela.setStyle(TableStyle([
        # Cor de fundo do cabeçalho
        ('BACKGROUND', (0, 0), (-1, -1), COR_PRIMARIA),
        # Padding interno (cima, baixo, esquerda, direita)
        ('TOPPADDING',    (0, 0), (-1, -1), 28),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 28),
        ('LEFTPADDING',   (0, 0), (-1, -1), 20),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 20),
        # Arredondamento das bordas
        ('ROUNDEDCORNERS', [8]),
    ]))

    elementos.append(tabela)

    # Linha decorativa colorida abaixo do cabeçalho
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(HRFlowable(
        width="100%",
        thickness=3,
        color=COR_ACENTO,
        spaceAfter=0.5 * cm,
    ))

    return elementos


# ══════════════════════════════════════════════════════════════════
#  CONSTRUÇÃO DAS SEÇÕES DO CORPO
# ══════════════════════════════════════════════════════════════════

def construir_secao(rotulo: str, titulo: str, conteudo: str, estilos: dict) -> list:
    """
    Constrói uma seção do documento (ex: Resumo, Conteúdo, Conclusão).

    Estrutura visual de cada seção:
      [RÓTULO EM VERMELHO]
      Título da Seção
      ──────────────────  (linha fina)
      Texto do conteúdo...

    Parâmetros:
        rotulo:   texto pequeno acima do título (ex: "RESUMO EXECUTIVO")
        titulo:   título grande da seção (ex: "Resumo")
        conteudo: texto principal da seção
        estilos:  dicionário de estilos retornado por criar_estilos()

    Retorna: lista de elementos Platypus
    """
    elementos = []

    if not conteudo.strip():
        return elementos  # seção vazia → não renderiza nada

    # Rótulo pequeno (efeito "SECTION LABEL")
    elementos.append(
        Paragraph(f'<font color="{COR_ACENTO.hexval()}">{rotulo}</font>', estilos['rotulo_secao'])
    )

    # Título da seção
    elementos.append(Paragraph(titulo, estilos['titulo_secao']))

    # Linha fina abaixo do título
    elementos.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=HexColor('#dee2e6'),
        spaceAfter=0.3 * cm,
    ))

    # Quebra o conteúdo em parágrafos (separados por linha em branco no .txt)
    # Isso preserva a formatação que o usuário fez no arquivo.
    paragrafos = _dividir_em_paragrafos(conteudo)
    for paragrafo in paragrafos:
        if paragrafo.strip():
            # Escapa caracteres XML especiais para não quebrar o Paragraph
            texto_seguro = _escapar_xml(paragrafo)
            elementos.append(Paragraph(texto_seguro, estilos['corpo']))

    elementos.append(Spacer(1, 0.4 * cm))

    return elementos


def _dividir_em_paragrafos(texto: str) -> list[str]:
    """
    Divide um texto em parágrafos separados por linhas em branco.

    Exemplo:
        "Linha 1\\nLinha 2\\n\\nLinha 3" → ["Linha 1 Linha 2", "Linha 3"]
    """
    blocos = []
    bloco_atual = []

    for linha in texto.splitlines():
        if linha.strip():
            bloco_atual.append(linha.strip())
        else:
            if bloco_atual:
                blocos.append(' '.join(bloco_atual))
                bloco_atual = []

    if bloco_atual:
        blocos.append(' '.join(bloco_atual))

    return blocos if blocos else [texto]


def _escapar_xml(texto: str) -> str:
    """
    Substitui caracteres que têm significado especial em XML/HTML.
    O ReportLab usa XML internamente para formatar texto.

    Se não escaparmos esses caracteres, o Paragraph vai dar erro
    quando o texto do usuário contiver <, >, & ou aspas.
    """
    texto = texto.replace('&', '&amp;')    # & → &amp;   (DEVE ser primeiro!)
    texto = texto.replace('<', '&lt;')     # < → &lt;
    texto = texto.replace('>', '&gt;')     # > → &gt;
    texto = texto.replace('"', '&quot;')   # " → &quot;
    return texto
