"""Chapter 4 labs: Grover's search, ideal and noisy, on two processor noise models.

Lab 4.1  Success probability against the number of Grover iterations (3 qubits).
Lab 4.2  Success probability at the optimal number of iterations, for 2 to 5 qubits,
         on an ideal simulator and under the noise models of two IBM processors:
         IBM Fez (Heron family, 2024) and IBM Sherbrooke (Eagle family, 2023).
Runs on a laptop; no quantum hardware or allowance is used.
Tested with qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime 0.52.1.
"""
import json, math, warnings
warnings.filterwarnings("ignore")
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import ZGate
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeSherbrooke

SHOTS, SEED = 4000, 11

def phase_flip_all_ones(qc, n):
    """Multi-controlled Z on all n qubits: flips the phase of |11...1>."""
    if n == 1:
        qc.z(0)
    else:
        qc.append(ZGate().control(n - 1), list(range(n)))

def grover(n, marked, iterations):
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(iterations):
        # oracle: map the marked string to all ones, flip its phase, map back
        for i, b in enumerate(reversed(marked)):
            if b == "0":
                qc.x(i)
        phase_flip_all_ones(qc, n)
        for i, b in enumerate(reversed(marked)):
            if b == "0":
                qc.x(i)
        # diffuser: reflection about the uniform superposition
        qc.h(range(n)); qc.x(range(n))
        phase_flip_all_ones(qc, n)
        qc.x(range(n)); qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def optimal_iterations(n):
    return max(1, math.floor(math.pi / 4 * math.sqrt(2 ** n)))

def run(qc, backend, sim):
    t = transpile(qc, backend, optimization_level=3, seed_transpiler=SEED) if backend else transpile(qc, sim)
    counts = sim.run(t, shots=SHOTS).result().get_counts()
    two_q = sum(v for k, v in t.count_ops().items() if k in ("cz", "cx", "ecr")) if backend else None
    return counts, two_q, (t.depth() if backend else None)

if __name__ == "__main__":
    ideal = AerSimulator(seed_simulator=SEED)
    procs = {"fez": FakeFez(), "sherbrooke": FakeSherbrooke()}
    noisy = {k: AerSimulator.from_backend(b, seed_simulator=SEED) for k, b in procs.items()}
    out = {"shots": SHOTS}
    # Lab 4.1: iterations sweep, 3 qubits, marked 101
    marked = "101"; sweep = []
    for it in range(0, 7):
        qc = grover(3, marked, it)
        row = {"iterations": it, "theory": math.sin((2 * it + 1) * math.asin(1 / math.sqrt(8))) ** 2}
        c, _, _ = run(qc, None, ideal); row["ideal"] = c.get(marked, 0) / SHOTS
        c, g, d = run(qc, procs["fez"], noisy["fez"]); row["fez"] = c.get(marked, 0) / SHOTS; row["fez_2q"] = g
        sweep.append(row)
    out["sweep_3q"] = sweep
    # Lab 4.2: 2 to 5 qubits at optimal iterations, marked all-ones-and-zero pattern
    scale = []
    for n in range(2, 6):
        m = ("10" * n)[:n]
        k = optimal_iterations(n)
        qc = grover(n, m, k)
        row = {"n": n, "N": 2 ** n, "iterations": k, "random_guess": 1 / 2 ** n,
               "theory": math.sin((2 * k + 1) * math.asin(1 / math.sqrt(2 ** n))) ** 2}
        c, _, _ = run(qc, None, ideal); row["ideal"] = c.get(m, 0) / SHOTS
        for name in procs:
            c, g, d = run(qc, procs[name], noisy[name])
            row[name] = c.get(m, 0) / SHOTS; row[name + "_2q"] = g; row[name + "_depth"] = d
        scale.append(row); print(row)
    out["scaling"] = scale
    json.dump(out, open("lab4_results.json", "w"), indent=1)
    for r in sweep:
        print(r)
