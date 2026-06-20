# smg_metrics

> **S**ymbolic **M**usic **G**eneration **Metrics** — 51 objective evaluation metrics, zero config.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENCE)
[![PyPI version](https://img.shields.io/pypi/v/smg-metrics.svg)](https://pypi.org/project/smg-metrics/)

**8 categories, 51 metrics, 20 papers/projects (1990–2026), fully typed & tested.**

| Category | Count | Latest source | Year |
|----------|-------|---------------|------|
| A. Single-file Quality | 13 | [MusPy](https://arxiv.org/abs/2008.01951) | 2020 |
| B. Note-level Pairwise | 5 | [Ou et al.](https://arxiv.org/abs/2408.15176) | 2025 |
| C. Bar-level Pairwise | 2 | [MuseMorphose](https://arxiv.org/abs/2105.04090) | 2023 |
| D. Chord-level Pairwise | 1 | [GETMusic](https://arxiv.org/abs/2305.10841) | 2023 |
| E. Distribution-level | 6 | [FGG](https://arxiv.org/abs/2410.08435) | 2025 |
| F. Advanced | 14 | [Text2midi](https://arxiv.org/abs/2412.16526) | 2025 |
| G. Structural | 4 | [MuseTok](https://arxiv.org/abs/2510.16273) | 2026 |
| H. Rhythmic/Temporal | 6 | [D3PIA](https://github.com/jech2/D3PIA) | 2026 |

## Quick Start

```bash
pip install smg-metrics
```

```python
from smg_metrics import single_file, single_file_rhythmic, pair_eval

quality = single_file("generated.mid")
print(quality.pce, quality.ebr, quality.gs)

rhythm = single_file_rhythmic("generated.mid")
print(rhythm.mean_ioi, rhythm.rhythmic_density)

pair = pair_eval("generated.mid", "reference.mid")
print(pair.note_f1, pair.sim_chr, pair.ca, pair.note_overlap)
```

```bash
smg-eval --music generated.mid
smg-eval --music gen.mid --pred gen.mid --ref ref.mid --dist --advanced --structural --rhythmic
```

## Installation

```bash
pip install smg-metrics

# Or install from source:
git clone https://github.com/OlyMarco/smg_metric.git
cd smg_metric && pip install -e .
```

| Package | Version | Purpose |
|---------|---------|---------|
| [`muspy`](https://github.com/salu133445/muspy) | >= 0.5.0 | 13 single-file quality metrics |
| [`miditoolkit`](https://github.com/music-x-lab/midi-toolkit) | >= 1.0 | MIDI parsing |
| [`pretty-midi`](https://github.com/craffel/pretty-midi) | >= 0.2.10 | Bar-level similarity parsing |
| [`mir-eval`](https://github.com/craffel/mir_eval) | >= 0.7 | Note-overlap metric |
| `numpy` | >= 1.24 | Numerical computation |
| `scipy` | >= 1.10 | Scientific computing |

## Python API

```python
from smg_metrics import (
    single_file,                # 13 MusPy quality metrics
    single_file_structural,     # 2 structural single-file metrics
    single_file_rhythmic,       # 4 D3PIA-style rhythmic metrics
    pair_eval,                  # 10 core pairwise metrics
    pair_eval_structural,       # 2 structural pairwise metrics
    distribution_eval,          # 6 distribution-level metrics
    advanced_eval,              # 14 advanced metrics
)
```

| Container | Fields | Count |
|-----------|--------|-------|
| `SingleFileResult` | pce, ebr, gs, sc, pisr, polyphony, polyphony_rate, pitch_range, n_pitches_used, n_pitch_classes_used, emr, pe, dpc | 13 |
| `StructuralSingleResult` | che, ngram_div | 2 |
| `RhythmicResult` | mean_ioi, rhythmic_intensity, rhythmic_density, voice_number | 4 |
| `PairResult` | note_f1, notei_f1, mel_f1, i_iou, ver, sim_chr, sim_grv, ca, onset_xor, note_overlap | 10 |
| `StructuralPairResult` | melody_match, tonal_dist | 2 |
| `DistributionResult` | pd, dd, ook, sc_sim, pce_sim, gs_sim | 6 |
| `AdvancedResult` | kl_duration, kl_ioi, kl_pitch, oa_duration, oa_ioi, oa_pitch_range, oa_density, ci_precision, ci_recall, ci_f1, cts, cr_pred, cr_ref, recon_acc | 14 |

Every result container is a frozen dataclass with `.to_dict()`.

### Individual metrics

```python
from smg_metrics import (
    chord_histogram_entropy, ngram_diversity,
    melody_matchness, tonal_distance,
    compute_ca, midi_to_chords,
    mean_ioi, rhythmic_intensity, rhythmic_density,
    voice_number, onset_xor_distance, note_overlap,
)

che = chord_histogram_entropy("file.mid")
div = ngram_diversity("file.mid", n=4)
ca = compute_ca("pred.mid", "ref.mid")
ioi = mean_ioi("file.mid")
xor = onset_xor_distance("pred.mid", "ref.mid")
nov = note_overlap("pred.mid", "ref.mid")
```

## CLI Usage

```bash
# Single-file quality (13 metrics)
smg-eval --music generated.mid

# Single-file quality + structural + rhythmic (19 metrics)
smg-eval --music generated.mid --structural --rhythmic

# Pairwise core (10 metrics)
smg-eval --pred gen.mid --ref ref.mid

# Full 51-metric run for one generated/reference pair
smg-eval --music gen.mid --pred gen.mid --ref ref.mid --dist --advanced --structural --rhythmic

# JSON output
smg-eval --pred gen.mid --ref ref.mid --json

# Batch directory
smg-eval --pred_dir ./pred/ --ref_dir ./ref/
```

| Flag | Description | Default |
|------|-------------|---------|
| `--music PATH` | Single-file mode | -- |
| `--pred PATH` | Predicted MIDI for pair mode | -- |
| `--ref PATH` | Reference MIDI for pair mode | -- |
| `--pred_dir DIR` | Batch predicted directory | -- |
| `--ref_dir DIR` | Batch reference directory | -- |
| `--root INT` | Root pitch for PISR | `0` |
| `--mode {major,minor}` | Scale mode for PISR | `major` |
| `--dist` | Include distribution-level metrics | `false` |
| `--advanced` | Include advanced metrics | `false` |
| `--structural` | Include structural metrics | `false` |
| `--rhythmic` | Include rhythmic/temporal metrics | `false` |
| `--json` | Output as JSON | `false` |

## Metrics Reference

### A. Single-file Quality (13)

Source: [MusPy](https://github.com/salu133445/muspy) / ISMIR 2020.

| Metric | Symbol | Range |
|--------|--------|-------|
| Pitch Class Entropy | PCE | [0, log2(12)] |
| Empty Beat Rate | EBR | [0, 1] |
| Groove Consistency | GS | [0, 1] |
| Scale Consistency | SC | [0, 1] |
| Pitch-in-Scale Rate | PISR | [0, 1] |
| Polyphony | Poly | [0, inf) |
| Polyphony Rate | PR | [0, 1] |
| Pitch Range | Range | [0, 127] |
| Unique Pitches | N_p | [0, 128] |
| Unique Pitch Classes | N_pc | [0, 12] |
| Empty Measure Rate | EMR | [0, 1] |
| Pitch Entropy | PE | [0, 7] |
| Drum Pattern Consistency | DPC | [0, 1] |

### B. Note-level Pairwise (5)

Source: [Ou et al.](https://arxiv.org/abs/2408.15176), Appendix C.

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Note F1 | F1 | [0, 1] | Quantised onset + pitch F1 |
| Notei F1 | F1i | [0, 1] | Note F1 plus instrument |
| Melody F1 | F1mel | [0, 1] | Note F1 on detected melody track |
| Instrument IoU | I-IoU | [0, 1] | Instrument set IoU |
| Voice Error Rate | VER | [0, inf) | Normalised voice-order edit distance |

### B2. Pairwise Rhythmic (2)

Sources: [D3PIA](https://github.com/jech2/D3PIA), [mir_eval](https://github.com/craffel/mir_eval).

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Onset XOR Distance | XOR | [0, 1] | Full-piece aligned binary onset-pattern XOR distance |
| Note Overlap | NOvlp | [0, 1] | mir_eval transcription average overlap |

### C. Bar-level Pairwise (2)

Source: [MuseMorphose](https://arxiv.org/abs/2105.04090).

| Metric | Symbol | Range |
|--------|--------|-------|
| Chroma Similarity | simChr | [0, 1] |
| Groove Similarity | simGrv | [0, 1] |

### D. Chord-level Pairwise (1)

Source: [GETMusic](https://arxiv.org/abs/2305.10841), Eq. 6.

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Chord Accuracy | CA | [0, 1] | Per-measure chord label match rate with Viterbi HMM chord recognition |

### E. Distribution-level (6)

Sources: [SongMASS](https://arxiv.org/abs/2012.05168), [FGG](https://arxiv.org/abs/2410.08435).

| Metric | Range | Description |
|--------|-------|-------------|
| PD | [0, 1] | Pitch distribution overlap |
| DD | [0, 1] | Duration distribution overlap |
| OOK | [0, 1] | Out-of-key rate on active 16th-note steps |
| SC_sim | [0, 1] | Scale consistency similarity |
| PCE_sim | [0, 1] | Pitch-class entropy similarity |
| GS_sim | [0, 1] | Groove consistency similarity |

### F. Advanced Metrics (14)

Sources: rule-guided diffusion, Text2midi, MuseTok.

| Group | Metrics |
|-------|---------|
| KL divergence | kl_duration, kl_ioi, kl_pitch |
| Overlapping area | oa_duration, oa_ioi, oa_pitch_range, oa_density |
| Instrument coverage | ci_precision, ci_recall, ci_f1 |
| Metadata / repetition / reconstruction | cts, cr_pred, cr_ref, recon_acc |

### G. Structural Metrics (4)

| Metric | Type | Range |
|--------|------|-------|
| Chord Histogram Entropy | Single | [0, log2(C)] |
| N-gram Diversity | Single | [0, 1] |
| Melody Matchness | Pair | [0, 1] |
| Tonal Distance | Pair | [0, inf) |

### H. Rhythmic & Temporal Metrics (4 single-file + 2 pairwise)

Sources: [D3PIA](https://github.com/jech2/D3PIA), [mir_eval](https://github.com/craffel/mir_eval).

| Metric | Symbol | Type | Range |
|--------|--------|------|-------|
| Mean Inter-Onset Interval | IOI | Single | [0, inf) |
| Rhythmic Intensity | RI | Single | [0, inf) |
| Rhythmic Density | RD | Single | [0, 1] |
| Voice Number | VN | Single | [0, inf) |
| Onset XOR Distance | XOR | Pair | [0, 1] |
| Note Overlap | NOvlp | Pair | [0, 1] |

## Research Notes

- FGG uses POP909 accompaniment generation at 16th-note resolution and reports % out-of-key notes, direct chord accuracy, chord progression similarity, chord IoU, and piano-roll IoU. The package implements the reproducible local-MIDI parts of that evaluation: OOK, Viterbi chord accuracy, pitch/duration overlaps, note overlap, and structural similarities.
- The FGG paper’s arXiv HTML reports Table 1 values: FGG % out-of-key notes 0.0%, direct chord accuracy 0.485, chord similarity 0.767, chord IoU 0.769, and piano-roll IoU 0.281; GETMusic scores lower on the same table. These values are model-generation results, not hard-coded package tests.
- D3PIA’s demo page exposes POP909 sample MIDI for GT, D3PIA, Polyffusion, C&E-E, WholeSongGen, FGG, and leadsheet models; the validation procedure can download those MIDIs and run `pair_eval()` / `compute_ca()` locally.

## Package Structure

```
smg_metric/
|-- pyproject.toml
|-- README.md
|-- test.py                    # Full 51-metric test script
|-- data/                      # Classical + POP909 MIDI test files
|-- smg_metrics/
|   |-- __init__.py            # Public API exports
|   |-- __main__.py            # python -m smg_metrics
|   |-- py.typed               # PEP 561 marker
|   |-- _io.py                 # Shared MIDI I/O
|   |-- _stats.py              # Shared statistics
|   |-- _edit.py               # Shared sequence editing
|   |-- single.py              # single_file wrappers
|   |-- pair.py                # pair_eval wrappers
|   |-- rhythmic.py            # D3PIA + mir_eval rhythmic metrics
|   |-- muspy_ext.py           # 13 MusPy metrics
|   |-- note_f1.py             # 5 note-level pairwise metrics
|   |-- similarity.py          # 2 bar-level similarity metrics
|   |-- chord_accuracy.py      # Chord Accuracy HMM
|   |-- distribution.py        # 6 distribution-level metrics
|   |-- advanced.py            # 14 advanced metrics
|   |-- structural.py          # 4 structural metrics
|   +-- cli.py                 # CLI entry point
```

## Testing

```bash
python test.py
python test.py data/
python test.py --single-only file.mid
python test.py --pair-only pred.mid ref.mid
```

`test.py` validates:

1. Single-file quality (13 metrics × N files)
2. Single-file structural (2 metrics × N files)
3. Single-file rhythmic/temporal (4 metrics × N files)
4. Pairwise note/rhythmic/bar/chord/structural/distribution/advanced (32 metrics × N pairs)
5. Self-consistency (12 checks × N files)

## Citation

If you use this toolkit, cite the relevant metric sources for the categories used:

```bibtex
@article{dong2020muspy,
  title={MusPy: A Toolkit for Symbolic Music Generation},
  author={Dong, Hao and others},
  journal={Proc. ISMIR},
  year={2020},
  url={https://arxiv.org/abs/2008.01951}
}

@article{zhu2025fgg,
  title={Efficient Fine-Grained Guidance for Diffusion Model Based Symbolic Music Generation},
  author={Zhu, Tingyu and Liu, Haoyu and Wang, Ziyu and Jiang, Zhimin and Zheng, Zeyu},
  journal={Proc. ICML},
  year={2025},
  url={https://arxiv.org/abs/2410.08435}
}

@inproceedings{choi2026d3pia,
  title={D3PIA: A Discrete Denoising Diffusion Model for Piano Accompaniment Generation from Lead Sheet},
  author={Choi, Eunjin and Kim, Hounsu and Bang, Hayeon and Kwon, Taegyun and Nam, Juhan},
  booktitle={Proc. ICASSP},
  year={2026}
}

@inproceedings{raffel2014mir_eval,
  title={mir_eval: A Transparent Implementation of Common MIR Metrics},
  author={Raffel, Colin and others},
  booktitle={Proc. ISMIR},
  year={2014}
}
```

## License

MIT. See [LICENCE](LICENCE).
