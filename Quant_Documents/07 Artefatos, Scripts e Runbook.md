---
tags: [runbook, artefatos, comandos]
atualizado: 2026-08-14
---

# Artefatos, Scripts e Runbook

Volta para [[00 MOC - Desafio Quant AI 2026]].

## Onde está cada coisa

### No repositório (`repo/`)

```
research/experiments/RSR_001/
  spec.md          especificação congelada, zero TBD
  decision.md      13 aprovações humanas, todas marcadas
  results.md       research sample completo; OOS a transcrever
  manifest.toml    status FROZEN, git_commit = H1

scripts/
  rsr_001.py                        implementação canônica do RSR_001
  robustez_residual_momentum.py     script anterior, superseded
  grafico_ic.py                     gera o gráfico de IC no estilo do relatório
  verify_research.py                verificador do harness (do parceiro)

notebooks/
  01_er_feasibility_v0_1..v0_5_1.ipynb    trabalho original do parceiro
  reconciliacao_residual_momentum.ipynb   reconciliação entre implementações

contexts/research/experiment_registry.md  índice canônico, 8 entradas
data/raw/us_sector_etfs_plus_spy_adjusted_close.csv   dados, 2000-01 a 2026-08
```

### Na pasta do projeto (fora do repo)

```
EPSILON_relatorio_final.pdf         5 páginas, 16:9, a reescrever
EPSILON_relatorio_fonte.html        fonte do PDF, editável
Blueprint_Relatorio_Final_Quant_AI.pdf   plano página a página
Retorno_*.md                        os 6 retornos técnicos trocados com o Codex
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

O fonte é HTML renderizado com WeasyPrint.

```bash
python -c "from weasyprint import HTML; HTML('EPSILON_relatorio_fonte.html').write_pdf('EPSILON_relatorio_final.pdf')"
```

Também abre no navegador e imprime para PDF, já que o `@page` está configurado para 16:9.

### Limpar metadados antes de enviar

```python
from pypdf import PdfReader, PdfWriter
r = PdfReader("EPSILON_relatorio_final.pdf"); w = PdfWriter()
for p in r.pages: w.add_page(p)
w.add_metadata({})
with open("AABC.pdf", "wb") as f: w.write(f)   # use a chave de envio real
print(PdfReader("AABC.pdf").metadata)
print("paginas:", len(PdfReader("AABC.pdf").pages))
```

## Git

Branch de trabalho: `relatorio-epsilon`.

> [!note] Aviso de CRLF é normal
> `LF will be replaced by CRLF` aparece sempre. É o `core.autocrlf` do Windows e não corrompe nada.

> [!warning] Não rodar git do sandbox de IA
> Acessar o repo clonado no OneDrive a partir de um ambiente Linux faz o git ver todos os arquivos como modificados (CRLF) e deixa `.git/index.lock` preso. Aconteceu uma vez e travou o commit. Rodar git sempre no Git Bash da máquina.

## Bug conhecido e aberto

`scripts/rsr_001.py`, linha da persistência:

```python
oos.drop(columns="long").to_csv(...)   # KeyError: coluna não existe mais
```

A refatoração para pesos removeu a coluna `long`. Correção: trocar por

```python
oos[["ic", "spread", "turnover", "custo", "liquido"]].to_csv(...)
```

**Não aplicar e reexecutar sem a decisão de governança.** Ver [[01 Estado Atual e Proximos Passos]].
