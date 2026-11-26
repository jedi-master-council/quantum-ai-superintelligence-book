"""Chapter 5 lab: train a small quantum neural network and compare it with classical models.

Data: the two-moons data set (scikit-learn), 200 training and 200 test points.
Quantum models (simulated exactly with a small state-vector simulator written in NumPy):
  * variational quantum classifier (VQC): 2 qubits, data re-uploading, 3 layers, 18 parameters,
    trained with exact parameter-shift gradients and the Adam optimiser;
  * quantum kernel support vector machine: fidelity kernel of a 2-qubit feature map.
Classical baselines: logistic regression, a support vector machine with an RBF kernel,
and a small multilayer perceptron.
The trained VQC is then evaluated with Qiskit under the noise model of IBM Fez.
Tested with qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime 0.52.1, scikit-learn 1.x.
"""
import json, time, warnings
import numpy as np
warnings.filterwarnings("ignore")
from sklearn.datasets import make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

SEED = 5
rng = np.random.default_rng(SEED)
X, y = make_moons(n_samples=400, noise=0.15, random_state=SEED)
X = (X - X.min(0)) / (X.max(0) - X.min(0)) * np.pi          # scale features to [0, pi]
Xtr, ytr, Xte, yte = X[:200], y[:200], X[200:], y[200:]

# ---------------- minimal 2-qubit state-vector simulator ----------------
I2 = np.eye(2)
def ry(t): c, s = np.cos(t / 2), np.sin(t / 2); return np.array([[c, -s], [s, c]], dtype=complex)
def rz(t): return np.array([[np.exp(-1j * t / 2), 0], [0, np.exp(1j * t / 2)]], dtype=complex)
CZ = np.diag([1, 1, 1, -1]).astype(complex)
Z0 = np.kron(np.diag([1, -1]), I2)           # Z on qubit 0 (first tensor factor)
L = 3                                         # layers
NP = L * 6                                    # parameters: per layer RY, RZ on each qubit plus RY after CZ

def vqc_state(x, th):
    psi = np.zeros(4, dtype=complex); psi[0] = 1
    th = th.reshape(L, 6)
    for l in range(L):
        psi = np.kron(ry(x[0]), ry(x[1])) @ psi                     # data re-uploading
        psi = np.kron(ry(th[l, 0]), ry(th[l, 1])) @ psi
        psi = np.kron(rz(th[l, 2]), rz(th[l, 3])) @ psi
        psi = CZ @ psi
        psi = np.kron(ry(th[l, 4]), ry(th[l, 5])) @ psi
    return psi

def vqc_out(x, th):
    psi = vqc_state(x, th)
    return np.real(np.conj(psi) @ Z0 @ psi)    # expectation in [-1, 1]

def loss_and_grad(th, Xb, yb):
    t = 1 - 2 * yb                             # class 0 -> +1, class 1 -> -1
    out = np.array([vqc_out(x, th) for x in Xb])
    loss = np.mean((out - t) ** 2)
    g = np.zeros_like(th)
    for k in range(len(th)):                   # parameter-shift rule, exact for these gates
        e = np.zeros_like(th); e[k] = np.pi / 2
        op = np.array([vqc_out(x, th + e) for x in Xb]); om = np.array([vqc_out(x, th - e) for x in Xb])
        g[k] = np.mean(2 * (out - t) * (op - om) / 2)
    return loss, g

def train_vqc(epochs=60, lr=0.05):
    th = rng.uniform(0, 2 * np.pi, NP); m = np.zeros(NP); v = np.zeros(NP); hist = []
    for ep in range(1, epochs + 1):
        idx = rng.permutation(len(Xtr))
        for b in range(0, len(idx), 25):
            bi = idx[b:b + 25]
            loss, g = loss_and_grad(th, Xtr[bi], ytr[bi])
            m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g ** 2
            th -= lr * (m / (1 - 0.9 ** ep)) / (np.sqrt(v / (1 - 0.999 ** ep)) + 1e-8)
        acc_tr = np.mean((np.array([vqc_out(x, th) for x in Xtr]) < 0) == ytr)
        acc_te = np.mean((np.array([vqc_out(x, th) for x in Xte]) < 0) == yte)
        full_loss = np.mean((np.array([vqc_out(x, th) for x in Xtr]) - (1 - 2 * ytr)) ** 2)
        hist.append({"epoch": ep, "loss": float(full_loss), "train_acc": float(acc_tr), "test_acc": float(acc_te)})
    return th, hist

# ---------------- quantum kernel ----------------
def fmap(x):
    psi = np.zeros(4, dtype=complex); psi[0] = 1
    for _ in range(2):
        psi = np.kron(ry(x[0]), ry(x[1])) @ psi
        psi = CZ @ psi
        psi = np.kron(rz(x[0] * x[1]), I2) @ psi
    return psi

def qkernel(A, B):
    SA = np.array([fmap(a) for a in A]); SB = np.array([fmap(b) for b in B])
    return np.abs(SA.conj() @ SB.T) ** 2

# ---------------- noisy evaluation with Qiskit ----------------
def vqc_qiskit(x, th):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2, 1); th = th.reshape(L, 6)
    # Qiskit orders qubits little-endian; qubit 1 in Qiskit is the first tensor factor above
    for l in range(L):
        qc.ry(x[0], 1); qc.ry(x[1], 0)
        qc.ry(th[l, 0], 1); qc.ry(th[l, 1], 0)
        qc.rz(th[l, 2], 1); qc.rz(th[l, 3], 0)
        qc.cz(0, 1)
        qc.ry(th[l, 4], 1); qc.ry(th[l, 5], 0)
    qc.measure(1, 0)
    return qc

def noisy_eval(th, shots=1000):
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeFez
    be = FakeFez(); sim = AerSimulator.from_backend(be, seed_simulator=SEED)
    circs = transpile([vqc_qiskit(x, th) for x in Xte], be, optimization_level=1, seed_transpiler=SEED)
    res = sim.run(circs, shots=shots).result()
    exp = np.array([(res.get_counts(i).get("0", 0) - res.get_counts(i).get("1", 0)) / shots for i in range(len(Xte))])
    ideal = np.array([vqc_out(x, th) for x in Xte])
    return float(np.mean((exp < 0) == yte)), exp.tolist(), ideal.tolist()

if __name__ == "__main__":
    out = {}
    t0 = time.time(); th, hist = train_vqc(); out["vqc_train_seconds"] = round(time.time() - t0, 1)
    out["vqc_history"] = hist; out["vqc_params"] = NP
    out["vqc_test_acc"] = hist[-1]["test_acc"]; out["vqc_train_acc"] = hist[-1]["train_acc"]
    Ktr, Kte = qkernel(Xtr, Xtr), qkernel(Xte, Xtr)
    qsvm = SVC(kernel="precomputed", C=1.0).fit(Ktr, ytr); out["qkernel_test_acc"] = float(qsvm.score(Kte, yte))
    lr = LogisticRegression().fit(Xtr, ytr); out["logistic_test_acc"] = float(lr.score(Xte, yte)); out["logistic_params"] = 3
    svm = SVC(kernel="rbf", C=1.0, gamma="scale").fit(Xtr, ytr); out["rbf_svm_test_acc"] = float(svm.score(Xte, yte))
    weak = MLPClassifier(hidden_layer_sizes=(8,), max_iter=3000, random_state=SEED).fit(Xtr, ytr)
    out["mlp_untuned_test_acc"] = float(weak.score(Xte, yte))      # default settings, unscaled inputs
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler().fit(Xtr)
    mlp = MLPClassifier(hidden_layer_sizes=(8,), activation="tanh", solver="lbfgs", max_iter=5000,
                        random_state=SEED).fit(sc.transform(Xtr), ytr)
    out["mlp_test_acc"] = float(mlp.score(sc.transform(Xte), yte))
    out["mlp_params"] = int(sum(w.size for w in mlp.coefs_) + sum(b.size for b in mlp.intercepts_))
    acc, exp, ideal = noisy_eval(th); out["vqc_noisy_fez_test_acc"] = acc
    out["vqc_noisy_mean_abs_shift"] = float(np.mean(np.abs(np.array(exp) - np.array(ideal))))
    gx = np.linspace(0, np.pi, 60)
    out["grid"] = {"x": gx.tolist(), "vqc": [[float(vqc_out(np.array([a, b]), th)) for a in gx] for b in gx]}
    out["test_points"] = {"X": Xte.tolist(), "y": yte.tolist()}
    out["theta"] = th.tolist()
    json.dump(out, open("lab5_results.json", "w"))
    for k, v in out.items():
        if not isinstance(v, (list, dict)):
            print(k, v)
