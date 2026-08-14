#!/usr/bin/env python3
"""
robustez_residual_momentum.py

Bateria de robustez PRE-DECLARADA para o Residual Momentum 12-1.

Roda apenas no research sample (primeiros 70% do painel, 2001-01 a 2018-10).
Nao toca no final OOS. Nenhuma variante e usada para SELECIONAR especificacao:
todas sao reportadas, inclusive as desfavoraveis. Isso e o que separa
robustez de specification search.

Uso:
    python scripts/robustez_residual_momentum.py

Saida: reports/robustez.csv e as metricas impressas no terminal.
"""

from pathlib import Path
import numpy as np
import pandas as pd

DADOS   = Path("data/raw/us_sector_etfs_plus_spy_adjusted_close.csv")
SAIDA   = Path("reports")
SPLIT   = 0.70          # fracao do painel reservada ao research sample
WIN     = 252           # janela de formacao e de estimacao do beta
GAP     = 21            # pula o mes mais recente -> 12 menos 1
N_PERM  = 5000          # permutacoes do teste de placebo
CUSTO   = 0.0010        # 10 bps por perna, ida e volta

# --------------------------------------------------------------------------

def carregar():
    px = pd.read_csv(DADOS, index_col=0, parse_dates=True)
    setores = [c for c in px.columns if c != "SPY"]
    ret = np.log(px / px.shift(1)).dropna()
    datas = list(ret.groupby(ret.index.to_period("M")).apply(lambda g: g.index[-1]))
    return ret, setores, datas


def painel(ret, setores, datas, win=WIN, gap=GAP, proxy="SPY"):
    """
    Um ponto por mes. Em cada data de decisao t estima UMA regressao de
    mercado na janela que termina em t e soma os residuos dessa mesma
    janela, excluindo os ultimos `gap` pregoes. Nenhum dado posterior a t
    entra na decisao tomada em t.
    """
    mkt = ret["SPY"] if proxy == "SPY" else ret[setores].mean(axis=1)
    linhas = []

    for j in range(len(datas) - 1):
        t, t_prox = datas[j], datas[j + 1]
        pos = ret.index.get_loc(t)
        if pos + 1 < win:
            continue

        jan = ret.iloc[pos - win + 1 : pos + 1]
        y   = jan[setores].to_numpy()
        m   = mkt.loc[jan.index].to_numpy()

        mc   = m - m.mean()
        beta = (mc @ (y - y.mean(0))) / (mc @ mc)
        alfa = y.mean(0) - beta * m.mean()
        eps  = y - (alfa + np.outer(m, beta))

        sinal = pd.Series(eps[:-gap].sum(0), index=setores)
        bruto = pd.Series(y[:-gap].sum(0), index=setores)
        fwd   = pd.Series(ret.loc[t:t_prox, setores].iloc[1:].sum().values, index=setores)

        top, bot = sinal.nlargest(3).index, sinal.nsmallest(3).index
        linhas.append({
            "data": t,
            "ic":      spearman(sinal, fwd),
            "ic_raw":  spearman(bruto, fwd),
            "spread":  fwd[top].mean() - fwd[bot].mean(),
            "top":     tuple(sorted(top)),
        })

    p = pd.DataFrame(linhas).set_index("data").dropna(subset=["ic"])
    corte = int(np.floor(len(p) * SPLIT))
    return p.iloc[:corte]          # research sample apenas


def spearman(x, y):
    return x.rank().corr(y.rank())


# --------------------------------------------------------------------------

def metricas_economicas(base):
    s = base["spread"]
    troca = np.mean([
        len(set(base["top"].iloc[i]) ^ set(base["top"].iloc[i - 1])) / 2
        for i in range(1, len(base))
    ])
    custo_aa = troca * 2 / 3 * CUSTO * 12
    cum = s.cumsum()

    print("\n=== METRICAS ECONOMICAS (Top 3 menos Bottom 3) ===")
    print(f"  spread medio mensal        {s.mean()*100:+8.3f}%")
    print(f"  spread anualizado          {s.mean()*12*100:+8.2f}%")
    print(f"  volatilidade anualizada    {s.std()*np.sqrt(12)*100:8.2f}%")
    print(f"  Sharpe bruto               {s.mean()/s.std()*np.sqrt(12):8.2f}")
    print(f"  meses positivos            {(s>0).mean()*100:8.1f}%")
    print(f"  max drawdown do spread     {(cum-cum.cummax()).min()*100:8.1f}%")
    print(f"  nomes trocados por mes     {troca:8.2f} de 3")
    print(f"  custo estimado a 10bps     {custo_aa*100:8.2f}% a.a.")
    print(f"  spread liquido de custo    {(s.mean()*12-custo_aa)*100:+8.2f}% a.a.")
    return {"spread_aa": s.mean()*12, "sharpe": s.mean()/s.std()*np.sqrt(12),
            "custo_aa": custo_aa, "turnover": troca}


def bateria(ret, setores, datas):
    print("\n=== ROBUSTEZ (todas reportadas, nenhuma seleciona spec) ===")
    print(f"{'variante':<34}{'mean IC':>10}{'spread a.a.':>14}")
    variantes = [
        ("base: SPY, formacao 252d", {}),
        ("formacao 126d",            {"win": 126}),
        ("formacao 504d",            {"win": 504}),
        ("proxy = media dos 9 ETFs", {"proxy": "EW"}),
        ("sem pular o mes (12-0)",   {"gap": 1}),
    ]
    linhas = []
    for nome, kw in variantes:
        p = painel(ret, setores, datas, **kw)
        linhas.append({"variante": nome, "mean_ic": p["ic"].mean(),
                       "spread_aa": p["spread"].mean()*12})
        print(f"{nome:<34}{p['ic'].mean():>10.4f}{p['spread'].mean()*12*100:>13.2f}%")
    return pd.DataFrame(linhas)


def permutacao(ret, setores, datas):
    """
    Placebo: embaralha o sinal entre os ativos, dentro de cada mes,
    preservando as datas e os retornos futuros. Se o sinal nao tiver
    informacao, o IC deve colapsar para zero.
    """
    sinais, futuros = [], []
    for j in range(len(datas) - 1):
        t, t_prox = datas[j], datas[j + 1]
        pos = ret.index.get_loc(t)
        if pos + 1 < WIN:
            continue
        jan = ret.iloc[pos - WIN + 1 : pos + 1]
        y, m = jan[setores].to_numpy(), jan["SPY"].to_numpy()
        mc   = m - m.mean()
        beta = (mc @ (y - y.mean(0))) / (mc @ mc)
        alfa = y.mean(0) - beta * m.mean()
        sinais.append((y - (alfa + np.outer(m, beta)))[:-GAP].sum(0))
        futuros.append(ret.loc[t:t_prox, setores].iloc[1:].sum().values)

    sinais, futuros = np.array(sinais), np.array(futuros)
    corte = int(np.floor(len(sinais) * SPLIT))
    sinais, futuros = sinais[:corte], futuros[:corte]

    def ic_medio(a, b):
        ra = np.argsort(np.argsort(a, axis=1), axis=1).astype(float)
        rb = np.argsort(np.argsort(b, axis=1), axis=1).astype(float)
        ra -= ra.mean(1, keepdims=True)
        rb -= rb.mean(1, keepdims=True)
        return ((ra*rb).sum(1) / np.sqrt((ra**2).sum(1)*(rb**2).sum(1))).mean()

    obs = ic_medio(sinais, futuros)
    rng = np.random.default_rng(7)
    nulo = np.array([ic_medio(rng.permuted(sinais, axis=1), futuros)
                     for _ in range(N_PERM)])
    p_val = (nulo >= obs).mean()

    print(f"\n=== TESTE DE PERMUTACAO ({N_PERM} sorteios) ===")
    print(f"  IC observado               {obs:+8.4f}")
    print(f"  media do nulo              {nulo.mean():+8.4f}")
    print(f"  desvio do nulo             {nulo.std():8.4f}")
    print(f"  percentil 95 do nulo       {np.percentile(nulo,95):+8.4f}")
    print(f"  percentil 99 do nulo       {np.percentile(nulo,99):+8.4f}")
    print(f"  p-valor empirico           {p_val:8.4f}")
    print(f"  z aproximado               {(obs-nulo.mean())/nulo.std():8.2f}")
    return {"ic_obs": obs, "p_valor": p_val,
            "z": (obs-nulo.mean())/nulo.std(), "nulo_std": nulo.std()}


def main():
    ret, setores, datas = carregar()
    base = painel(ret, setores, datas)
    print(f"RESEARCH SAMPLE  n={len(base)}  "
          f"{base.index.min().date()} a {base.index.max().date()}")
    print("Final OOS nao foi tocado por este script.")

    print(f"\n=== METRICAS DE SINAL ===")
    print(f"  mean IC residual           {base['ic'].mean():+8.4f}")
    print(f"  mean IC bruto              {base['ic_raw'].mean():+8.4f}")
    print(f"  hit rate IC > 0            {(base['ic']>0).mean()*100:8.1f}%")

    eco  = metricas_economicas(base)
    grid = bateria(ret, setores, datas)
    perm = permutacao(ret, setores, datas)

    SAIDA.mkdir(parents=True, exist_ok=True)
    grid.to_csv(SAIDA / "robustez.csv", index=False)
    pd.Series({**eco, **perm}).to_csv(SAIDA / "metricas_research.csv")
    print(f"\n[saida] {SAIDA/'robustez.csv'} e {SAIDA/'metricas_research.csv'}")


if __name__ == "__main__":
    main()
