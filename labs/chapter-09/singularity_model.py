"""Chapter 9 lab: a Monte Carlo model of a singularity-type transition, with and without quantum acceleration.

1. AGI arrives at a date drawn from the reader's personal forecast (Chapter 2, combined method).
2. After AGI, capability I (1 at AGI) grows by  dI/dt = r * I**alpha.
   r     : initial growth rate per year (log-normal; default median 0.35, i.e. doubling in about two years)
   alpha : returns to self-improvement (uniform 0.6 to 1.3). alpha > 1 gives runaway (finite-time) growth;
           alpha < 1 gives growth that slows as capability rises (ideas get harder to find).
   Growth is capped by a physical limit on how fast capability can grow (MAX_RATE per year).
3. A singularity-type transition is dated when I reaches THRESHOLD (default 1000 times the AGI level).
4. Quantum acceleration multiplies r by (1 + q) once a useful error-corrected quantum computer exists.
All defaults are the author's illustrative assumptions; change them.
"""
import json, importlib.util, os
import numpy as np

RNG = np.random.default_rng(9)
N = 100_000
DT = 0.05
END = 2150.0
R_MEDIAN, R_P90_RATIO = 0.35, 2.5
ALPHA = (0.6, 1.3)
MAX_RATE = 3.0            # capability can grow by at most a factor e**3 (about 20x) per year
THRESHOLD = 1000.0
FTQC_YEAR = (2032.0, 2042.0)
SCENARIOS = {"no quantum": 0.0, "quantum, evidence of Part II": 0.10, "quantum, hypothesis": 1.0}

def agi_dates(n):
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("agi", os.path.join(here, "..", "chapter-02", "agi_forecast.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.N = n; m.RNG = np.random.default_rng(2026)
    s = {"survey": m.survey(), "compute": m.compute(), "horizon": m.horizon()}
    pick = m.RNG.choice(list(s), size=n, p=[m.WEIGHTS[k] for k in s])
    out = np.empty(n)
    for k in s:
        out[pick == k] = s[k][pick == k]
    return out

def simulate(q, agi, r, alpha, ftqc):
    logI = np.zeros(N); t = agi.copy(); done = np.full(N, np.nan)
    active = agi < END
    lthr = np.log(THRESHOLD)
    year = np.minimum(agi, END)
    while active.any():
        rate = r * np.exp((alpha - 1) * logI) * np.where(year >= ftqc, 1 + q, 1.0)
        rate = np.minimum(rate, MAX_RATE)
        logI = np.where(active, logI + rate * DT, logI)
        year = np.where(active, year + DT, year)
        hit = active & (logI >= lthr)
        done[hit] = year[hit]
        active = active & ~hit & (year < END)
    return done

def summary(d):
    ok = d[~np.isnan(d)]
    q = np.percentile(ok, [10, 50, 90]) if len(ok) else [np.nan] * 3
    return {"p10": round(float(q[0]), 1), "median": round(float(q[1]), 1), "p90": round(float(q[2]), 1),
            "p_by_2045": round(float(np.mean(d <= 2045)), 3), "p_by_2060": round(float(np.mean(d <= 2060)), 3),
            "p_by_2100": round(float(np.mean(d <= 2100)), 3), "p_none_by_2150": round(float(np.mean(np.isnan(d))), 3)}

if __name__ == "__main__":
    agi = agi_dates(N)
    sigma = np.log(R_P90_RATIO) / 1.2815515655446004
    r = RNG.lognormal(np.log(R_MEDIAN), sigma, N)
    alpha = RNG.uniform(*ALPHA, N)
    ftqc = RNG.uniform(*FTQC_YEAR, N)
    out = {"agi": {"median": round(float(np.median(agi)), 1)}, "scenarios": {}, "cdf_years": list(range(2025, 2151))}
    out["cdf"] = {}
    for name, q in SCENARIOS.items():
        d = simulate(q, agi, r, alpha, ftqc)
        out["scenarios"][name] = summary(d)
        out["cdf"][name] = [round(float(np.mean(d <= y)), 4) for y in out["cdf_years"]]
        print(name, out["scenarios"][name])
    # sensitivity to returns: split by alpha
    d0 = simulate(0.0, agi, r, alpha, ftqc)
    gap = d0 - agi
    out["gap_by_alpha"] = {}
    for lo, hi in [(0.6, 0.8), (0.8, 1.0), (1.0, 1.15), (1.15, 1.3)]:
        m = (alpha >= lo) & (alpha < hi) & ~np.isnan(gap)
        out["gap_by_alpha"][f"{lo}-{hi}"] = {"median_years_agi_to_transition": round(float(np.median(gap[m])), 1),
                                             "share_reaching_by_2150": round(float(np.mean(~np.isnan(d0[(alpha >= lo) & (alpha < hi)]))), 3)}
    print(out["gap_by_alpha"])
    json.dump(out, open("singularity_results.json", "w"), indent=1)
