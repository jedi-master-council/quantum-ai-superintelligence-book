# Quantum AI and the Road to Superintelligence: companion code

Companion repository for the book *Quantum AI and the Road to Superintelligence: AGI, the Quantum Brain and the Technological Singularity, with Hands-On Labs on Free Quantum Computers* by Petar Radanliev (Springer, in preparation).

The repository holds the code for the labs, the scripts that draw every original figure in the book, and the data those figures use. It is maintained after publication: when a quantum computing platform changes its interface, allowance or software, the changes are recorded here.

## Contents

| Folder | What it holds |
|---|---|
| `labs/chapter-03/` | Lab 3.1 (an entangled pair, ideal and noisy) and Lab 3.2 (how noise grows with the circuit) |
| `figures/` | Scripts that draw the book's original figures at printed size, and the shared style with the book's colour key |
| `figures/data/` | Data used by the figures, produced by the labs |

Further chapters are added as they are completed.

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
python figs_ch3_12.py out
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
