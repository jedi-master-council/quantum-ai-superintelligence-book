"""Chapter 6, Labs 6.2 to 6.4: noise-induced barren plateaus, the cost of loading data, and the
cost of error mitigation.

Lab 6.2  Noise-induced barren plateau (Wang et al. 2021). A 6-qubit hardware-efficient circuit with a
         LOCAL cost, simulated with density matrices. After every layer each qubit suffers depolarising
         noise of strength p. The variance of the gradient of the first parameter is measured over 200
         random parameter settings for depths 1 to 20 and p = 0, 0.01, 0.03.
Lab 6.3  Cost of amplitude encoding. Qiskit's StatePreparation loads a random complex vector of length
         N = 2^n into n qubits; the circuit is compiled to CX and single-qubit gates and the CX gates are
         counted for n = 1 to 10. Angle encoding of the same number of features is shown for comparison.
Lab 6.4  Zero-noise extrapolation on GHZ states under the IBM Fez noise model. Every two-qubit gate of the
         compiled circuit is repeated 1, 3 or 5 times (each CZ is its own inverse, so the ideal circuit is
         unchanged and the noise is scaled), and the probability of a correct outcome is extrapolated to zero
         noise with a quadratic (Richardson) fit. The factor by which extrapolation inflates the statistical
         variance is reported.
Tested with numpy 2.x, qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime 0.52.1.
"""
import json, sys
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "lab6_extensions_results.json"
res = {}
rng = np.random.default_rng(66)

# ---------------------------------------------------------------- Lab 6.2
print("Lab 6.2 ...")
n = 6; D = 2 ** n
def ry(t): c, s = np.cos(t / 2), np.sin(t / 2); return np.array([[c, -s], [s, c]], dtype=complex)
def rz(t): return np.array([[np.exp(-1j * t / 2), 0], [0, np.exp(1j * t / 2)]], dtype=complex)
idx = np.arange(D); czd = np.ones(D)
for q in range(n - 1):
    b1 = (idx >> (n - 1 - q)) & 1; b2 = (idx >> (n - 2 - q)) & 1
    czd *= np.where((b1 & b2) == 1, -1, 1)
def layer_U(th):            # th: (n, 2)
    U = np.array([[1.0 + 0j]])
    for q in range(n):
        U = np.kron(U, rz(th[q, 1]) @ ry(th[q, 0]))
    return czd[:, None] * U
def depolarise(rho, p):
    if p == 0: return rho
    r = rho.reshape([2] * (2 * n))
    for q in range(n):
        red = np.trace(r, axis1=q, axis2=q + n)                   # trace out qubit q
        mixed = np.multiply.outer(np.eye(2) / 2, red)              # axes: q, q', others...
        # move the new axes into position q (row) and q + n (column)
        mixed = np.moveaxis(mixed, [0, 1], [q, q + n])
        r = (1 - p) * r + p * mixed
    return r.reshape(D, D)
Pz = [np.diag(((idx >> (n - 1 - q)) & 1) == 0).astype(float) for q in range(n)]
def local_cost(rho): return 1 - np.mean([np.real(np.trace(P @ rho)) for P in Pz])
def run(theta, layers, p):
    rho = np.zeros((D, D), dtype=complex); rho[0, 0] = 1
    th = theta.reshape(layers, n, 2)
    for l in range(layers):
        U = layer_U(th[l]); rho = depolarise(U @ rho @ U.conj().T, p)
    return local_cost(rho)
noise = {}
DEPTHS = (1, 2, 4, 8, 12, 16, 20)
for p in (0.0, 0.01, 0.03):
    row = {}
    for L in DEPTHS:
        g = []
        for _ in range(200):
            th = rng.uniform(0, 2 * np.pi, L * n * 2); e = np.zeros_like(th); e[0] = np.pi / 2
            g.append((run(th + e, L, p) - run(th - e, L, p)) / 2)
        row[str(L)] = float(np.var(g))
    noise[str(p)] = row
    print(p, row)
res["noise_plateau"] = dict(qubits=n, samples=200, variance=noise)

# ---------------------------------------------------------------- Lab 6.3
print("Lab 6.3 ...")
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import StatePreparation
load = []
for k in range(1, 11):
    v = rng.standard_normal(2 ** k) + 1j * rng.standard_normal(2 ** k); v /= np.linalg.norm(v)
    qc = QuantumCircuit(k); qc.append(StatePreparation(v), range(k))
    t = transpile(qc, basis_gates=["cx", "u"], optimization_level=1)
    ops = t.count_ops()
    load.append(dict(qubits=k, amplitudes=2 ** k, cx=int(ops.get("cx", 0)), single=int(ops.get("u", 0)), depth=t.depth()))
    print(load[-1])
res["amplitude_encoding"] = load

# ---------------------------------------------------------------- Lab 6.4
print("Lab 6.4 ...")
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez
be = FakeFez(); sim = AerSimulator.from_backend(be, seed_simulator=7)
def ghz(m):
    qc = QuantumCircuit(m, m); qc.h(0)
    for i in range(m - 1): qc.cx(i, i + 1)
    qc.measure(range(m), range(m)); return qc
def fold(tc, lam):
    out = tc.copy_empty_like()
    for ins in tc.data:
        reps = lam if ins.operation.name == "cz" else 1
        for _ in range(reps): out.append(ins.operation, ins.qubits, ins.clbits)
    return out
lams = np.array([1, 3, 5]); coef = np.array([15, -10, 3]) / 8          # Richardson weights for 1, 3, 5 -> 0
SH = 8000; zne = []
for m in (2, 4, 6, 8, 10):
    tc = transpile(ghz(m), be, optimization_level=1, seed_transpiler=1)
    vals = []
    for lam in lams:
        c = sim.run(fold(tc, lam), shots=SH).result().get_counts()
        vals.append((c.get("0" * m, 0) + c.get("1" * m, 0)) / SH)
    est = float(coef @ np.array(vals))
    zne.append(dict(qubits=m, two_qubit_gates=int(tc.count_ops().get("cz", 0)), raw=vals[0], folded3=vals[1], folded5=vals[2],
                    extrapolated=est))
    print(zne[-1])
res["zne"] = dict(scales=lams.tolist(), weights=coef.tolist(), variance_inflation=float(np.sum(coef ** 2)),
                  shots_per_scale=SH, results=zne)
json.dump(res, open(OUT, "w"), indent=1)
