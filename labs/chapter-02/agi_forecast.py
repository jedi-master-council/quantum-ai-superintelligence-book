"""Chapter 2 lab: build a personal AGI forecast from three published inputs.

Every assumption is a named parameter at the top of the file. Change them and rerun.
Method 1  Expert survey: a log-normal fitted to the two quantiles reported by
          Grace et al. (2024) for 'high-level machine intelligence' (10% by 2027, 50% by 2047;
          survey fielded in 2023).
Method 2  Compute threshold: training compute grows by a fixed factor each year until a
          slowdown year; AGI arrives when compute has grown by a required number of orders of
          magnitude (OOM) above the 2025 frontier. The required OOM is uncertain.
Method 3  Task-horizon trend: the length of task frontier agents complete with 50% reliability
          (about 110 minutes for the best 2025 model; Kwa et al. 2025) doubles every few months
          until it reaches a target horizon taken here as a proxy for general capability.
The three distributions are mixed with weights chosen by the reader.
Writes results to agi_forecast_results.json.
"""
import json
import numpy as np

RNG = np.random.default_rng(2026)
N = 200_000
NOW = 2025.0

# ---- Method 1: survey ------------------------------------------------------------
SURVEY_YEAR, Q10, Q50 = 2023.0, 2027.0, 2047.0

# ---- Method 2: compute threshold (all values are assumptions to be changed) ---------
GROWTH_OOM_PER_YEAR = (0.55, 0.75)   # 4-5x per year is 0.60-0.70 OOM per year (Epoch AI 2024)
SLOWDOWN_YEAR = (2028.0, 2035.0)     # after this, growth falls to SLOW_OOM_PER_YEAR
SLOW_OOM_PER_YEAR = 0.25
REQUIRED_OOM_LOG10_MEDIAN = 4.0      # median: 4 OOM above the 2025 frontier
REQUIRED_OOM_SD = 1.5                # spread in OOM

# ---- Method 3: task horizon ----------------------------------------------------------
H0_MIN, H0_YEAR = 110.0, 2025.3      # 50% horizon of the best model in early 2025 (minutes)
DOUBLING_MONTHS = (4.0, 12.0)        # uniform range around the reported ~7 months
TARGET_HOURS_LOG10 = (np.log10(40.0), np.log10(2000.0))   # one working week to one working year

WEIGHTS = {"survey": 1 / 3, "compute": 1 / 3, "horizon": 1 / 3}


def survey():
    from math import log
    z10 = 1.2815515655446004
    mu = log(Q50 - SURVEY_YEAR)
    sigma = (log(Q50 - SURVEY_YEAR) - log(Q10 - SURVEY_YEAR)) / z10
    return SURVEY_YEAR + RNG.lognormal(mu, sigma, N)


def compute():
    g = RNG.uniform(*GROWTH_OOM_PER_YEAR, N)
    slow = RNG.uniform(*SLOWDOWN_YEAR, N)
    need = np.clip(RNG.normal(REQUIRED_OOM_LOG10_MEDIAN, REQUIRED_OOM_SD, N), 0.0, None)
    fast_oom = g * np.clip(slow - NOW, 0, None)
    t_fast = need / g
    t = np.where(need <= fast_oom, NOW + t_fast, slow + (need - fast_oom) / SLOW_OOM_PER_YEAR)
    return t


def horizon():
    d = RNG.uniform(*DOUBLING_MONTHS, N) / 12.0
    target_min = 10 ** RNG.uniform(*TARGET_HOURS_LOG10, N) * 60.0
    doublings = np.log2(target_min / H0_MIN)
    return H0_YEAR + doublings * d


def summary(x):
    q = np.percentile(x, [10, 50, 90])
    return {"p10": round(float(q[0]), 1), "median": round(float(q[1]), 1), "p90": round(float(q[2]), 1),
            "p_by_2030": round(float(np.mean(x <= 2030)), 3), "p_by_2040": round(float(np.mean(x <= 2040)), 3),
            "p_by_2050": round(float(np.mean(x <= 2050)), 3)}


if __name__ == "__main__":
    samples = {"survey": survey(), "compute": compute(), "horizon": horizon()}
    pick = RNG.choice(list(samples), size=N, p=[WEIGHTS[k] for k in samples])
    combined = np.empty(N)
    for k in samples:
        combined[pick == k] = samples[k][pick == k]
    samples["combined"] = combined
    out = {k: summary(v) for k, v in samples.items()}
    grid = np.arange(2025, 2101)
    out["cdf"] = {k: [round(float(np.mean(v <= y)), 4) for y in grid] for k, v in samples.items()}
    out["cdf_years"] = grid.tolist()
    json.dump(out, open("agi_forecast_results.json", "w"), indent=1)
    for k in ("survey", "compute", "horizon", "combined"):
        print(f"{k:9s}", out[k])
