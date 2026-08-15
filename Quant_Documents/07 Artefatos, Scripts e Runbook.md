---
tags: [runbook, artefatos, comandos]
atualizado: 2026-08-15
---

# Artefatos, Scripts e Runbook

Volta para [[00 MOC - Desafio Quant AI 2026]].

## Onde está cada coisa

### No repositório (`repo/`)

```
research/experiments/RSR_001/
  spec.md          especificação congelada, zero TBD
  decision.md      13 aprovações humanas + decisão NO-GO registrada
  results.md       research sample e OOS, com proveniência da transcrição
  manifest.toml    status FINAL, oos_opened = true, git_commit = H1
  reauditoria.md   reauditoria estática de 15/08, 5 achados

scripts/
  rsr_001.py                        implementação canônica do RSR_001
  robustez_residual_momentum.py     script anterior, superseded
  grafico_ic.py                     gera o gráfico de IC no estilo do relatório
  verify_research.py                verificador do harness (do parceiro)

notebooks/
  01_er_feasibility_v0_1..v0_5_1.ipynb    trabalho original do parceiro
  reconciliacao_residual_momentum.ipynb   reconciliação entre implementações

reports/
  EPSILON_relatorio_final.pdf    entregável, 5 páginas, 960×540 pt
  EPSILON_relatorio_fonte.html   fonte do PDF, versionado junto
  rsr_001_oos_terminal.txt       VAZIO. Commitado assim de propósito, é o achado F1

contexts/research/experiment_registry.md  índice canônico, 8 entradas
data/raw/us_sector_etfs_plus_spy_adjusted_close.csv   dados, 2000-01 a 2026-08
```

### Na pasta do projeto (fora do repo)

```
EPSILON_relatorio_final.pdf         cópia de trabalho do entregável
EPSILON_relatorio_fonte.html        cópia de trabalho do fonte
Blueprint_Relatorio_Final_Quant_AI.pdf   plano página a página
Retorno_*.md                        os 6 retornos técnicos da frente de pesquisa
Diretrizes_Relatorio_Final_*.pdf    edital
Criterios_Avaliacao_Desafio.pdf     manual de avaliação
```

## Ambiente

Python **3.12.4** na máquina do João, chamado como `python` no Git Bash. O harness exige 3.11 ou superior por causa de `tomllib`.

```bash
python -m pip install -r requirements.txt pytest -q
```

> [!warning] pytest sem escopo falha
> `audit_bundle/tests/research/test_verify_research.py` colide com `tests/research/test_verify_research.py`. Colisão pré-existente, herdada do commit `v2`. Rode sempre com escopo:
> ```bash
> python -m pytest tests/ -q
> ```
> Se quiser resolver de vez, depois da entrega: `printf '[pytest]\nnorecursedirs = audit_bundle .venv\n' > pytest.ini`

## Comandos

### Verificação completa

```bash
python scripts/verify_research.py && python -m pytest tests/ -q && echo OK
```

### RSR_001

```bash
python scripts/rsr_001.py              # research sample apenas
python scripts/rsr_001.py --robustez   # + bateria, placebos e ablação
python scripts/rsr_001.py --ensaio     # exercita o critério no research, sem tocar OOS
python scripts/rsr_001.py --abrir-oos  # JÁ FOI EXECUTADO. Não rodar de novo sem decisão.
```

### Gráfico do relatório

```bash
python scripts/grafico_ic.py                  # research apenas
python scripts/grafico_ic.py --abrir-holdout  # inclui o OOS
```

Saída em `reports/ic_acumulado.svg`, no tamanho exato do espaço da página 4 (174mm × 70mm) e na paleta do relatório.

### Reconstruir o PDF

WeasyPrint **não está instalado nesta máquina**. A build atual usa Chrome headless, que respeita o `@page { size: 338.67mm 190.5mm }` e gera 960×540 pt exatos.

```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="bruto.pdf" --virtual-time-budget=6000 \
  "file:///C:/.../reports/EPSILON_relatorio_fonte.html"
```

As fontes DejaVu estão instaladas por usuário em `%LOCALAPPDATA%\Microsoft\Windows\Fonts`, e o Chrome as embute.

### Limpar metadados antes de enviar

Obrigatório: o Chrome grava `/Producer: Skia/PDF` e `/Creator` com o user-agent.

```python
from pypdf import PdfReader, PdfWriter
r = PdfReader("bruto.pdf"); w = PdfWriter()
for p in r.pages: w.add_page(p)
w.add_metadata({})                              # zera autor, título e datas
with open("AABC.pdf", "wb") as f: w.write(f)    # use a chave de envio real
```

### Conferência de eliminação

```python
import fitz
d = fitz.open("AABC.pdf")
print(d.page_count, d[0].rect)                  # 5, Rect(0,0,960,540) -> 16:9
print(d.metadata)                               # só /Producer: pypdf
t = "\n".join(p.get_text() for p in d)
for termo in ["Delta Vega", "github", "http", "universidade", "substituir", "preencher"]:
    assert termo.lower() not in t.lower(), termo
```

## Git

Branch final: `relatorio-final`, saída de `relatorio-epsilon` e pushada para o origin.

> [!note] Aviso de CRLF é normal
> `LF will be replaced by CRLF` aparece sempre. É o `core.autocrlf` do Windows e não corrompe nada.

> [!warning] Não rodar git do sandbox de IA
> Acessar o repo clonado no OneDrive a partir de um ambiente Linux faz o git ver todos os arquivos como modificados (CRLF) e deixa `.git/index.lock` preso. Aconteceu uma vez e travou o commit. Rodar git sempre no Git Bash da máquina.

## Bug conhecido, deixado aberto de propósito

`scripts/rsr_001.py:310`, linha da persistência:

```python
oos.drop(columns="long").to_csv(...)   # KeyError: coluna não existe mais
```

A refatoração para pesos removeu a coluna `long`. A correção seria

```python
oos[["ic", "spread", "turnover", "custo", "liquido"]].to_csv(...)
```

> [!danger] Não corrigir e não reexecutar
> A decisão de governança foi a **Opção B**: não reexecutar. Corrigir a linha só teria efeito acompanhado de reexecução, e reexecutar está vedado pela regra pré-registrada. O bug fica no código como registro do achado F4. Ver `research/experiments/RSR_001/reauditoria.md`.

Se algum dia o `RSR_001` for revisitado com **nova specification e novo freeze**, aí sim corrigir — junto de um `--ensaio` que exercite o caminho de gravação.
