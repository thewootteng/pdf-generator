# 📄 PDF Generator

Ferramenta de linha de comando para gerar PDFs profissionais a partir de arquivos `.txt` simples. Desenvolvida em Python 3 com ReportLab.

---

## 📋 Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Usar](#como-usar)
- [Formato do Arquivo TXT](#formato-do-arquivo-txt)
- [Argumentos Disponíveis](#argumentos-disponíveis)
- [Personalização](#personalização)
- [Adicionando Novos Campos](#adicionando-novos-campos)
- [Solução de Problemas](#solução-de-problemas)

---

## Requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes do Python)
- Sistema Linux (testado no Kali Linux)

---

## Instalação

**1. Clone ou baixe o projeto:**
```bash
git clone https://github.com/seu-usuario/pdf-generator.git
cd pdf-generator
```

**2. (Opcional) Crie um ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install reportlab
```

**4. Verifique a instalação:**
```bash
python3 -c "import reportlab; print('ReportLab OK:', reportlab.Version)"
```

---

## Estrutura do Projeto

```
pdf-generator/
│
├── main.py           # Ponto de entrada — execute este arquivo
├── parser.py         # Lê e interpreta o arquivo .txt
├── gerador.py        # Gera o PDF usando os dados do parser
├── utils.py          # Funções auxiliares (cores, nomes, validação)
├── modelo.txt        # Modelo de documento para o usuário preencher
│
├── templates/
│   ├── __init__.py   # Marca como pacote Python
│   └── layout.py     # Define o visual: cores, fontes, estilos
│
├── output/           # PDFs gerados ficam aqui (criado automaticamente)
│
└── README.md         # Esta documentação
```

### Função de cada arquivo

| Arquivo | Responsabilidade |
|---------|-----------------|
| `main.py` | Recebe os argumentos do terminal, orquestra o fluxo completo |
| `parser.py` | Lê o `.txt` e transforma em dicionário Python |
| `gerador.py` | Usa os dados e o layout para criar o arquivo `.pdf` |
| `utils.py` | Funções utilitárias: mensagens coloridas, conversão de nomes |
| `templates/layout.py` | Define cores, fontes, estilos e estrutura visual |

---

## Como Usar

**Uso básico:**
```bash
python3 main.py modelo.txt
```

**Especificando a pasta de saída:**
```bash
python3 main.py modelo.txt --saida ~/Documentos/pdfs/
```

**Especificando o nome do arquivo:**
```bash
python3 main.py modelo.txt --nome relatorio_junho
```

**Ver ajuda:**
```bash
python3 main.py --help
```

**Ver versão:**
```bash
python3 main.py --versao
```

### Saída esperada no terminal

```
=======================================================
  📄 PDF Generator v1.0.0
=======================================================

[INFO] Lendo arquivo...
[INFO] Interpretando conteúdo...
[INFO] Validando campos...
[INFO] Gerando PDF...

[SUCCESS] PDF criado com sucesso!
  📁 output/relatorio_de_vendas.pdf
```

---

## Formato do Arquivo TXT

O arquivo `.txt` usa um formato simples de `CAMPO: valor`.

```
# Linhas começando com # são comentários — serão ignoradas

TITULO: Relatório de Vendas

AUTOR: Rick Feisa

DATA: 24/06/2026

RESUMO:
Texto do resumo aqui.
Pode ter múltiplas linhas.

CONTEUDO:
Conteúdo principal do documento.

Parágrafos são separados por uma linha em branco.

CONCLUSAO:
Texto da conclusão aqui.
```

### Regras do formato

| Regra | Detalhe |
|-------|---------|
| Campos obrigatórios | `TITULO` e `CONTEUDO` |
| Campos opcionais | `AUTOR`, `DATA`, `RESUMO`, `CONCLUSAO` |
| Comentários | Linhas que começam com `#` são ignoradas |
| Campos ausentes | O programa continua, o campo fica em branco |
| Parágrafos | Separados por uma linha em branco |
| Acentos | Totalmente suportados (UTF-8) |

### Nome automático do PDF

O nome do arquivo é gerado automaticamente a partir do `TITULO`:

| TITULO no .txt | Nome do PDF |
|----------------|-------------|
| `Relatório de Vendas` | `relatorio_de_vendas.pdf` |
| `Análise #1 - Dados!` | `analise_1_dados.pdf` |
| `(sem título)` | `documento.pdf` |

---

## Argumentos Disponíveis

| Argumento | Atalho | Padrão | Descrição |
|-----------|--------|--------|-----------|
| `arquivo` | — | (obrigatório) | Caminho para o arquivo .txt |
| `--saida` | `-s` | `output/` | Diretório de saída |
| `--nome` | `-n` | (do título) | Nome do arquivo PDF |
| `--versao` | `-v` | — | Exibe a versão |
| `--help` | `-h` | — | Exibe ajuda |

---

## Personalização

Toda a aparência do PDF está em `templates/layout.py`.

### Mudando as cores

No início do arquivo, localize a seção `PALETA DE CORES`:

```python
COR_PRIMARIA    = HexColor('#1a1a2e')   # fundo do cabeçalho
COR_ACENTO      = HexColor('#e94560')   # rótulos de seção e linha decorativa
COR_DESTAQUE    = HexColor('#0f3460')   # títulos de seção
COR_TEXTO       = HexColor('#2c2c2c')   # texto principal
```

Substitua os códigos hex pelas cores da sua preferência. Use [coolors.co](https://coolors.co) para criar paletas.

### Mudando as fontes

Nas funções `criar_estilos()`, altere o parâmetro `fontName`:

```python
# Opções disponíveis sem instalação extra:
# Helvetica, Helvetica-Bold, Helvetica-Oblique
# Times-Roman, Times-Bold, Times-Italic
# Courier, Courier-Bold

estilos['corpo'] = ParagraphStyle(
    fontName='Times-Roman',   # ← troque aqui
    fontSize=11,
    ...
)
```

### Mudando o tamanho da fonte

```python
estilos['titulo'] = ParagraphStyle(
    fontSize=26,   # ← troque aqui (em pontos tipográficos)
    ...
)
```

### Mudando as margens

Em `gerador.py`, na função `gerar_pdf()`:

```python
doc = SimpleDocTemplate(
    leftMargin=2 * cm,     # margem esquerda
    rightMargin=2 * cm,    # margem direita
    topMargin=2 * cm,      # margem superior
    bottomMargin=2.5 * cm, # margem inferior
)
```

---

## Adicionando Novos Campos

Para adicionar um campo como `EMPRESA:`, siga estes 3 passos:

**Passo 1 — Registre o campo em `parser.py`:**
```python
CAMPOS_CONHECIDOS = {
    'TITULO':    'TITULO',
    'AUTOR':     'AUTOR',
    'EMPRESA':   'EMPRESA',   # ← adicione aqui
    ...
}
```

**Passo 2 — Use o campo em `gerador.py`:**
```python
def montar_story(dados, estilos):
    ...
    empresa = dados.get('EMPRESA', '')
    if empresa.strip():
        story.extend(construir_secao(
            rotulo='SOBRE A EMPRESA',
            titulo='Empresa',
            conteudo=empresa,
            estilos=estilos,
        ))
```

**Passo 3 — Adicione ao modelo.txt:**
```
EMPRESA:
Descrição da empresa aqui.
```

Pronto! O novo campo será reconhecido e exibido no PDF.

---

## Solução de Problemas

**"Arquivo não encontrado"**
```bash
# Verifique se você está no diretório certo
ls -la modelo.txt

# Use o caminho completo se necessário
python3 main.py /caminho/completo/modelo.txt
```

**"Sem permissão para ler"**
```bash
chmod +r modelo.txt
```

**"Sem permissão para escrever"**
```bash
chmod +w output/
# ou especifique outro diretório
python3 main.py modelo.txt --saida /tmp/
```

**Caracteres estranhos no PDF**
```
Salve o arquivo .txt em UTF-8.
No nano: use Ctrl+O → Enter (já salva em UTF-8)
No VS Code: verifique o canto inferior direito da janela
```

**ImportError: No module named 'reportlab'**
```bash
pip install reportlab
# ou
pip3 install reportlab
```

---

## Licença

MIT — livre para usar, modificar e distribuir.
