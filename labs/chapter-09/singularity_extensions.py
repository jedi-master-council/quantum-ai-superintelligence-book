"""Chapter 9, Labs 9.2 and 9.3: what bounds a runaway, and what one measurement would tell us.

Lab 9.2  Sensitivity of the singularity model (singularity_model.py) to its two structural assumptions:
         the physical cap on growth (at most 1.5, 2, 3, 10, 20, 100 or about 10^8 times per year) and the
         threshold that defines the transition (100, 1,000 or 10,000 times the capability of AGI).
         No quantum acceleration.
Lab 9.3  Value of information. Suppose a future study measures the returns to self-improvement, alpha,
         with a standard error of 0.1, and finds 0.8, 1.0 or 1.2. The prior (uniform 0.6 to 1.3) is updated
         by importance resampling and the model is rerun with the updated alpha, to show how far one
         measurement narrows the date of the transition.
"""
import json, sys
import numpy as np
import singularity_model as S

OUT = sys.argv[1] if len(sys.argv) > 1 else "singularity_extensions_results.json"
S.N = 40_000
rng = np.random.default_rng(99)
agi = S.agi_dates(S.N)
sigma = np.log(S.R_P90_RATIO) / 1.2815515655446004
r = rng.lognormal(np.log(S.R_MEDIAN), sigma, S.N)
alpha = rng.uniform(*S.ALPHA, S.N)
ftqc = rng.uniform(*S.FTQC_YEAR, S.N)
res = {}

def summ(d):
    s = S.summary(d); gap = d - agi; g = gap[~np.isnan(gap)]
    s["median_gap"] = round(float(np.median(g)), 1); return s

print("Lab 9.2 ...")
caps = {}
for label, cap in (("1.5x", np.log(1.5)), ("2x", np.log(2)), ("3x", np.log(3)), ("10x", np.log(10)), ("20x (default)", 3.0), ("100x", np.log(100)), ("no cap", 20.0)):
    S.MAX_RATE = cap; caps[label] = summ(S.simulate(0.0, agi, r, alpha, ftqc)); print(label, caps[label])
S.MAX_RATE = 3.0
thr = {}
for T in (100.0, 1000.0, 10000.0):
    S.THRESHOLD = T; thr[f"{int(T)}"] = summ(S.simulate(0.0, agi, r, alpha, ftqc)); print(T, thr[f"{int(T)}"])
S.THRESHOLD = 1000.0
res["cap"] = caps; res["threshold"] = thr

print("Lab 9.3 ...")
years = list(range(2025, 2151))
prior = S.simulate(0.0, agi, r, alpha, ftqc)
post = {"prior": dict(summary=summ(prior), cdf=[float(np.mean(prior <= y)) for y in years])}
for obs in (0.8, 1.0, 1.2):
    w = np.exp(-0.5 * ((alpha - obs) / 0.1) ** 2); w /= w.sum()
    idx = rng.choice(S.N, S.N, p=w)
    d = S.simulate(0.0, agi[idx], r[idx], alpha[idx], ftqc[idx])
    gap = d - agi[idx]
    sm = S.summary(d); sm["median_gap"] = round(float(np.nanmedian(gap)), 1)
    post[f"measured {obs}"] = dict(summary=sm, cdf=[float(np.mean(d <= y)) for y in years],
                                   alpha_posterior=[float(np.percentile(alpha[idx], p)) for p in (10, 50, 90)])
    print(obs, sm)
res["value_of_information"] = dict(standard_error=0.1, years=years, results=post)
json.dump(res, open(OUT, "w"), indent=1)
