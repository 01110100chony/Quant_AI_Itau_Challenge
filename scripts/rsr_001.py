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

        # pesos: +1/k nos comprados, -1/k nos vendidos, 0 no resto
        w = pd.Series(0.0, index=UNIVERSO)
        w[lng] = +1.0 / TOP_BOTTOM
        w[srt] = -1.0 / TOP_BOTTOM

        linhas.append({"data": t, "ic": spearman(x, fwd),
                       "spread": float(w @ fwd),
                       **{f"w_{c}": w[c] for c in UNIVERSO}})

    p = pd.DataFrame(linhas).set_index("data")

    # Cost_t = c * soma_i |w_it - w_i,t-1|, com w_i,-1 = 0
    cols = [f"w_{c}" for c in UNIVERSO]
    p["turnover"] = p[cols].diff().abs().sum(axis=1)
    p.loc[p.index[0], "turnover"] = p.loc[p.index[0], cols].abs().sum()
    p["custo"] = CUSTO_PERNA * p["turnover"]
    p["liquido"] = p["spread"] - p["custo"]
    return p


def fatiar(p):
    """research | contaminado (quarentena) | oos limpo"""
    res  = p.loc[:RESEARCH_END]
    cont = p.loc[RESEARCH_END:CONTAM_END].iloc[1:]
    oos  = p.loc[CONTAM_END:].iloc[1:]
    return res, cont, oos


def metricas(bloco, rotulo):
    s, n = bloco["spread"], bloco["liquido"]
    cum  = n.cumsum()
    print(f"\n--- {rotulo}  ({len(bloco)} meses, "
          f"{bloco.index.min().date()} a {bloco.index.max().date()}) ---")
    print(f"  mean IC                 {bloco['ic'].mean():+8.4f}")
    print(f"  hit rate IC > 0         {(bloco['ic']>0).mean()*100:7.1f}%")
    print(f"  spread bruto            {s.mean()*12*100:+7.2f}% a.a.")
    print(f"  turnover soma|dw|       {bloco['turnover'].mean():7.3f} por mes")
    print(f"  custo                   {bloco['custo'].mean()*12*100:7.2f}% a.a.")
    print(f"  retorno LIQUIDO         {n.mean()*12*100:+7.2f}% a.a.")
    print(f"  volatilidade (liquido)  {n.std()*np.sqrt(12)*100:7.2f}%")
    print(f"  Sharpe liquido          {n.mean()*12/(n.std()*np.sqrt(12)):7.2f}")
    print(f"  meses liquidos positivos{(n>0).mean()*100:7.1f}%")
    print(f"  max drawdown (liquido)  {(cum-cum.cummax()).min()*100:7.1f}%")
    return {"mean_ic": bloco["ic"].mean(), "spread_bruto_aa": s.mean() * 12,
            "custo_aa": bloco["custo"].mean() * 12, "liquido_aa": n.mean() * 12,
            "sharpe_liquido": n.mean() * 12 / (n.std() * np.sqrt(12)),
            "turnover": bloco["turnover"].mean(), "n": len(bloco)}


def matrizes(ret, mkt, idx):
    """Sinal e retorno futuro alinhados, para os meses em idx."""
    sinal = -residuos_pit(ret, mkt).rolling(S_REVERSAO).sum()
    datas = [d for d in ret.groupby(ret.index.to_period("M")).apply(lambda g: g.index[-1])]
    X, Y = [], []
    for j in range(len(datas) - 1):
        t, t_prox = datas[j], datas[j + 1]
        if t not in idx:
            continue
        X.append(sinal.loc[t].values)
        Y.append(ret.loc[t:t_prox, UNIVERSO].iloc[1:].sum().values)
    return np.array(X), np.array(Y)


def relatar_placebos(ret, mkt, idx, rotulo):
    X, Y = matrizes(ret, mkt, idx)
    obs, p1, p2 = placebos(X, Y)
    print(f"\n--- PLACEBOS ({rotulo}) ---")
    print(f"  IC observado                    {obs:+8.4f}")
    print(f"  P1 permutacao cross-sectional   p = {p1:6.4f}")
    print(f"  P2 embaralhamento temporal      p = {p2:6.4f}")
    r_res, r_raw, d = ablacao_a1(ret, idx, X, Y)
    print(f"\n--- A1 ABLACAO DE RESIDUALIZACAO (evidencia secundaria) ---")
    print(f"  IC reversao residual            {r_res:+8.4f}")
    print(f"  IC reversao sem residualizar    {r_raw:+8.4f}")
    print(f"  delta IC (A1)                   {d:+8.4f}   (esperado > 0)")
    print("  A1 nao e placebo e nao e condicao de GO.")


def robustez(ret, mkt):
    print("\n--- ROBUSTEZ (todas reportadas, nenhuma seleciona a spec) ---")
    print(f"{'variante':<38}{'mean IC':>10}{'spread a.a.':>13}")
    for nome, kw in [("base: W=252, S=21", {}),
                     ("W=126", {"w": 126}), ("W=504", {"w": 504}),
                     ("S=10",  {"s": 10}),  ("S=42",  {"s": 42})]:
        res, _, _ = fatiar(painel(ret, mkt, **kw))
        print(f"{nome:<38}{res['ic'].mean():>10.4f}"
              f"{res['spread'].mean()*12*100:>12.2f}%")


def ic_medio(a, b):
    ra = np.argsort(np.argsort(a, 1), 1).astype(float)
    rb = np.argsort(np.argsort(b, 1), 1).astype(float)
    ra -= ra.mean(1, keepdims=True)
    rb -= rb.mean(1, keepdims=True)
    return ((ra * rb).sum(1) / np.sqrt((ra ** 2).sum(1) * (rb ** 2).sum(1))).mean()


N_PERM, SEMENTE = 5000, 7


def placebos(X, Y, n=N_PERM, semente=SEMENTE):
    """
    Placebos pre-registrados. Ambos unilaterais, pois H_A: mean IC > 0.

    P1  permutacao cross-sectional: dentro de cada mes, embaralha os labels
        do sinal entre os 9 ativos, preservando os retornos daquele mes.

    P2  permutacao temporal em bloco: reordena os meses do vetor
        cross-sectional completo (R_1,...,R_9)_{t+1}, mantendo cada vetor
        intacto. Nao permuta ativos independentemente.

    p-valor unilateral, estimador nao enviesado de Monte Carlo:

        p = (1 + #{nulo >= observado}) / (N + 1)
    """
    obs = ic_medio(X, Y)
    rng = np.random.default_rng(semente)
    n1  = np.array([ic_medio(rng.permuted(X, axis=1), Y) for _ in range(n)])
    rng = np.random.default_rng(semente)
    n2  = np.array([ic_medio(X, Y[rng.permutation(len(Y))]) for _ in range(n)])
    p = lambda nulo: (1 + int((nulo >= obs).sum())) / (n + 1)
    return obs, p(n1), p(n2)


def ablacao_a1(ret, idx, X, Y):
    """
    A1 — Residualization Ablation. NAO e placebo e NAO e condicao de GO.
    Compara o IC do sinal residual com o da mesma reversao calculada sobre
    o retorno bruto. Evidencia secundaria de que residualizar agrega.
    """
    bruto = -ret[UNIVERSO].rolling(S_REVERSAO).sum()
    datas = [d for d in ret.groupby(ret.index.to_period("M")).apply(lambda g: g.index[-1])]
    Xb = np.array([bruto.loc[t].values for t in datas[:-1] if t in idx])
    ic_res, ic_raw = ic_medio(X, Y), ic_medio(Xb, Y)
    return ic_res, ic_raw, ic_res - ic_raw


def avaliar_criterio(bloco, X, Y):
    """
    Criterio pre-registrado em spec.md. Nao alterar apos a abertura.
    ScientificPass e EconomicPass sao avaliados separadamente.
    A1 nao entra no criterio.
    """
    ic, liq = bloco["ic"], bloco["liquido"]
    obs, p1, p2 = placebos(X, Y)

    # tres blocos cronologicos, definidos por posicao antes da abertura
    cortes = np.array_split(np.arange(len(bloco)), 3)
    ic_blocos  = [ic.iloc[c].mean() for c in cortes]
    net_blocos = [liq.iloc[c].mean() * 12 for c in cortes]
    net_total  = liq.mean() * 12

    sci = (ic.mean() > 0 and p1 < 0.10 and p2 < 0.10
           and sum(v > 0 for v in ic_blocos) >= 2)
    eco = (net_total > 0 and sum(v > 0 for v in net_blocos) >= 2)

    print("\n--- CRITERIO PRE-REGISTRADO ---")
    print(f"  mean IC no OOS            {ic.mean():+8.4f}   {'ok' if ic.mean()>0 else 'FALHA'}")
    print(f"  P1 permutacao cross-sec.  p={p1:6.4f}   {'ok' if p1<0.10 else 'FALHA'}")
    print(f"  P2 embaralhamento tempo.  p={p2:6.4f}   {'ok' if p2<0.10 else 'FALHA'}")
    print(f"  IC>0 nos blocos           {sum(v>0 for v in ic_blocos)} de 3      "
          f"{'ok' if sum(v>0 for v in ic_blocos)>=2 else 'FALHA'}")
    print(f"    B1 {ic_blocos[0]:+.4f}   B2 {ic_blocos[1]:+.4f}   B3 {ic_blocos[2]:+.4f}")
    print(f"  ScientificPass            {'SIM' if sci else 'NAO'}")
    print(f"\n  retorno liquido no OOS    {net_total*100:+7.2f}% a.a.   "
          f"{'ok' if net_total>0 else 'FALHA'}")
    print(f"  liquido>0 nos blocos      {sum(v>0 for v in net_blocos)} de 3      "
          f"{'ok' if sum(v>0 for v in net_blocos)>=2 else 'FALHA'}")
    print(f"    B1 {net_blocos[0]*100:+.2f}%   B2 {net_blocos[1]*100:+.2f}%   "
          f"B3 {net_blocos[2]*100:+.2f}%")
    print(f"  EconomicPass              {'SIM' if eco else 'NAO'}")

    if sci and eco:
        return "GO", p1, p2
    if sci:
        return "CONDITIONAL GO", p1, p2
    return "NO-GO", p1, p2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abrir-oos", action="store_true")
    ap.add_argument("--robustez", action="store_true")
    ap.add_argument("--ensaio", action="store_true",
                    help="exercita o caminho do criterio no RESEARCH sample, "
                         "para validar o codigo antes da execucao irreversivel")
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
        relatar_placebos(ret, mkt, set(res.index), "research sample")

    if args.ensaio:
        print("\n" + "#" * 62)
        print("ENSAIO. Criterio aplicado ao RESEARCH sample, nao ao OOS.")
        print("Serve apenas para validar o caminho de codigo. O resultado")
        print("abaixo NAO e valido como decisao, porque a amostra ja foi vista.")
        print("#" * 62)
        Xr, Yr = matrizes(ret, mkt, set(res.index))
        v, _, _ = avaliar_criterio(res, Xr, Yr)
        print(f"\n  [ensaio] o caminho de codigo executou e retornaria: {v}")
        print("  [ensaio] OOS permanece fechado.")

    if args.abrir_oos:
        print("\n" + "=" * 62)
        print("ABERTURA DO FINAL OOS. OPERACAO IRREVERSIVEL.")
        print("Confirme que spec.md esta aprovado e commitado.")
        print("=" * 62)
        if input("Digite ABRIR OOS para continuar: ").strip() != "ABRIR OOS":
            sys.exit("Cancelado. OOS permanece fechado.")

        m_oos = metricas(oos, "FINAL OOS")
        X, Y = matrizes(ret, mkt, set(oos.index))
        veredito, p1, p2 = avaliar_criterio(oos, X, Y)

        print("\n" + "=" * 62)
        print(f"VEREDITO  ->  {veredito}")
        print("=" * 62)
        print("Nenhum parametro pode ser reajustado a partir daqui.")

        SAIDA.mkdir(parents=True, exist_ok=True)
        oos.drop(columns="long").to_csv(SAIDA / "rsr_001_oos_bruto.csv")
        pd.Series({**{f"research_{k}": v for k, v in m_res.items()},
                   **{f"oos_{k}": v for k, v in m_oos.items()},
                   "oos_p_P1": p1, "oos_p_P2": p2,
                   "veredito": veredito,
                   "aberto_em": dt.datetime.now().isoformat(timespec="seconds")}
                  ).to_csv(SAIDA / "rsr_001_veredito.csv")
        print(f"\n[saida] {SAIDA/'rsr_001_oos_bruto.csv'}")
        print(f"[saida] {SAIDA/'rsr_001_veredito.csv'}")
        print("\nAtualize manifest.toml: oos_opened = true e oos_opened_at.")


if __name__ == "__main__":
    main()
