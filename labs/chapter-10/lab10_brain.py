"""Chapter 10 labs: a spiking network, a brain-scale cost estimate, a connectome-growth
scenario model, and a toy quantum neuron.

Lab 10.1  Leaky integrate-and-fire (LIF) network of excitatory and inhibitory neurons in NumPy
          (Brunel-style sparse random network driven by Poisson input). Measures firing rates,
          irregularity and the wall-clock cost of each simulated second at several sizes, and
          scales the cost to a human brain at the same (LIF) level of detail.
Lab 10.2  The quantum perceptron of Tacchino et al. (2019) with 4 and 8 binary inputs (3 and 4
          qubits including the ancilla), simulated ideally and under the FakeFez noise model.
Lab 10.3  Monte Carlo scenario model for the date of whole-mouse and human connectomes, starting
          from the largest published connectome in 2025 (MICrONS, about 0.5 billion synapses).
          All growth assumptions are the author's and are stated below.
Results are written to JSON under the keys "spiking", "human_lif_flops", "quantum_neuron" and "timeline".
Tested with numpy 2.x, qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime 0.52.1.
"""
import json, sys, time
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "lab10_results.json"
res = {}

# ---------------------------------------------------------------- Lab 10.1
def lif_network(N, T=1.0, dt=1e-4, g=8.0, nu_rel=2.0, seed=1, KE=400, KI=100, CX=1000, D=1.5e-3):
    """Brunel-style E/I network of LIF neurons with fixed in-degree (KE excitatory and KI inhibitory
    inputs per neuron), a synaptic delay D and CX external Poisson inputs per neuron firing at
    nu_rel times the rate that would just bring a neuron to threshold on its own."""
    rng = np.random.default_rng(seed)
    NE = int(0.8 * N); NI = N - NE
    tau, vth, vreset, tref = 20e-3, 20.0, 10.0, 2e-3          # s, mV, mV, s
    J = 0.2                                                   # mV, excitatory PSP
    W = np.zeros((N, N), dtype=np.float32)                    # rows = sources, columns = targets
    for t in range(N):
        e = rng.choice(NE, KE, replace=False); i = NE + rng.choice(NI, KI, replace=False)
        W[e, t] = J; W[i, t] = -g * J
    nsyn = N * (KE + KI)
    nu_thr = vth / (J * CX * tau)                             # Hz per external input
    lam = nu_rel * nu_thr * CX * dt
    v = rng.uniform(vreset, vth, N).astype(np.float32)
    refr = np.zeros(N)
    steps = int(T / dt); nd = int(round(D / dt))
    buf = [np.zeros(N, dtype=bool) for _ in range(nd)]
    spikes_t, spikes_i = [], []
    events = 0
    t0 = time.perf_counter()
    for s in range(steps):
        arriving = buf[s % nd]
        if arriving.any():
            I_rec = W[arriving].sum(0); events += int(arriving.sum()) * (KE + KI)
        else:
            I_rec = np.zeros(N, dtype=np.float32)
        ext = rng.poisson(lam, N) * J
        active = refr <= 0
        v[active] += -v[active] * dt / tau + I_rec[active] + ext[active]
        refr -= dt
        spk = v >= vth
        buf[s % nd] = spk                                    # delivered nd steps later
        if spk.any():
            idx = np.nonzero(spk)[0]
            spikes_t.append(np.full(idx.size, s * dt)); spikes_i.append(idx)
            v[spk] = vreset; refr[spk] = tref
    wall = time.perf_counter() - t0
    st = np.concatenate(spikes_t) if spikes_t else np.array([]); si = np.concatenate(spikes_i).astype(int) if spikes_i else np.array([], int)
    rates = np.bincount(si, minlength=N) / T
    cvs = []
    for i in range(N):
        ti = st[si == i]
        if ti.size > 3:
            isi = np.diff(ti); cvs.append(isi.std() / isi.mean())
    keep = st < 0.25
    return dict(N=N, synapses=nsyn, rate_E=float(rates[:NE].mean()), rate_I=float(rates[NE:].mean()),
                cv_isi=float(np.mean(cvs)) if cvs else None, wall_s=wall, events=events,
                raster=(st[keep].tolist(), si[keep].tolist()) if N == 1000 else None)

print("Lab 10.1 ...")
runs = [lif_network(N) for N in (1000, 2000, 4000, 8000)]
DRIVES = (0.8, 1.0, 1.5, 2.0, 3.0, 4.0)
drive = [lif_network(1000, nu_rel=nu, seed=2) for nu in DRIVES]
r1000 = [r for r in runs if r["N"] == 1000][0]
res["spiking"] = dict(
    sizes=[{k: r[k] for k in ("N", "synapses", "rate_E", "rate_I", "cv_isi", "wall_s", "events")} for r in runs],
    drive=[{"nu_rel": nu, "rate_E": r["rate_E"], "rate_I": r["rate_I"], "cv_isi": r["cv_isi"]}
           for nu, r in zip(DRIVES, drive)],
    raster=r1000["raster"])
# laptop throughput at the largest size: neuron updates and delivered synaptic events per wall second
big = runs[-1]
res["spiking"]["laptop_neuron_updates_per_s"] = big["N"] * 1e4 / big["wall_s"]
res["spiking"]["laptop_events_per_s"] = big["events"] / big["wall_s"]

# Brain-scale arithmetic at LIF level of detail (inputs are published orders of magnitude)
human = dict(neurons=86e9, synapses_low=1e14, synapses_high=1e15, rate_low=0.1, rate_high=2.0)
dt_steps = 1e4                          # 0.1 ms time step
flop_neuron_step = 5                    # multiply-adds per LIF update (order of magnitude)
flop_syn_event = 2                      # one multiply-add per delivered spike
neur = human["neurons"] * dt_steps * flop_neuron_step
syn_lo = human["synapses_low"] * human["rate_low"] * flop_syn_event
syn_hi = human["synapses_high"] * human["rate_high"] * flop_syn_event
res["human_lif_flops"] = dict(neuron_updates=neur, synaptic_low=syn_lo, synaptic_high=syn_hi,
                              total_low=neur + syn_lo, total_high=neur + syn_hi,
                              memory_bytes_low=human["synapses_low"] * 4, memory_bytes_high=human["synapses_high"] * 4)

# ---------------------------------------------------------------- Lab 10.3
print("Lab 10.3 (timeline) ...")
rng = np.random.default_rng(10)
S = 100_000
start_year, start_syn = 2025.0, 5e8          # MICrONS (2025): about 0.5 billion synapses
mouse_syn = 10 ** rng.uniform(np.log10(5e10), np.log10(2e11), S)     # assumption: whole mouse brain
human_syn = 10 ** rng.uniform(14, 15, S)                              # whole human brain
T10 = rng.uniform(3.0, 8.0, S)          # years per tenfold increase in largest connectome (author's assumption)
lag = rng.uniform(2.0, 10.0, S)         # years from connectome to validated emulation (author's assumption)
mouse_conn = start_year + T10 * np.log10(mouse_syn / start_syn)
human_conn = start_year + T10 * np.log10(human_syn / start_syn)
def q(a): return [float(np.percentile(a, p)) for p in (10, 50, 90)]
res["timeline"] = dict(assumptions=dict(start_year=start_year, start_synapses=start_syn, years_per_tenfold=[3, 8],
                                       mouse_synapses=[5e10, 2e11], human_synapses=[1e14, 1e15], emulation_lag_years=[2, 10]),
                      mouse_connectome=q(mouse_conn), mouse_emulation=q(mouse_conn + lag),
                      human_connectome=q(human_conn), human_emulation=q(human_conn + lag),
                      p_human_emulation_by=dict((str(y), float(np.mean(human_conn + lag <= y))) for y in (2050, 2060, 2075, 2100)),
                      cdf_years=list(range(2025, 2121)),
                      cdf_mouse=[float(np.mean(mouse_conn + lag <= y)) for y in range(2025, 2121)],
                      cdf_human=[float(np.mean(human_conn + lag <= y)) for y in range(2025, 2121)])

# ---------------------------------------------------------------- Lab 10.2
print("Lab 10.2 (quantum neuron) ...")
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeFez

def neuron_circuit(i_vec, w_vec):
    n = int(np.log2(len(i_vec)))
    qc = QuantumCircuit(n + 1, 1)
    qc.h(range(n))
    qc.append(DiagonalGate([complex(s) for s in i_vec]), list(range(n)))          # input state |psi_i>
    qc.append(DiagonalGate([complex(s) for s in w_vec]), list(range(n)))          # U_w: undo weight signs
    qc.h(range(n)); qc.x(range(n))                                                # ... and map |psi_w> to |1...1>
    qc.mcx(list(range(n)), n)                                                     # ancilla flips if all ones
    qc.measure(n, 0)
    return qc

fake = FakeFez(); noise = NoiseModel.from_backend(fake)
ideal_sim = AerSimulator(); noisy_sim = AerSimulator(noise_model=noise)
SHOTS = 4000
lab3 = {}
for n in (2, 3):
    m = 2 ** n
    w = np.array([1, -1] * (m // 2))                                              # fixed weight pattern
    allin = [np.array([1 - 2 * ((k >> j) & 1) for j in range(m)]) for k in range(2 ** m)]
    if n == 3:
        sel = np.random.default_rng(3).choice(len(allin), 48, replace=False)
        allin = [allin[k] for k in sel] + [w, -w]
    ideal, meas_i, meas_n, twoq = [], [], [], []
    for idx, iv in enumerate(allin):
        qc = neuron_circuit(iv, w)
        ideal.append(float((iv @ w / m) ** 2))
        ti = transpile(qc, ideal_sim, optimization_level=1, seed_transpiler=1)
        ci = ideal_sim.run(ti, shots=SHOTS, seed_simulator=7 + idx).result().get_counts()
        meas_i.append(ci.get("1", 0) / SHOTS)
        tn = transpile(qc, fake, optimization_level=3, seed_transpiler=1)
        twoq.append(sum(v for k, v in tn.count_ops().items() if k in ("cz", "ecr", "cx")))
        cn = noisy_sim.run(tn, shots=SHOTS, seed_simulator=1007 + idx).result().get_counts()
        meas_n.append(cn.get("1", 0) / SHOTS)
    ideal, meas_i, meas_n = map(np.array, (ideal, meas_i, meas_n))
    fire_true = ideal > 0.5
    lab3[str(m)] = dict(qubits=n + 1, inputs=len(allin), two_qubit_gates_mean=float(np.mean(twoq)),
                        mae_ideal_sim=float(np.abs(meas_i - ideal).mean()), mae_fez=float(np.abs(meas_n - ideal).mean()),
                        fire_accuracy_fez=float(np.mean((meas_n > 0.5) == fire_true)),
                        mean_output_when_match_fez=float(meas_n[ideal > 0.99].mean()),
                        by_level={f"{lv:.4f}": [int(np.sum(np.isclose(ideal, lv))), float(meas_n[np.isclose(ideal, lv)].mean()),
                                                float(meas_n[np.isclose(ideal, lv)].min()), float(meas_n[np.isclose(ideal, lv)].max())]
                                  for lv in sorted(set(np.round(ideal, 4)))},
                        mean_output_orthogonal_fez=float(meas_n[ideal == 0].mean()),
                        points=[[float(a), float(b)] for a, b in zip(ideal, meas_n)])
res["quantum_neuron"] = lab3
json.dump(res, open(OUT, "w"), indent=1)
print("spiking:", [(r["N"], round(r["rate_E"], 1), round(r["wall_s"], 2)) for r in res["spiking"]["sizes"]])
print("timeline:", {k: res["timeline"][k] for k in ("mouse_emulation", "human_emulation", "p_human_emulation_by")})
print("quantum neuron:", {k: {a: b for a, b in v.items() if a != "points"} for k, v in res["quantum_neuron"].items()})
