"""Chapter 7, Labs 7.3 and 7.4: learning a faster gate, and searching for a cheaper compilation.

Lab 7.3  Model-free calibration of a single-qubit X gate on a simulated transmon. The transmon is a
         three-level system (states 0, 1 and the leakage state 2) with anharmonicity -300 MHz. Its true
         frequency is 2 MHz away from the value the controller assumes, standing in for drift.
         Three pulses are compared at durations from 4 to 24 ns:
           (a) a Gaussian pulse calibrated from the nominal model (area pi, no correction);
           (b) the same with the textbook DRAG correction for leakage, still from the nominal model;
           (c) a pulse whose amplitude, DRAG coefficient and frequency offset are tuned by a black-box
               optimiser (Nelder-Mead) that sees only the measured gate error, as a learning agent would.
         Gate error = 1 - average gate fidelity on the qubit subspace; leakage is also reported.
Lab 7.4  Searching compilations. Three circuits are compiled for IBM Fez with the default stochastic
         layout and routing (one seed) and with the best of 100 seeds, and the two-qubit gate counts and
         the probability of a correct result under the Fez noise model are compared.
"""
import json, sys
import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

OUT = sys.argv[1] if len(sys.argv) > 1 else "lab7_extensions_results.json"
res = {}

# ---------------------------------------------------------------- Lab 7.3
print("Lab 7.3 ...")
alpha = -2 * np.pi * 0.300            # rad/ns
drift = 2 * np.pi * 0.002             # true detuning unknown to the controller, rad/ns
a = np.diag([1, np.sqrt(2)], 1).astype(complex); ad = a.conj().T
N3 = np.diag([0, 1, 2]).astype(complex)
H_static = alpha / 2 * (N3 @ N3 - N3) + drift * N3
X_t = np.array([[0, 1], [1, 0]], dtype=complex)
DT = 0.05
def evolve(T, amp, beta, dphi):
    steps = int(round(T / DT)); t = (np.arange(steps) + 0.5) * DT
    s = T / 4; g = np.exp(-(t - T / 2) ** 2 / (2 * s ** 2)); g0 = np.exp(-(T / 2) ** 2 / (2 * s ** 2))
    env = (g - g0); env /= env.sum() * DT                   # unit area
    denv = np.gradient(env, DT)
    U = np.eye(3, dtype=complex)
    for k in range(steps):
        ox = amp * np.pi * env[k]; oy = beta * amp * np.pi * denv[k]
        H = H_static - dphi * N3 + ox / 2 * (a + ad) + oy / 2 * 1j * (ad - a)
        U = expm(-1j * H * DT) @ U
    return U
def error(U):
    M = X_t.conj().T @ U[:2, :2]
    F = (np.real(np.trace(M @ M.conj().T)) + abs(np.trace(M)) ** 2) / 6
    leak = 1 - np.mean([np.sum(abs(U[:2, j]) ** 2) for j in range(2)])
    return 1 - F, leak
rows = []
for T in (4, 6, 8, 10, 12, 16, 20, 24):
    e_g, l_g = error(evolve(T, 1.0, 0.0, 0.0))
    b0 = -1 / (2 * alpha)
    e_d, l_d = error(evolve(T, 1.0, b0, 0.0))
    f = lambda x: error(evolve(T, x[0], x[1], x[2]))[0]
    best = minimize(lambda x: np.log10(f(x) + 1e-12), [1.0, b0, 0.0], method="Nelder-Mead",
                    options=dict(maxiter=400, xatol=1e-5, fatol=1e-4))
    e_l, l_l = error(evolve(T, *best.x))
    rows.append(dict(duration_ns=T, gaussian_error=e_g, gaussian_leak=l_g, drag_error=e_d, drag_leak=l_d,
                     learned_error=e_l, learned_leak=l_l, evaluations=int(best.nfev), learned_params=best.x.tolist()))
    print({k: (round(v, 7) if isinstance(v, float) else v) for k, v in rows[-1].items() if k != "learned_params"})
res["calibration"] = dict(anharmonicity_MHz=-300, drift_MHz=2, rows=rows)

# ---------------------------------------------------------------- Lab 7.4
print("Lab 7.4 ...")
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez
be = FakeFez(); sim = AerSimulator.from_backend(be, seed_simulator=3)
def qft_test(n):                      # QFT, barrier, inverse QFT: ideal output is |0..0>; the barrier stops cancellation
    qc = QuantumCircuit(n, n); qc.x(range(0, n, 2)); qc.append(QFTGate(n), range(n)); qc.barrier()
    qc.append(QFTGate(n).inverse(), range(n)); qc.x(range(0, n, 2)); qc.measure(range(n), range(n)); return qc
def bv(n, secret=None):               # Bernstein-Vazirani: every data qubit interacts with one ancilla
    secret = secret or "1" * n
    qc = QuantumCircuit(n + 1, n); qc.x(n); qc.h(range(n + 1))
    for i, bit in enumerate(reversed(secret)):
        if bit == "1": qc.cx(i, n)
    qc.h(range(n)); qc.measure(range(n), range(n)); return qc, secret
def mirror_random(n, seed=11):
    rng = np.random.default_rng(seed); qc = QuantumCircuit(n)
    for _ in range(4):
        for q in range(n): qc.u(*rng.uniform(0, 2 * np.pi, 3), q)
        perm = rng.permutation(n)
        for i in range(0, n - 1, 2): qc.cx(perm[i], perm[i + 1])
    full = QuantumCircuit(n, n); full.compose(qc, inplace=True); full.barrier(); full.compose(qc.inverse(), inplace=True)
    full.measure(range(n), range(n)); return full
bvc, bvs = bv(8)
tests = {"QFT and inverse, 6 qubits": (qft_test(6), "0" * 6), "Bernstein-Vazirani, 8 + 1 qubits": (bvc, bvs),
         "random mirror circuit, 8 qubits": (mirror_random(8), "0" * 8)}
comp = {}
for name, (qc, target) in tests.items():
    def cost(t): return int(t.count_ops().get("cz", 0))
    default = transpile(qc, be, optimization_level=3, seed_transpiler=0)
    cands = [transpile(qc, be, optimization_level=3, seed_transpiler=s) for s in range(100)]
    counts = [cost(t) for t in cands]; best = cands[int(np.argmin(counts))]; worst = cands[int(np.argmax(counts))]
    def success(t):
        c = sim.run(t, shots=8000).result().get_counts(); return c.get(target, 0) / 8000
    comp[name] = dict(default_cz=cost(default), best_cz=min(counts), worst_cz=max(counts), median_cz=float(np.median(counts)),
                      default_success=success(default), best_success=success(best), worst_success=success(worst),
                      seeds_at_best=int(np.sum(np.array(counts) == min(counts))))
    print(name, comp[name])
res["compilation_search"] = comp
json.dump(res, open(OUT, "w"), indent=1)
