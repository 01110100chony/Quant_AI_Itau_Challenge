#!/usr/bin/env python3
"""
grafico_ic.py

Gera o grafico de Information Coefficient acumulado do ROBO EPSILON, no mesmo
estilo visual do relatorio final, e imprime os numeros da faixa de metricas.

PROTOCOLO DE HOLDOUT
--------------------
Por padrao o script roda SOMENTE no research sample (2001 a 2018). O holdout
so e calculado com a flag --abrir-holdout, que deve ser usada UMA UNICA VEZ,
depois que a especificacao estiver congelada e commitada.

    python grafico_ic.py                    # research sample apenas
    python grafico_ic.py --abrir-holdout    # inclui 2018 a 2026

Saidas em reports/: ic_acumulado.svg (vetorial, para o relatorio),
ic_acumulado.png (300 dpi) e ic_metricas.csv.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

# --------------------------------------------------------------------------
# ESPECIFICACAO CONGELADA
# --------------------------------------------------------------------------
UNIVERSO   = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
MERCADO    = "SPY"
INICIO     = "2001-01-01"
FIM        = "2026-08-01"
CORTE_OOS  = "2018-01-01"     # fronteira research / holdout
JAN_BETA   = 252              # janela de estimacao do beta, em pregoes
LOOKBACK   = 252              # inicio da janela de momentum
GAP        = 21               # pula o mes mais recente -> "12 menos 1"

# Paleta identica a do relatorio
PAPEL   = "#F2EFE9"
TINTA   = "#1A1D21"
VERDE   = "#2C6E5D"
CINZA   = "#A39C8E"
AREIA   = "#E4DED2"
NEUTRO  = "#8A8478"
BORDA   = "#C4BDB0"


def espacado(texto: str) -> str:
    """Imita o letter-spacing do relatorio, que o matplotlib nao suporta."""
    return " ".join(texto)


# --------------------------------------------------------------------------
# DADOS
# --------------------------------------------------------------------------
def carregar_precos(cache: Path) -> pd.DataFrame:
    """Le o snapshot local se existir; caso contrario baixa e grava o snapshot."""
    if cache.exists():
        print(f"[dados] snapshot local: {cache}")
        return pd.read_csv(cache, index_col=0, parse_dates=True)

    import yfinance as yf
    print("[dados] baixando do Yahoo Finance")
    bruto = yf.download(
        UNIVERSO + [MERCADO], start=INICIO, end=FIM,
        auto_adjust=True, progress=False, threads=False,
    )
    precos = bruto["Close"] if isinstance(bruto.columns, pd.MultiIndex) else bruto
    precos = precos[UNIVERSO + [MERCADO]].dropna(how="all")

    cache.parent.mkdir(parents=True, exist_ok=True)
    precos.to_csv(cache)
    print(f"[dados] snapshot gravado em {cache}")
    return precos


def residualizar(ret: pd.DataFrame, ret_m: pd.Series) -> pd.DataFrame:
    """
    Resid. da regressao movel de cada ativo contra o mercado.

    Beta e alpha em t usam apenas a janela que TERMINA em t. Nenhum dado
    posterior entra na conta, o que elimina look-ahead na construcao do sinal.
    """
    var_m  = ret_m.rolling(JAN_BETA).var()
    med_m  = ret_m.rolling(JAN_BETA).mean()

    residuos = {}
    for tic in ret.columns:
        cov   = ret[tic].rolling(JAN_BETA).cov(ret_m)
        beta  = cov / var_m
        alpha = ret[tic].rolling(JAN_BETA).mean() - beta * med_m
        residuos[tic] = ret[tic] - alpha - beta * ret_m
    return pd.DataFrame(residuos)


def momentum(serie: pd.DataFrame, padronizar: bool = False) -> pd.DataFrame:
    """
    Soma acumulada de t-LOOKBACK ate t-GAP. Pula o mes mais recente.

    Com padronizar=True divide pelo desvio padrao da propria serie na janela,
    que e a definicao de Blitz, Huij e Martens (2011) para residual momentum.
    As duas variantes produzem resultados diferentes. Use --diagnostico para
    comparar contra o numero do seu notebook antes de fechar o relatorio.
    """
    janela = LOOKBACK - GAP
    acum = serie.rolling(janela).sum()
    if padronizar:
        acum = acum / serie.rolling(janela).std()
    return acum.shift(GAP)


def rank_ic(sinal_m: pd.DataFrame, fwd: pd.DataFrame) -> pd.Series:
    """
    Spearman cross-sectional entre o sinal em t e o retorno de t para t+1.

    Calculado como Pearson sobre os ranks, que e a definicao de Spearman.
    Evita a dependencia de scipy e mantem o script rodando so com
    pandas, numpy e matplotlib.
    """
    ics = {}
    for data in sinal_m.index:
        s, r = sinal_m.loc[data], fwd.loc[data]
        ok = s.notna() & r.notna()
        if ok.sum() >= 5:
            ics[data] = s[ok].rank().corr(r[ok].rank())
    return pd.Series(ics).dropna()


def calcular(precos: pd.DataFrame, padronizar: bool = False):
    ret   = np.log(precos[UNIVERSO]).diff()
    ret_m = np.log(precos[MERCADO]).diff()

    eps   = residualizar(ret, ret_m)
    sinal = {"residual": momentum(eps, padronizar),
             "bruto":    momentum(ret, padronizar)}

    fim_mes = ret.resample("ME").last().index
    fwd = ret.resample("ME").sum().shift(-1)     # retorno do mes seguinte

    out = {}
    for nome, s in sinal.items():
        s_m = s.reindex(fim_mes, method="ffill")
        out[nome] = rank_ic(s_m, fwd)
    return pd.DataFrame(out).dropna()


# --------------------------------------------------------------------------
# GRAFICO
# --------------------------------------------------------------------------
def desenhar(ic: pd.DataFrame, abriu_holdout: bool, destino: Path):
    corte = pd.Timestamp(CORTE_OOS)
    acum  = ic.cumsum()

    fig, ax = plt.subplots(figsize=(6.85, 2.76))   # 174mm x 70mm
    fig.patch.set_facecolor(PAPEL)
    ax.set_facecolor(PAPEL)

    fim_eixo = acum.index.max() if abriu_holdout else pd.Timestamp(FIM)
    ax.set_xlim(acum.index.min(), fim_eixo)

    # faixa do holdout
    ax.axvspan(corte, fim_eixo, color=AREIA, zorder=0, lw=0)
    ax.axvline(corte, color=TINTA, lw=1.2, zorder=3)

    ax.plot(acum.index, acum["residual"], color=VERDE, lw=2.2, zorder=4,
            solid_capstyle="round")
    ax.plot(acum.index, acum["bruto"], color=CINZA, lw=1.4, ls=(0, (4, 3)),
            zorder=4)

    # rotulos das regioes
    meio_res = acum.index.min() + (corte - acum.index.min()) / 2
    topo = ax.get_ylim()[1]
    ax.text(meio_res, topo * 0.94, espacado("RESEARCH SAMPLE"),
            ha="center", va="top", fontsize=7, color=NEUTRO)
    ax.text(corte + (fim_eixo - corte) / 2, topo * 0.94,
            espacado("HOLDOUT 2018 A 2026"),
            ha="center", va="top", fontsize=7, color=NEUTRO)
    if not abriu_holdout:
        ax.text(corte + (fim_eixo - corte) / 2, topo * 0.78,
                "ainda fechado", ha="center", va="top",
                fontsize=6.5, color=BORDA, style="italic")

    # nomes das series. Ancorados no ponto de maior separacao vertical entre
    # as duas curvas dentro do research sample, para nunca se sobreporem.
    ref = acum.loc[:corte]
    i = int((ref["residual"] - ref["bruto"]).abs().to_numpy().argmax())
    x_ref = ref.index[i]
    y_res, y_bru = ref["residual"].iloc[i], ref["bruto"].iloc[i]
    dy = 11 if y_res >= y_bru else -11

    ax.annotate("Residual Momentum", xy=(x_ref, y_res),
                xytext=(0, dy), textcoords="offset points",
                ha="center", fontsize=8, zorder=6,
                bbox=dict(facecolor=PAPEL, edgecolor="none", pad=1.6), color=VERDE, fontweight="bold")
    ax.annotate("Raw Momentum", xy=(x_ref, y_bru),
                xytext=(0, -dy - 4), textcoords="offset points",
                ha="center", fontsize=8, zorder=6,
                bbox=dict(facecolor=PAPEL, edgecolor="none", pad=1.6), color=NEUTRO)

    # eixos: so a base, como no relatorio
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(TINTA)
    ax.spines["bottom"].set_linewidth(1.0)
    ax.yaxis.set_major_locator(NullLocator())

    marcas = [acum.index.min(), corte] + ([fim_eixo] if abriu_holdout else [])
    ax.set_xticks(marcas)
    ax.set_xticklabels([str(m.year) for m in marcas], fontsize=8, color=NEUTRO)
    for rot in ax.get_xticklabels():
        if rot.get_text() == str(corte.year):
            rot.set_color(TINTA)
            rot.set_fontweight("bold")
    ax.tick_params(axis="x", length=0, pad=6)

    ax.set_ylabel("")
    fig.tight_layout(pad=0.4)

    destino.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        caminho = destino / f"ic_acumulado.{ext}"
        fig.savefig(caminho, facecolor=PAPEL, dpi=300, bbox_inches="tight")
        print(f"[saida] {caminho}")
    plt.close(fig)


# --------------------------------------------------------------------------
# METRICAS
# --------------------------------------------------------------------------
def reportar(ic: pd.DataFrame, abriu_holdout: bool, destino: Path):
    corte = pd.Timestamp(CORTE_OOS)
    faixas = {"research 2001-2018": ic.loc[:corte]}
    if abriu_holdout:
        faixas["holdout 2018-2026"] = ic.loc[corte:]

    linhas = []
    print("\n" + "=" * 62)
    print("FAIXA DE METRICAS DA PAGINA 4")
    print("=" * 62)
    for nome, bloco in faixas.items():
        if bloco.empty:
            continue
        reg = {
            "faixa": nome,
            "meses": len(bloco),
            "mean_ic_residual": round(bloco["residual"].mean(), 4),
            "mean_ic_bruto":    round(bloco["bruto"].mean(), 4),
            "hit_rate_residual": round((bloco["residual"] > 0).mean(), 4),
        }
        linhas.append(reg)
        print(f"\n{nome}  ({len(bloco)} meses)")
        print(f"  MEAN IC RESIDUAL   {reg['mean_ic_residual']:>8.4f}")
        print(f"  MEAN IC BRUTO      {reg['mean_ic_bruto']:>8.4f}")
        print(f"  HIT RATE IC > 0    {reg['hit_rate_residual']*100:>7.1f}%")

    # diagnostico por subperiodo, usado no bloco "o que nao funciona bem"
    print("\n" + "-" * 62)
    print("DIAGNOSTICO POR SUBPERIODO  (delta IC = residual menos bruto)")
    print("-" * 62)
    blocos = [("2001-2006", "2001", "2005"), ("2006-2012", "2006", "2011"),
              ("2012-2018", "2012", "2017")]
    if abriu_holdout:
        blocos.append(("2018-2026", "2018", "2026"))
    for rotulo, ini, fim in blocos:
        b = ic.loc[ini:fim]
        if b.empty:
            continue
        d = b["residual"].mean() - b["bruto"].mean()
        print(f"  {rotulo}   delta IC {d:+.3f}   ({len(b)} meses)")

    pd.DataFrame(linhas).to_csv(destino / "ic_metricas.csv", index=False)
    print(f"\n[saida] {destino / 'ic_metricas.csv'}")


def diagnostico(precos: pd.DataFrame):
    """
    Matriz de reconciliacao. Roda todas as combinacoes plausiveis da
    especificacao e imprime o Mean IC de cada uma, no research sample.

    Serve para achar qual combinacao reproduz o numero do notebook do grupo.
    Se nenhuma reproduzir, a divergencia precisa ser resolvida ANTES de o
    numero entrar no relatorio.
    """
    ret   = np.log(precos[UNIVERSO]).diff()
    ret_m = np.log(precos[MERCADO]).diff()
    eps   = residualizar(ret, ret_m)
    corte = pd.Timestamp(CORTE_OOS)

    fim_mes = ret.resample("ME").last().index
    fwd_mes = ret.resample("ME").sum().shift(-1)
    fwd_21d = ret.rolling(21).sum().shift(-21)

    print("\n" + "=" * 72)
    print("MATRIZ DE RECONCILIACAO  (research sample, ate 2018)")
    print("=" * 72)
    print(f"{'sinal':<22}{'padroniza':<12}{'frequencia':<20}{'mean IC':>10}{'hit':>8}")
    print("-" * 72)

    for rotulo, serie in (("residual", eps), ("bruto", ret)):
        for pad in (False, True):
            sinal = momentum(serie, padronizar=pad)
            for freq, s_al, f_al in (
                ("mensal",        sinal.reindex(fim_mes, method="ffill"), fwd_mes),
                ("diario sobrep.", sinal, fwd_21d),
            ):
                ic = rank_ic(s_al.loc[:corte], f_al.loc[:corte])
                if ic.empty:
                    continue
                print(f"{rotulo:<22}{str(pad):<12}{freq:<20}"
                      f"{ic.mean():>10.4f}{(ic > 0).mean() * 100:>7.1f}%")
    print("-" * 72)
    print("Compare com o Mean IC registrado no research log antes de publicar.")


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--abrir-holdout", action="store_true",
                    help="calcula tambem 2018 a 2026. Usar uma unica vez.")
    ap.add_argument("--dados", default="data/raw/precos_etfs.csv",
                    help="snapshot local de precos")
    ap.add_argument("--saida", default="reports", help="pasta de saida")
    ap.add_argument("--diagnostico", action="store_true",
                    help="matriz de reconciliacao das variantes de especificacao")
    ap.add_argument("--padronizar", action="store_true",
                    help="divide o momentum pelo desvio da janela (Blitz et al.)")
    args = ap.parse_args()

    if args.diagnostico:
        diagnostico(carregar_precos(Path(args.dados)))
        return

    if args.abrir_holdout:
        print("\n*** ABRINDO O HOLDOUT 2018-2026 ***")
        print("Confirme que a especificacao esta congelada e commitada.")
        if input("Digite ABRIR para continuar: ").strip() != "ABRIR":
            sys.exit("Cancelado. Holdout permanece fechado.")

    precos = carregar_precos(Path(args.dados))
    print(f"[dados] {precos.index.min().date()} a {precos.index.max().date()}, "
          f"{len(precos)} pregoes, {precos.shape[1]} series")

    ic = calcular(precos, padronizar=args.padronizar)
    if not args.abrir_holdout:
        ic = ic.loc[:pd.Timestamp(CORTE_OOS)]
    print(f"[calculo] {len(ic)} observacoes mensais de IC")

    destino = Path(args.saida)
    destino.mkdir(parents=True, exist_ok=True)
    desenhar(ic, args.abrir_holdout, destino)
    reportar(ic, args.abrir_holdout, destino)


if __name__ == "__main__":
    main()
