"""Chapter 4, Labs 4.3 and 4.4: Shor's algorithm in miniature, and simulating a quantum magnet.

Lab 4.3  Order finding for N = 15 with a = 7, the textbook demonstration of Shor's algorithm. Four counting
         qubits and four work qubits; the controlled multiplications by 7^(2^j) mod 15 use the compiled
         permutation circuits found in introductory texts, which already encode knowledge of the answer
         (Smolin, Smith and Vargo 2013). Run ideally and under the IBM Fez noise model. A shot is useful when
         it gives the period r = 4 by the continued-fraction step (measured phase 4/16 or 12/16).
Lab 4.4  Time evolution of a four-spin transverse-field Ising chain, H = -J sum Z_i Z_(i+1) - h sum X_i, with
         J = h = 1, from the all-up state. The exact average magnetisation <Z> is compared with first-order
         Trotter circuits of step 0.25, simulated ideally and under the Fez noise model, for times up to 2.5.
"""
import json, sys
import numpy as np
from fractions import Fraction
from scipy.linalg import expm
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez

OUT = sys.argv[1] if len(sys.argv) > 1 else "lab4_extensions_results.json"
be = FakeFez(); noisy = AerSimulator.from_backend(be, seed_simulator=41); ideal = AerSimulator(seed_simulator=41)
res = {}

# ---------------------------------------------------------------- Lab 4.3
def c_amod15(a, power):
    U = QuantumCircuit(4)
    for _ in range(power):
        if a in (2, 13): U.swap(2, 3); U.swap(1, 2); U.swap(0, 1)
        if a in (7, 8): U.swap(0, 1); U.swap(1, 2); U.swap(2, 3)
        if a in (4, 11): U.swap(1, 3); U.swap(0, 2)
        if a in (7, 11, 13):
            for q in range(4): U.x(q)
    g = U.to_gate(); g.name = f"{a}^{power} mod 15"
    return g.control()
nc = 4
qc = QuantumCircuit(nc + 4, nc)
qc.h(range(nc)); qc.x(nc)                      # work register = 1
for j in range(nc):
    qc.append(c_amod15(7, 2 ** j), [j] + [nc + i for i in range(4)])
qc.append(QFTGate(nc).inverse(), range(nc))
qc.measure(range(nc), range(nc))
def analyse(counts):
    shots = sum(counts.values()); out = {}; useful = 0
    for b, c in counts.items():
        k = int(b, 2); out[k] = out.get(k, 0) + c / shots
        r = Fraction(k, 2 ** nc).limit_denominator(15).denominator
        if r == 4: useful += c
    return out, useful / shots
ti = transpile(qc, ideal, optimization_level=1)
ci = ideal.run(ti, shots=8000).result().get_counts()
tn = transpile(qc, be, optimization_level=3, seed_transpiler=4)
cn = noisy.run(tn, shots=8000).result().get_counts()
di, ui = analyse(ci); dn, un = analyse(cn)
res["shor15"] = dict(counting_qubits=nc, two_qubit_gates_fez=int(tn.count_ops().get("cz", 0)), depth_fez=tn.depth(),
                     ideal_distribution={str(k): v for k, v in sorted(di.items())},
                     fez_distribution={str(k): v for k, v in sorted(dn.items())},
                     useful_fraction_ideal=ui, useful_fraction_fez=un,
                     factors_from_r4=[int(np.gcd(7 ** 2 - 1, 15)), int(np.gcd(7 ** 2 + 1, 15))])
print({k: v for k, v in res["shor15"].items() if "distribution" not in k})

# ---------------------------------------------------------------- Lab 4.4
n, J, h, dt = 4, 1.0, 1.0, 0.25
I2 = np.eye(2); X = np.array([[0, 1], [1, 0]]); Z = np.diag([1, -1])
def op(single, i):
    m = np.array([[1.0]])
    for k in range(n): m = np.kron(m, single if k == i else I2)
    return m
H = sum(-J * op(Z, i) @ op(Z, i + 1) for i in range(n - 1)) + sum(-h * op(X, i) for i in range(n))
Mz = sum(op(Z, i) for i in range(n)) / n
psi0 = np.zeros(2 ** n); psi0[0] = 1
times = [dt * k for k in range(11)]
exact = [float(np.real((expm(-1j * H * t) @ psi0).conj() @ Mz @ (expm(-1j * H * t) @ psi0))) for t in times]
def trotter(steps):
    c = QuantumCircuit(n, n)
    for _ in range(steps):
        for i in range(n - 1): c.rzz(-2 * J * dt, i, i + 1)
        for i in range(n): c.rx(-2 * h * dt, i)
    c.measure(range(n), range(n)); return c
def mag(counts):
    s = sum(counts.values()); return sum(c * np.mean([1 - 2 * int(b) for b in key]) for key, c in counts.items()) / s
tro_ideal, tro_fez, gates = [], [], []
for k in range(len(times)):
    c = trotter(k)
    tro_ideal.append(float(mag(ideal.run(transpile(c, ideal), shots=8000).result().get_counts())))
    t = transpile(c, be, optimization_level=1, seed_transpiler=4); gates.append(int(t.count_ops().get("cz", 0)))
    tro_fez.append(float(mag(noisy.run(t, shots=8000).result().get_counts())))
res["ising"] = dict(qubits=n, J=J, h=h, dt=dt, times=times, exact=exact, trotter_ideal=tro_ideal, trotter_fez=tro_fez, two_qubit_gates=gates,
                    max_trotter_error=float(np.max(np.abs(np.array(tro_ideal) - np.array(exact)))),
                    max_noise_error=float(np.max(np.abs(np.array(tro_fez) - np.array(tro_ideal)))))
print({k: (np.round(v, 3).tolist() if isinstance(v, list) else v) for k, v in res["ising"].items()})
json.dump(res, open(OUT, "w"), indent=1)
