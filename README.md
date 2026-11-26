# Quantum AI and the Road to Superintelligence: companion code

Companion repository for the book *Quantum AI and the Road to Superintelligence: AGI, the Quantum Brain and the Technological Singularity, with Hands-On Labs on Free Quantum Computers* by Petar Radanliev (Springer, in preparation).

The repository holds the code for the labs, the scripts that draw every original figure in the book, and the data those figures use. It is maintained after publication: when a quantum computing platform changes its interface, allowance or software, the changes are recorded here.

## Contents

| Folder | What it holds |
|---|---|
| `labs/chapter-02/` | Lab 2.1: a personal AGI forecast combining a survey fit, a compute-threshold model and a task-horizon model |
| `labs/chapter-03/` | Lab 3.1 (an entangled pair, ideal and noisy) and Lab 3.2 (how noise grows with the circuit) |
| `labs/chapter-04/` | Grover's search on 2 to 5 qubits, ideal and under the IBM Fez and Sherbrooke noise models |
| `labs/chapter-05/` | A small quantum neural network and a quantum kernel against classical baselines |
| `labs/chapter-06/` | Barren plateaus: gradient variance against qubit number and circuit depth |
| `labs/chapter-07/` | AI for quantum computing: learned error correction of results and a learned decoder |
| `labs/chapter-08/` | The build roadmap: milestone dates with and without quantum relief |
| `labs/chapter-09/` | Dating a singularity-type transition (imports the Chapter 2 forecast) |
| `labs/chapter-10/` | A spiking network in NumPy, a quantum neuron under noise, and a brain-emulation timeline |
| `labs/chapter-11/` | Protecting a model file with hybrid post-quantum cryptography, and Mosca's inequality for AI assets |
| `figures/` | Scripts that draw the book's original figures at printed size, and the shared style with the book's colour key |
| `figures/data/` | Data used by the figures, produced by the labs |

Each lab writes its results to a JSON file beside the script; copying that file into `figures/data/` and rerunning the figure script redraws the printed figure from the reader's own run.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python labs/chapter-03/lab3_bell_ghz.py
```

The labs run on a laptop simulator at no cost. Running them on real quantum hardware needs a free account with a provider; Chapter 3 of the book explains how to open one.

## Reproducing the figures

```bash
cd figures
python figs_ch1.py out
python figs_ch2.py out ../labs/chapter-02/agi_forecast.py
python figs_ch3_12.py out
for n in 4 5 6 7 8 9 10 11; do python figs_ch$n.py out; done
```

Each figure is written as PDF, SVG, PNG and TIFF. The figures use the Liberation Serif typeface at 11 pt, which has the same letter widths as the Times New Roman used in the book's text; install it (it is free) to reproduce the figures exactly.

## Colour key

Every figure uses the same colours for the same ideas: grey for today's AI and classical computing, blue for artificial general intelligence, orange for superintelligence, purple for the technological singularity, green for quantum hardware and quantum machine intelligence, teal for minds and brains, red for security and control, and dashed yellow for results not yet shown. The values are defined once, in `figures/figstyle.py`.

## Tested versions

| Package | Version |
|---|---|
| qiskit | 2.6.2 |
| qiskit-aer | 0.18.4 |
| qiskit-ibm-runtime | 0.52.1 |

Last tested on 26 November 2026. With these versions and the fixed seeds in the code, the labs reproduce the results printed in the book exactly.

## Licence

The code is released under the MIT licence (see `LICENSE`). The text and figures of the book are not part of this repository and remain under the publisher's copyright.

## Citation

See `CITATION.cff`.
