"""Chapter 8, Labs 8.2 and 8.3: which assumption matters most, and the energy arithmetic of a
frontier training run.

Lab 8.2  One-at-a-time sensitivity of the roadmap model (roadmap.py). Each input is moved to a low and a
         high value while the others keep their defaults, and the change in the median date of M4
         (superintelligence) is recorded. Inputs: the four stage medians (halved and increased by half),
         the spread of every stage (ratio 90th percentile / median reduced or increased by a third), the
         date range for a useful error-corrected quantum computer (2028-2032 or 2040-2050) and the quantum
         relief (0.5 instead of 0.15, applied to the M3 and M4 stages).
Lab 8.3  Electrical power needed for a training run of C operations completed in a given number of days,
         as a function of the energy efficiency of the hardware in operations per joule:
             power = C / (efficiency x utilisation x seconds) x PUE.
         Reference point: an NVIDIA H100 SXM delivers about 9.9e14 dense BF16 operations per second at a
         board power of 700 W, i.e. about 1.4e12 operations per joule at peak. Utilisation 0.4 and a power
         usage effectiveness of 1.2 are the author's stated assumptions; the board power excludes the host
         server and network, so the result is a lower bound for that hardware.
"""
import json, sys
import numpy as np
import roadmap as R

OUT = sys.argv[1] if len(sys.argv) > 1 else "roadmap_extensions_results.json"
res = {}

def m4_median(milestones=None, ftqc=None, speed=None, quantum=True):
    saved = (R.MILESTONES, R.FTQC_YEAR, R.QUANTUM_SPEEDUP)
    if milestones is not None: R.MILESTONES = milestones
    if ftqc is not None: R.FTQC_YEAR = ftqc
    if speed is not None: R.QUANTUM_SPEEDUP = speed
    R.RNG = np.random.default_rng(8)
    out = R.run(quantum)
    R.MILESTONES, R.FTQC_YEAR, R.QUANTUM_SPEEDUP = saved
    return list(out.values())[-1]["median"]

base = m4_median()
sens = []
for i, (name, med, ratio, cons, rel) in enumerate(R.MILESTONES):
    lo = [list(m) for m in R.MILESTONES]; hi = [list(m) for m in R.MILESTONES]
    lo[i][1] = med * 0.5; hi[i][1] = med * 1.5
    sens.append(dict(input=f"Duration of the {name.split()[0]} stage (median {med} years)", low_label="halved", high_label="+50%",
                     low=m4_median([tuple(m) for m in lo]) - base, high=m4_median([tuple(m) for m in hi]) - base))
lo = [(n, m, 1 + (r - 1) * 2 / 3, c, q) for n, m, r, c, q in R.MILESTONES]
hi = [(n, m, 1 + (r - 1) * 4 / 3, c, q) for n, m, r, c, q in R.MILESTONES]
sens.append(dict(input="Spread of every stage", low_label="narrower", high_label="wider", low=m4_median(lo) - base, high=m4_median(hi) - base))
sens.append(dict(input="Error-corrected quantum computer (default 2032-2042)", low_label="2028-2032", high_label="2040-2050",
                 low=m4_median(ftqc=(2028.0, 2032.0)) - base, high=m4_median(ftqc=(2040.0, 2050.0)) - base))
sens.append(dict(input="Quantum relief of M3 and M4 (default 15%)", low_label="none", high_label="50%",
                 low=m4_median(speed=0.0) - base, high=m4_median(speed=0.5) - base))
sens.append(dict(input="Quantum relief 50% and machine by 2028-2032", low_label="", high_label="combined",
                 low=0.0, high=m4_median(ftqc=(2028.0, 2032.0), speed=0.5) - base))
res["sensitivity"] = dict(base_m4_median=base, rows=sens)
for r in sens: print(r)

# ---------------------------------------------------------------- Lab 8.3
H100_EFF = 9.89e14 / 700.0          # operations per joule at peak, dense BF16
UTIL, PUE = 0.4, 1.2
effs = np.logspace(11, 14, 61)
def power_w(C, days, eff): return C / (eff * UTIL * days * 86400) * PUE
curves = {f"{C:.0e}": [power_w(C, 120, e) for e in effs] for C in (2e26, 2e27, 2e28, 2e29)}
res["energy"] = dict(utilisation=UTIL, pue=PUE, days=120, h100_ops_per_joule=H100_EFF, efficiency=effs.tolist(), power_w=curves,
                     at_h100={k: power_w(float(k), 120, H100_EFF) for k in curves},
                     efficiency_needed_for_5GW_2e29=float(2e29 / (5e9 / PUE * UTIL * 120 * 86400)),
                     efficiency_needed_for_1GW_2e29=float(2e29 / (1e9 / PUE * UTIL * 120 * 86400)))
print({k: f"{v/1e9:.2f} GW" for k, v in res["energy"]["at_h100"].items()})
print(res["energy"]["efficiency_needed_for_5GW_2e29"] / H100_EFF, res["energy"]["efficiency_needed_for_1GW_2e29"] / H100_EFF)
json.dump(res, open(OUT, "w"), indent=1)
