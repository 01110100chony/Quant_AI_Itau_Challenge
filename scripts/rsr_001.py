#!/usr/bin/env python3
"""
rsr_001.py — implementacao canonica de RSR_001, Residual Short-Term Reversal.

Contrato: este script implementa exatamente o que esta congelado em
research/experiments/RSR_001/spec.md. Qualquer divergencia entre os dois e
um bug, e o spec prevalece.

    python scripts/rsr_001.py                # research sample apenas
    python scripts/rsr_001.py --robustez     # + bateria e permutacao
    python scripts/rsr_001.py --abrir-oos    # abre o OOS limpo. UMA vez.

O Final OOS (2019-03-29 a 2026-07-31) so e tocado com --abrir-oos, que exige
confirmacao digitada. O periodo 2018-11-30 a 2019-02-28 esta em quarentena
permanente e nunca entra em nenhum calculo.
"""

import argparse
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---- PARAMETROS CONGELADOS (spec.md v1.0) --------------------------------
UNIVERSO      = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
MERCADO       = "SPY"
W_ESTIMACAO   = 252          # |W_d| = 252, estritamente anterior a d
S_REVERSAO    = 21           # |S_t| = 21
TOP_BOTTOM    = 3
CUSTO_PERNA   = 0.0010       # 10 bps por perna, ida e volta
RESEARCH_END  = "2018-10-31"
CONTAM_END    = "2019-02-28" # quarentena permanente
DADOS         = Path("data/raw/us_sector_etfs_plus_spy_adjusted_close.csv")
SAIDA         = Path("reports")


def spearman(x, y):
    return x.rank().corr(y.rank())


def residuos_pit(ret, mkt, w=W_ESTIMACAO):
    """
    Residuos point-in-time. Beta e alpha de [d-w, d-1], aplicados em d.
    A janela de estimacao NAO inclui d, portanto a identidade de OLS que
    invalidou o construct anterior nao se aplica.
    """
    var = mkt.rolling(w).var().shift(1)
    med = mkt.rolling(w).mean().shift(1)
    saida = {}
    for tic in UNIVERSO:
        beta = ret[tic].rolling(w).cov(mkt).shift(1) / var
        alfa = ret[tic].rolling(w).mean().shift(1) - beta * med
        saida[tic] = ret[tic] - alfa - beta * mkt
    return pd.DataFrame(saida)


def painel(ret, mkt, w=W_ESTIMACAO, s=S_REVERSAO):
    eps  = residuos_pit(ret, mkt, w)
    sinal = -eps.rolling(s).sum()                 # S_t = {t-(s-1), ..., t}
    datas = [d for d in ret.groupby(ret.index.to_period("M")).apply(lambda g: g.index[-1])]

    linhas = []
    for j in range(len(datas) - 1):
        t, t_prox = datas[j], datas[j + 1]
        if t not in sinal.index or sinal.loc[t].isna().any():
            continue
        x   = sinal.loc[t]
        fwd = pd.Series(ret.loc[t:t_prox, UNIVERSO].iloc[1:].sum().values, index=UNIVERSO)
        lng = x.nlargest(TOP_BOTTOM).index
        srt = x.nsmallest(TOP_BOTTOM).index
        linhas.append({"data": t, "ic": spearman(x, fwd),
                       "spread": fwd[lng].mean() - fwd[srt].mean(),
                       "long": tuple(sorted(lng))})
    return pd.DataFrame(linhas).set_index("data")


def fatiar(p):
    """research | contaminado (quarentena) | oos limpo"""
    res  = p.loc[:RESEARCH_END]
    cont = p.loc[RESEARCH_END:CONTAM_END].iloc[1:]
    oos  = p.loc[CONTAM_END:].iloc[1:]
    return res, cont, oos


def metricas(bloco, rotulo):
    s = bloco["spread"]
    troca = np.mean([len(set(bloco["long"].iloc[i]) ^ set(bloco["long"].iloc[i - 1])) / 2
                     for i in range(1, len(bloco))])
    custo = troca * 2 / TOP_BOTTOM * CUSTO_PERNA * 12
    liq   = s.mean() * 12 - custo
    cum   = s.cumsum()
    print(f"\n--- {rotulo}  ({len(bloco)} meses, "
          f"{bloco.index.min().date()} a {bloco.index.max().date()}) ---")
    print(f"  mean IC                 {bloco['ic'].mean():+8.4f}")
    print(f"  hit rate IC > 0         {(bloco['ic']>0).mean()*100:7.1f}%")
    print(f"  spread bruto            {s.mean()*12*100:+7.2f}% a.a.")
    print(f"  turnover                {troca:7.2f} de {TOP_BOTTOM}")
    print(f"  custo estimado          {custo*100:7.2f}% a.a.")
    print(f"  spread LIQUIDO          {liq*100:+7.2f}% a.a.")
    print(f"  volatilidade            {s.std()*np.sqrt(12)*100:7.2f}%")
    print(f"  Sharpe liquido          {liq/(s.std()*np.sqrt(12)):7.2f}")
    print(f"  meses positivos         {(s>0).mean()*100:7.1f}%")
    print(f"  max drawdown do spread  {(cum-cum.cummax()).min()*100:7.1f}%")
    return {"mean_ic": bloco["ic"].mean(), "spread_liquido_aa": liq,
            "sharpe_liquido": liq / (s.std() * np.sqrt(12)),
            "turnover": troca, "n": len(bloco)}


def permutacao(ret, mkt, res_idx, n=5000):
    eps   = residuos_pit(ret, mkt)
    sinal = -eps.rolling(S_REVERSAO).sum()
    datas = [d for d in ret.groupby(ret.index.to_period("M")).apply(lambda g: g.index[-1])]
    X, Y = [], []
    for j in range(len(datas) - 1):
        t, t_prox = datas[j], datas[j + 1]
        if t not in res_idx:
            continue
        X.append(sinal.loc[t].values)
        Y.append(ret.loc[t:t_prox, UNIVERSO].iloc[1:].sum().values)
    X, Y = np.array(X), np.array(Y)

    def ic_medio(a, b):
        ra = np.argsort(np.argsort(a, 1), 1).astype(float)
        rb = np.argsort(np.argsort(b, 1), 1).astype(float)
        ra -= ra.mean(1, keepdims=True)
        rb -= rb.mean(1, keepdims=True)
        return ((ra * rb).sum(1) / np.sqrt((ra ** 2).sum(1) * (rb ** 2).sum(1))).mean()

    obs  = ic_medio(X, Y)
    rng  = np.random.default_rng(7)
    nulo = np.array([ic_medio(rng.permuted(X, axis=1), Y) for _ in range(n)])
    print(f"\n--- PERMUTACAO ({n} sorteios, research sample) ---")
    print(f"  IC observado            {obs:+8.4f}")
    print(f"  desvio do nulo          {nulo.std():8.4f}")
    print(f"  p-valor empirico        {(nulo>=obs).mean():8.4f}")
    print(f"  z                       {(obs-nulo.mean())/nulo.std():8.2f}")


def robustez(ret, mkt):
    print("\n--- ROBUSTEZ (todas reportadas, nenhuma seleciona a spec) ---")
    print(f"{'variante':<38}{'mean IC':>10}{'spread a.a.':>13}")
    for nome, kw in [("base: W=252, S=21", {}),
                     ("W=126", {"w": 126}), ("W=504", {"w": 504}),
                     ("S=10",  {"s": 10}),  ("S=42",  {"s": 42})]:
        res, _, _ = fatiar(painel(ret, mkt, **kw))
        print(f"{nome:<38}{res['ic'].mean():>10.4f}"
              f"{res['spread'].mean()*12*100:>12.2f}%")


def avaliar_criterio(m):
    """Criterio pre-registrado em spec.md. Nao alterar apos a abertura."""
    if m["mean_ic"] > 0 and m["spread_liquido_aa"] > 0:
        return "GO"
    if m["mean_ic"] > 0:
        return "CONDITIONAL GO"
    return "NO-GO"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abrir-oos", action="store_true")
    ap.add_argument("--robustez", action="store_true")
    args = ap.parse_args()

    px  = pd.read_csv(DADOS, index_col=0, parse_dates=True)
    ret = np.log(px / px.shift(1)).dropna()
    mkt = ret[MERCADO]

    p = painel(ret, mkt)
    res, cont, oos = fatiar(p)

    print("RSR_001 — Residual Short-Term Reversal")
    print(f"research     {res.index.min().date()} a {res.index.max().date()}  n={len(res)}")
    print(f"quarentena   {cont.index.min().date()} a {cont.index.max().date()}  n={len(cont)}  (excluida)")
    print(f"OOS limpo    {oos.index.min().date()} a {oos.index.max().date()}  n={len(oos)}"
          f"  {'ABRINDO' if args.abrir_oos else 'FECHADO'}")

    m_res = metricas(res, "RESEARCH SAMPLE")

    if args.robustez:
        robustez(ret, mkt)
        permutacao(ret, mkt, set(res.index))

    if args.abrir_oos:
        print("\n" + "=" * 62)
        print("ABERTURA DO FINAL OOS. OPERACAO IRREVERSIVEL.")
        print("Confirme que spec.md esta aprovado e commitado.")
        print("=" * 62)
        if input("Digite ABRIR OOS para continuar: ").strip() != "ABRIR OOS":
            sys.exit("Cancelado. OOS permanece fechado.")

        m_oos = metricas(oos, "FINAL OOS")
        veredito = avaliar_criterio(m_oos)
        print("\n" + "=" * 62)
        print(f"CRITERIO PRE-REGISTRADO  ->  {veredito}")
        print("=" * 62)
        print("Nenhum parametro pode ser reajustado a partir daqui.")

        SAIDA.mkdir(parents=True, exist_ok=True)
        oos.drop(columns="long").to_csv(SAIDA / "rsr_001_oos_bruto.csv")
        pd.Series({**{f"research_{k}": v for k, v in m_res.items()},
                   **{f"oos_{k}": v for k, v in m_oos.items()},
                   "veredito": veredito,
                   "aberto_em": dt.datetime.now().isoformat(timespec="seconds")}
                  ).to_csv(SAIDA / "rsr_001_veredito.csv")
        print(f"\n[saida] {SAIDA/'rsr_001_oos_bruto.csv'}")
        print(f"[saida] {SAIDA/'rsr_001_veredito.csv'}")
        print("\nAtualize manifest.toml: oos_opened = true e oos_opened_at.")


if __name__ == "__main__":
    main()
