"""Chapter 8 roadmap model: four milestones from today's AI to superintelligence.

Each milestone follows the previous one after a duration drawn from a log-normal distribution
(median and the ratio of the 90th percentile to the median are the author's illustrative defaults;
change them). Each milestone names its binding constraint. A quantum scenario shortens the
durations of milestones whose binding constraint quantum computing could relieve (materials and
energy, through quantum simulation), but only once a useful error-corrected quantum computer
exists, at a date drawn from a range.
Writes roadmap_results.json.
"""
import json
import numpy as np

RNG = np.random.default_rng(8)
N = 200_000
START = 2025.0
MILESTONES = [
    # name, median years after previous, p90/median ratio, binding constraint, quantum can relieve?
    ("M1 Agents complete week-long tasks", 3.5, 1.8, "reliability of algorithms", False),
    ("M2 AI carries out most AI research", 3.0, 2.2, "compute for experiments", False),
    ("M3 AGI: every task, better and cheaper", 4.0, 2.5, "energy, materials and robotics", True),
    ("M4 ASI: far beyond the best humans", 5.0, 3.0, "energy and algorithmic insight", True),
]
FTQC_YEAR = (2032.0, 2042.0)      # useful error-corrected quantum computer, uniform range
QUANTUM_SPEEDUP = 0.15            # fraction by which relievable durations shorten once FTQC exists

def lognormal(median, ratio, n):
    sigma = np.log(ratio) / 1.2815515655446004
    return RNG.lognormal(np.log(median), sigma, n)

def run(quantum):
    t = np.full(N, START); out = {}
    ftqc = RNG.uniform(*FTQC_YEAR, N)
    for name, med, ratio, constraint, relievable in MILESTONES:
        d = lognormal(med, ratio, N)
        if quantum and relievable:
            d = np.where(t >= ftqc, d * (1 - QUANTUM_SPEEDUP), d)
        t = t + d
        q = np.percentile(t, [10, 50, 90])
        out[name] = {"p10": round(float(q[0]), 1), "median": round(float(q[1]), 1), "p90": round(float(q[2]), 1),
                     "constraint": constraint, "quantum_relievable": relievable}
    return out

if __name__ == "__main__":
    res = {"classical": run(False), "quantum": run(True), "assumptions": {
        "start": START, "milestones": MILESTONES, "ftqc_year": FTQC_YEAR, "quantum_speedup": QUANTUM_SPEEDUP}}
    json.dump(res, open("roadmap_results.json", "w"), indent=1)
    for sc in ("classical", "quantum"):
        print(sc)
        for k, v in res[sc].items():
            print("  ", k, v["p10"], v["median"], v["p90"])
