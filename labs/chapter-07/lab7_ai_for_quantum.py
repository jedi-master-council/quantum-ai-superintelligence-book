"""Chapter 7 labs: machine learning that improves quantum results.

Lab 7.1  Learned error mitigation. 4-qubit random circuits are run ideally and under the noise
         model of IBM Fez. A neural network learns to map noisy output distributions to ideal ones.
         It is compared with no correction and with standard readout-error mitigation
         (inverting the 16 x 16 readout assignment matrix measured with calibration circuits).
         Test set: unseen random circuits of the same family, and GHZ circuits it never saw.
Lab 7.2  A learned decoder for a distance-5 repetition code under correlated noise.
         Compared with the standard minimum-weight decoder, which assumes independent errors.
Tested with qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime 0.52.1, scikit-learn 1.9.
"""
import json, warnings
import numpy as np
warnings.filterwarnings("ignore")
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez
from sklearn.neural_network import MLPRegressor

SEED, N, SHOTS = 7, 4, 4000
rng = np.random.default_rng(SEED)
D = 2 ** N

def random_circuit():
    qc = QuantumCircuit(N)
    for _ in range(2):
        for q in range(N):
            qc.ry(rng.uniform(0, np.pi), q)
        for q in range(N - 1):
            qc.cz(q, q + 1)
    for q in range(N):
        qc.ry(rng.uniform(0, np.pi), q)
    return qc

def ghz():
    qc = QuantumCircuit(N); qc.h(0)
    for q in range(N - 1):
        qc.cx(q, q + 1)
    return qc

def probs_ideal(qc):
    return Statevector.from_instruction(qc).probabilities()      # index = little-endian bit string

def run_noisy(circs, be, sim):
    meas = []
    for qc in circs:
        m = qc.copy(); m.measure_all(); meas.append(m)
    t = transpile(meas, be, optimization_level=1, seed_transpiler=SEED)
    res = sim.run(t, shots=SHOTS).result()
    out = []
    for i in range(len(circs)):
        p = np.zeros(D)
        for k, v in res.get_counts(i).items():
            p[int(k.replace(" ", ""), 2)] += v / SHOTS
        out.append(p)
    return np.array(out)

def tvd(p, q):
    return 0.5 * np.abs(p - q).sum(axis=-1)

def lab_7_1():
    be = FakeFez(); sim = AerSimulator.from_backend(be, seed_simulator=SEED)
    train = [random_circuit() for _ in range(400)]
    test = [random_circuit() for _ in range(100)]
    P_tr, P_te = np.array([probs_ideal(c) for c in train]), np.array([probs_ideal(c) for c in test])
    N_tr, N_te = run_noisy(train, be, sim), run_noisy(test, be, sim)
    g = [ghz()]; P_g = np.array([probs_ideal(c) for c in g]); N_g = run_noisy(g, be, sim)
    # readout calibration: prepare each basis state and measure
    cal = []
    for b in range(D):
        qc = QuantumCircuit(N)
        for q in range(N):
            if (b >> q) & 1:
                qc.x(q)
        cal.append(qc)
    A = run_noisy(cal, be, sim).T              # column b = distribution observed when b prepared
    Ainv = np.linalg.pinv(A)
    def ro(p):
        x = np.clip(p @ Ainv.T, 0, None); return x / x.sum(axis=-1, keepdims=True)
    # learn the correction (ideal minus noisy) from the noisy distribution
    model = MLPRegressor(hidden_layer_sizes=(64,), max_iter=5000, random_state=SEED, alpha=1e-3,
                         learning_rate_init=1e-3, tol=1e-7)
    model.fit(N_tr, P_tr - N_tr)
    def ml(p):
        x = np.clip(p + model.predict(p), 0, None); return x / x.sum(axis=-1, keepdims=True)
    out = {}
    for name, Pn, Pi in [("random_test", N_te, P_te), ("ghz", N_g, P_g)]:
        out[name] = {"raw": float(tvd(Pn, Pi).mean()), "readout": float(tvd(ro(Pn), Pi).mean()),
                     "ml": float(tvd(ml(Pn), Pi).mean())}
    out["calibration_circuits"] = D; out["training_circuits"] = len(train); out["test_circuits"] = len(test)
    out["ghz_example"] = {"ideal": P_g[0].tolist(), "raw": N_g[0].tolist(), "readout": ro(N_g)[0].tolist(), "ml": ml(N_g)[0].tolist()}
    return out

def lab_7_2(p=0.04, q=0.04, d=5, n_train=200_000, n_test=200_000):
    """Bit-flip repetition code. Independent flips with prob p on each data bit, plus
    correlated flips of neighbouring pairs with prob q on each adjacent pair (crosstalk)."""
    def sample(n):
        e = (rng.random((n, d)) < p).astype(int)
        pairs = (rng.random((n, d - 1)) < q).astype(int)
        for i in range(d - 1):
            e[:, i] ^= pairs[:, i]; e[:, i + 1] ^= pairs[:, i]
        syn = e[:, :-1] ^ e[:, 1:]
        logical = e[:, 0].copy()   # which of the two error patterns consistent with the syndrome occurred
        return syn, e, logical
    def mw_decode(syn):
        # The two error patterns consistent with a syndrome are corr (with first bit 0) and its complement.
        # Minimum weight chooses the lighter; returns 1 if it chooses the complement (first bit flipped).
        n = syn.shape[0]; corr = np.zeros((n, d), dtype=int)
        for i in range(1, d):
            corr[:, i] = corr[:, i - 1] ^ syn[:, i - 1]
        w = corr.sum(axis=1)
        return (w > d // 2).astype(int)
    syn_tr, _, lg_tr = sample(n_train)
    keys_tr = syn_tr @ (1 << np.arange(d - 1))
    table = np.zeros(2 ** (d - 1), dtype=int)
    for k in range(2 ** (d - 1)):          # learned decoder: most frequent logical outcome per syndrome
        m = keys_tr == k
        table[k] = int(lg_tr[m].mean() > 0.5) if m.any() else 0
    syn_te, e_te, lg_te = sample(n_test)
    keys_te = syn_te @ (1 << np.arange(d - 1))
    # residual logical error: decoder prediction disagrees with actual majority flip
    mw_err = float(np.mean(mw_decode(syn_te) != lg_te))
    ml_err = float(np.mean(table[keys_te] != lg_te))
    return {"p": p, "q": q, "distance": d, "minimum_weight_logical_error": mw_err, "learned_logical_error": ml_err,
            "physical_flip_rate_per_bit": float(e_te.mean()), "train_samples": n_train, "test_samples": n_test,
            "syndromes_where_decoders_differ": int(np.sum(table != np.array([mw_decode(np.array([[ (k >> i) & 1 for i in range(d - 1)]]))[0] for k in range(2 ** (d - 1))])))}

if __name__ == "__main__":
    out = {"lab7_1": lab_7_1()}
    print(json.dumps(out["lab7_1"], indent=1)[:600])
    out["lab7_2_sweep"] = [lab_7_2(p=0.02, q=q) for q in (0.0, 0.02, 0.04, 0.06, 0.08)]
    for r in out["lab7_2_sweep"]:
        print(r)
    json.dump(out, open("lab7_results.json", "w"), indent=1)
