"""Chapter 5, Labs 5.3 and 5.4: what the quantum classifier computes, what training it costs,
and how the quantum kernel depends on its bandwidth.

Lab 5.3  (a) The output of the trained classifier of Lab 5.1 is sampled on a grid and its two-dimensional
         Fourier spectrum computed. With three re-uploads of RY(x) encodings the output can contain only
         integer frequencies from -3 to 3 in each feature (Schuld, Sweke and Meyer 2021).
         (b) A classical surrogate: a linear model on the 49 functions cos/sin(k x1 + m x2), |k|,|m| <= 3,
         is fitted to the quantum model's output and, separately, trained directly on the data.
         (c) Cost accounting: circuit executions and shots needed to train the model on hardware, and the
         effect of finite shots on training (gradients estimated from 100 and 1,000 shots).
Lab 5.4  Quantum kernel bandwidth: the features are multiplied by a factor c before encoding, and the
         test accuracy and the typical off-diagonal kernel value are recorded (Shaydulin and Wild 2022).
Run from this folder after lab5_qnn.py; reads lab5_results.json for the trained parameters.
"""
import json, sys, time
import numpy as np
import lab5_qnn as Q
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC

OUT = sys.argv[1] if len(sys.argv) > 1 else "lab5_extensions_results.json"
R = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "lab5_results.json"))
th = np.array(R["theta"])
res = {}

# ---------------- (a) Fourier spectrum of the trained model
N = 16
g = 2 * np.pi * np.arange(N) / N
F = np.array([[Q.vqc_out(np.array([a, b]), th) for a in g] for b in g])      # F[b, a]
C = np.fft.fft2(F) / N ** 2                                                     # C[m, k]: m for x2, k for x1
freqs = np.fft.fftfreq(N, 1 / N).astype(int)
power = np.abs(C) ** 2
inside = sum(power[i, j] for i in range(N) for j in range(N) if abs(freqs[i]) <= Q.L and abs(freqs[j]) <= Q.L)
res["fourier"] = dict(grid_points=N, max_frequency_allowed=Q.L,
                      power_fraction_within_allowed=float(inside / power.sum()),
                      magnitude=[[float(np.abs(C[i, j])) for j in np.argsort(freqs)] for i in np.argsort(freqs)],
                      freqs=sorted(freqs.tolist()))

# ---------------- (b) classical trigonometric surrogate
K = [(k, m) for k in range(-Q.L, Q.L + 1) for m in range(-Q.L, Q.L + 1)]
def trig(X):
    cols = [np.ones(len(X))]
    for k, m in K:
        if (k, m) > (0, 0):                                  # one of each +/- pair; (0,0) is the constant
            ph = k * X[:, 0] + m * X[:, 1]
            cols += [np.cos(ph), np.sin(ph)]
    return np.stack(cols, 1)
Ftr = trig(Q.Xtr); Fte = trig(Q.Xte)
q_tr = np.array([Q.vqc_out(x, th) for x in Q.Xtr]); q_te = np.array([Q.vqc_out(x, th) for x in Q.Xte])
mimic = LinearRegression(fit_intercept=False).fit(Ftr, q_tr)
res["surrogate"] = dict(n_features=Ftr.shape[1],
                        r2_on_test_inputs=float(mimic.score(Fte, q_te)),
                        max_abs_error=float(np.max(np.abs(mimic.predict(Fte) - q_te))),
                        same_predictions=float(np.mean((mimic.predict(Fte) < 0) == (q_te < 0))))
direct = LogisticRegression(C=1.0, max_iter=5000).fit(Ftr[:, 1:], Q.ytr)
res["surrogate"]["trained_on_data_test_acc"] = float(direct.score(Fte[:, 1:], Q.yte))

# ---------------- (c) cost of training on hardware, and finite-shot training
epochs, n_train, P = 60, len(Q.Xtr), Q.NP
per_epoch = n_train * (2 * P + 1)                 # forward pass plus two shifted circuits per parameter
res["cost"] = dict(epochs=epochs, train_points=n_train, parameters=P, circuits_per_epoch=per_epoch,
                   circuits_total=per_epoch * epochs, shots_total_at_1000=per_epoch * epochs * 1000)

def shot_out(x, th_, shots, rng):
    p0 = (1 + Q.vqc_out(x, th_)) / 2
    return 2 * rng.binomial(shots, min(max(p0, 0), 1)) / shots - 1

def train_shots(shots, seed=5, epochs=60, lr=0.05):
    rng = np.random.default_rng(seed); th_ = rng.uniform(0, 2 * np.pi, P); m = np.zeros(P); v = np.zeros(P)
    for ep in range(1, epochs + 1):
        idx = rng.permutation(n_train)
        for b in range(0, n_train, 25):
            bi = idx[b:b + 25]; t = 1 - 2 * Q.ytr[bi]
            out = np.array([shot_out(x, th_, shots, rng) for x in Q.Xtr[bi]])
            gr = np.zeros(P)
            for k in range(P):
                e = np.zeros(P); e[k] = np.pi / 2
                op = np.array([shot_out(x, th_ + e, shots, rng) for x in Q.Xtr[bi]])
                om = np.array([shot_out(x, th_ - e, shots, rng) for x in Q.Xtr[bi]])
                gr[k] = np.mean((out - t) * (op - om))
            m = 0.9 * m + 0.1 * gr; v = 0.999 * v + 0.001 * gr ** 2
            th_ -= lr * (m / (1 - 0.9 ** ep)) / (np.sqrt(v / (1 - 0.999 ** ep)) + 1e-8)
    return float(np.mean((np.array([Q.vqc_out(x, th_) for x in Q.Xte]) < 0) == Q.yte))

t0 = time.time()
res["finite_shots"] = {str(s): train_shots(s) for s in (10, 100, 1000)}
res["finite_shots"]["exact"] = R["vqc_test_acc"]
res["finite_shots_seconds"] = round(time.time() - t0, 1)

# ---------------- Lab 5.4: kernel bandwidth
bw = {}
for c in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0):
    Ktr = Q.qkernel(c * Q.Xtr, c * Q.Xtr); Kte = Q.qkernel(c * Q.Xte, c * Q.Xtr)
    off = Ktr[~np.eye(len(Ktr), dtype=bool)]
    svm = SVC(kernel="precomputed", C=1.0).fit(Ktr, Q.ytr)
    bw[str(c)] = dict(test_acc=float(svm.score(Kte, Q.yte)), train_acc=float(svm.score(Ktr, Q.ytr)),
                      mean_offdiag=float(off.mean()), sd_offdiag=float(off.std()))
res["bandwidth"] = bw
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "fourier"} | {"fourier_power_within": res["fourier"]["power_fraction_within_allowed"]}, indent=1))
