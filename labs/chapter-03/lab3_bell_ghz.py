# Tested with qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime 0.52.1 (26 November 2026).
# Reproduces the results printed in Chapter 3 exactly (fixed seeds).
"""Lab 3: first circuits. Runs on a laptop with Qiskit and Qiskit Aer.
Ideal simulation, then the same circuits under a noise model built from
calibration data of an IBM processor (fake backend snapshot shipped with
qiskit-ibm-runtime). Swap in a real backend with the commented lines."""
import json, warnings
warnings.filterwarnings("ignore")
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez

SHOTS = 4000

def bell():
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1); qc.measure([0, 1], [0, 1])
    return qc

def ghz(n):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure(range(n), range(n))
    return qc

ideal = AerSimulator(seed_simulator=7)
fake = FakeFez()
noisy = AerSimulator.from_backend(fake, seed_simulator=7)

out = {"shots": SHOTS, "noise_model_source": fake.name}
qc = bell()
out["bell_ideal"] = ideal.run(transpile(qc, ideal), shots=SHOTS).result().get_counts()
tq = transpile(qc, fake, optimization_level=1, seed_transpiler=7)
out["bell_noisy"] = noisy.run(tq, shots=SHOTS).result().get_counts()
out["bell_transpiled_ops"] = dict(tq.count_ops())
out["bell_transpiled_depth"] = tq.depth()

ghz_rows = []
for n in range(2, 13):
    t = transpile(ghz(n), fake, optimization_level=1, seed_transpiler=7)
    c = noisy.run(t, shots=SHOTS).result().get_counts()
    good = c.get("0" * n, 0) + c.get("1" * n, 0)
    ghz_rows.append({"n": n, "p_correct": good / SHOTS, "two_qubit_gates": sum(v for k, v in t.count_ops().items() if k in ("cz", "cx", "ecr")), "depth": t.depth()})
out["ghz"] = ghz_rows
json.dump(out, open("lab3_results.json", "w"), indent=1)
print(bell().draw(output="text"))
print(json.dumps(out, indent=1))

# To run on a real IBM processor instead (needs a free IBM Quantum Platform account):
# from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
# service = QiskitRuntimeService()            # after save_account(token=..., ...)
# backend = service.least_busy(operational=True, simulator=False)
# job = SamplerV2(mode=backend).run([transpile(bell(), backend)], shots=SHOTS)
# print(job.result()[0].data.c.get_counts())
