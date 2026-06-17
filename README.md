# smg_metrics

> **S**ymbolic **M**usic **G**eneration **Metrics** — 45 objective evaluation metrics, zero config.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/smg-metrics.svg)](https://pypi.org/project/smg-metrics/)

**7 categories, 45 metrics, 18 papers (2006–2026), fully typed & tested.**

| Category | Count | Latest Paper | Year |
|----------|-------|-------------|------|
| A. Single-file Quality | 13 | [MusPy](https://arxiv.org/abs/2008.01951) | 2020 |
| B. Note-level Pairwise | 5 | [Ou et al., NeurIPS 2025](https://arxiv.org/abs/2408.15176) | 2025 |
| C. Bar-level Pairwise | 2 | [MuseMorphose](https://arxiv.org/abs/2105.04090) | 2023 |
| D. Chord-level Pairwise | 1 | [GETMusic](https://arxiv.org/abs/2305.10841) | 2023 |
| E. Distribution-level | 6 | [FGG](https://arxiv.org/abs/2410.08435) | 2025 |
| F. Advanced | 14 | [Text2midi](https://arxiv.org/abs/2412.16526) | 2025 |
| G. Structural | 4 | [MuseTok](https://arxiv.org/abs/2510.16273) | 2026 |

**Paper timeline:**
```
2006  Harte et al. (ACM MM) .............. Tonal Distance
2012  Papadopoulos & Peeters (ISMIR) ..... Chord Histogram Entropy
2016  Mogren (NeurIPS WS) ................ Scale Consistency (C-RNN-GAN)
2018  Dong et al. (AAAI) ................. MuseGAN metrics (PISR/PR/EMR/DPC)
      Dong et al. (ISMIR LBD) ............ Pypianoroll (EBR)
      Yang & Lerch (NCA) ................. N-gram Diversity
2020  MusPy (ISMIR) ...................... PCE/GS/PitchRange/PE/...
      Jazz Transformer (ISMIR) ............ Groove Consistency
      SongMASS + PopMAG (ACM-MM) ......... PD/DD/CA
2023  MuseMorphose (TASLP) ............... simChr/simgrv
      GETMusic (IJCAI) ................... Chord Accuracy (Viterbi HMM)
2024  SCG (ICML Oral) .................... KL/OA/CI/CTS
2025  FGG (ICML) ......................... OOK
      Text2midi (AAAI) ................... CR
      Ou et al. (NeurIPS) ................ Note F1/Mel F1/I-IoU/VER
2026  MuseTok (ICASSP) ................... ReconAcc
```

## Quick Start (30 seconds)

```bash
pip install smg-metrics
```

```python
from smg_metrics import single_file, pair_eval

# Single-file quality (13 metrics, no reference needed)
q = single_file("generated.mid")
print(q.pce, q.ebr, q.gs)

# Pairwise comparison (30 metrics: note + structural + distribution + advanced)
s = pair_eval("generated.mid", "reference.mid")
print(s.note_f1, s.sim_chr, s.ca)
```

```bash
# CLI
smg-eval --music generated.mid
smg-eval --pred gen.mid --ref ref.mid --dist --advanced --structural
```


## Table of Contents

1. [Installation](#1-installation)
2. [Python API](#2-python-api)
3. [CLI Usage](#3-cli-usage)
4. [Metrics Reference](#4-metrics-reference)
5. [Package Structure](#5-package-structure)
6. [Testing](#6-testing)
7. [Citation](#7-citation)


## 1. Installation

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
| [`pretty-midi`](https://github.com/craffel/pretty-midi) | >= 0.2.10 | MIDI parsing (similarity module) |
| `numpy` | >= 1.24 | Numerical computation |
| `scipy` | >= 1.10 | Scientific computing |


## 2. Python API

### High-level API

```python
from smg_metrics import (
    single_file,                # 13 MusPy quality metrics
    single_file_structural,     # 2 structural metrics (CHE, Ngram)
    pair_eval,                  # 8 pairwise metrics
    pair_eval_structural,       # 2 structural pairwise (MelodyMatch, TonalDist)
    distribution_eval,          # 6 distribution-level metrics
    advanced_eval,              # 14 advanced metrics
)

# Single-file
quality = single_file("output.mid")           # 13 metrics
struct  = single_file_structural("output.mid") # 2 metrics

# Pairwise (pred vs ref)
pair    = pair_eval("gen.mid", "ref.mid")            # 8 metrics
pstruct = pair_eval_structural("gen.mid", "ref.mid")  # 2 metrics
dist    = distribution_eval("gen.mid", "ref.mid")     # 6 metrics
adv     = advanced_eval("gen.mid", "ref.mid")         # 14 metrics
```

### Individual metrics

```python
from smg_metrics import (
    chord_histogram_entropy, ngram_diversity,
    melody_matchness, tonal_distance,
    compute_ca, midi_to_chords,
)

che  = chord_histogram_entropy("file.mid")          # Chord Histogram Entropy
div  = ngram_diversity("file.mid", n=4)             # N-gram diversity
mm   = melody_matchness("pred.mid", "ref.mid")      # Melody similarity
td   = tonal_distance("pred.mid", "ref.mid")        # Tonal distance
ca   = compute_ca("pred.mid", "ref.mid")            # Chord Accuracy
chords = midi_to_chords("file.mid")                 # Chord labels per bar
```

### Result containers

Every function returns a frozen dataclass with `.to_dict()`:

```python
quality = single_file("file.mid")
print(quality.pce)          # 3.16
print(quality.to_dict())    # {'pce': 3.16, 'ebr': 0.03, ...}
```

| Container | Fields | Count |
|-----------|--------|-------|
| `SingleFileResult` | pce, ebr, gs, sc, pisr, polyphony, polyphony_rate, pitch_range, n_pitches_used, n_pitch_classes_used, emr, pe, dpc | 13 |
| `StructuralSingleResult` | che, ngram_div | 2 |
| `PairResult` | note_f1, notei_f1, mel_f1, i_iou, ver, sim_chr, sim_grv, ca | 8 |
| `StructuralPairResult` | melody_match, tonal_dist | 2 |
| `DistributionResult` | pd, dd, ook, sc_sim, pce_sim, gs_sim | 6 |
| `AdvancedResult` | kl_duration, kl_ioi, kl_pitch, oa_duration, oa_ioi, oa_pitch_range, oa_density, ci_precision, ci_recall, ci_f1, cts, cr_pred, cr_ref, recon_acc | 14 |


## 3. CLI Usage

```bash
# Single-file (13 metrics)
smg-eval --music generated.mid

# Single-file + structural (15 metrics)
smg-eval --music generated.mid --structural

# Pairwise (8 metrics)
smg-eval --pred gen.mid --ref ref.mid

# All metrics (45 metrics)
smg-eval --music gen.mid --pred gen.mid --ref ref.mid --dist --advanced --structural

# JSON output
smg-eval --pred gen.mid --ref ref.mid --json

# Batch directory
smg-eval --pred_dir ./pred/ --ref_dir ./ref/
```

| Flag | Description | Default |
|------|-------------|---------|
| `--music PATH` | Single-file mode | -- |
| `--pred PATH` | Predicted MIDI (pair mode) | -- |
| `--ref PATH` | Reference MIDI (pair mode) | -- |
| `--pred_dir DIR` | Batch predicted directory | -- |
| `--ref_dir DIR` | Batch reference directory | -- |
| `--root INT` | Root pitch for PISR (0=C) | `0` |
| `--mode {major,minor}` | Scale mode for PISR | `major` |
| `--dist` | Include distribution-level metrics | `false` |
| `--advanced` | Include advanced metrics | `false` |
| `--structural` | Include structural metrics | `false` |
| `--json` | Output as JSON | `false` |


## 4. Metrics Reference

### A. Single-file Quality (13 metrics)

No reference file required. Source: [MusPy](https://github.com/salu133445/muspy) ([ISMIR 2020](https://arxiv.org/abs/2008.01951)).

| Metric | Symbol | Range | Paper |
|--------|--------|-------|-------|
| Pitch Class Entropy | PCE | [0, log2(12)] | [Jazz Transformer, ISMIR 2020](https://arxiv.org/abs/2008.01307) |
| Empty Beat Rate | EBR | [0, 1] | [Pypianoroll, ISMIR 2018](https://github.com/salu133445/pypianoroll) |
| Groove Consistency | GS | [0, 1] | [Jazz Transformer, ISMIR 2020](https://arxiv.org/abs/2008.01307) |
| Scale Consistency | SC | [0, 1] | [C-RNN-GAN, NeurIPS 2016 WS](https://arxiv.org/abs/1611.09904) |
| Pitch-in-Scale Rate | PISR | [0, 1] | [MuseGAN, AAAI 2018](https://arxiv.org/abs/1709.06298) |
| Polyphony | Poly | [1, inf) | [MuseGAN, AAAI 2018](https://arxiv.org/abs/1709.06298) |
| Polyphony Rate | PR | [0, 1] | [MuseGAN, AAAI 2018](https://arxiv.org/abs/1709.06298) |
| Pitch Range | Range | [0, 127] | [MusPy, ISMIR 2020](https://arxiv.org/abs/2008.01951) |
| Unique Pitches | N_p | [0, 128] | [MusPy, ISMIR 2020](https://arxiv.org/abs/2008.01951) |
| Unique Pitch Classes | N_pc | [0, 12] | [MusPy, ISMIR 2020](https://arxiv.org/abs/2008.01951) |
| Empty Measure Rate | EMR | [0, 1] | [MuseGAN, AAAI 2018](https://arxiv.org/abs/1709.06298) |
| Pitch Entropy | PE | [0, 7] | [MusPy, ISMIR 2020](https://arxiv.org/abs/2008.01951) |
| Drum Pattern Consistency | DPC | [0, 1] | [MuseGAN, AAAI 2018](https://arxiv.org/abs/1709.06298) |

### B. Pairwise Note-level (5 metrics)

Source: [Ou et al., NeurIPS 2025](https://arxiv.org/abs/2408.15176), Appendix C.

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Note F1 | F1 | [0, 1] | Note-level F1 (onset + pitch, 16th-note quantised) |
| Notei F1 | F1i | [0, 1] | Note F1 + correct instrument |
| Melody F1 | F1mel | [0, 1] | Note F1 on melody track only |
| Instrument IoU | I-IoU | [0, 1] | Instrument set intersection-over-union |
| Voice Error Rate | VER | [0, inf) | Normalised edit distance of voice ordering |

### C. Pairwise Bar-level (2 metrics)

Source: [MuseMorphose](https://arxiv.org/abs/2105.04090) (Wu & Yang, IEEE/ACM TASLP 2023).

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Chroma Similarity | simChr | [0, 1] | Bar-level pitch-class cosine similarity |
| Groove Similarity | simGrv | [0, 1] | Bar-level onset-pattern cosine similarity |

### D. Pairwise Chord-level (1 metric)

Source: [GETMusic](https://arxiv.org/abs/2305.10841) (Lv et al., IJCAI 2023), Eq. 6.

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Chord Accuracy | CA | [0, 1] | Per-measure chord label match rate (Viterbi HMM) |

### E. Distribution-level (6 metrics)

Sources: [SongMASS](https://arxiv.org/abs/2012.05168) (Ren et al., ACM-MM 2020), [FGG](https://arxiv.org/abs/2410.08435) (ICML 2025).

| Metric | Range | Description |
|--------|-------|-------------|
| PD | [0, 1] | Pitch Distribution overlap |
| DD | [0, 1] | Duration Distribution overlap |
| OOK | [0, 1] | Out-of-Key Rate (auto-detected key) |
| SC_sim | [0, 1] | Scale Consistency similarity |
| PCE_sim | [0, 1] | Pitch Class Entropy similarity |
| GS_sim | [0, 1] | Groove Consistency similarity |

### F. Advanced Metrics (14 metrics)

Sources: [Rule Guided Diffusion](https://arxiv.org/abs/2402.14285) (ICML 2024), [Text2midi](https://arxiv.org/abs/2412.16526) (AAAI 2025), [MuseTok](https://arxiv.org/abs/2510.16273) (ICASSP 2026).

| Metric | Range | Description | Source |
|--------|-------|-------------|--------|
| KL Duration | [0, inf) | KL divergence of duration distributions | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| KL IOI | [0, inf) | KL divergence of IOI distributions | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| KL Pitch | [0, inf) | KL divergence of pitch distributions | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| OA Duration | [0, 1] | Overlapping area of mean duration | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| OA IOI | [0, 1] | Overlapping area of mean IOI | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| OA Pitch Range | [0, 1] | Overlapping area of pitch range | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| OA Density | [0, 1] | Overlapping area of note density | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| CI Precision | [0, 1] | Instrument coverage precision | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| CI Recall | [0, 1] | Instrument coverage recall | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| CI F1 | [0, 1] | Instrument coverage F1 | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| CTS | {0, 1, NaN} | Correct Time Signature | [rule-guided-music](https://github.com/yjhuangcd/rule-guided-music) |
| CR Pred | [0, inf) | Compression ratio (predicted) | [Text2midi](https://github.com/AMAAI-Lab/Text2midi) |
| CR Ref | [0, inf) | Compression ratio (reference) | [Text2midi](https://github.com/AMAAI-Lab/Text2midi) |
| ReconAcc | [0, 1] | Reconstruction accuracy (edit distance) | [MuseTok](https://github.com/Yuer867/MuseTok) |

### G. Structural Metrics (4 metrics)

| Metric | Type | Range | Paper |
|--------|------|-------|-------|
| Chord Histogram Entropy | Single | [0, log2(C)] | [Papadopoulos & Peeters, ISMIR 2012](https://www.researchgate.net/publication/262080861_Large-scale_Study_of_Chord_Estimation_Algorithms_Based_on_Chroma) |
| N-gram Diversity | Single | [0, 1] | [Yang & Lerch, NCA 2018](https://link.springer.com/article/10.1007/s00521-018-3759-5) |
| Melody Matchness | Pair | [0, 1] | [Mongeau & Sankoff, CH 1990](https://doi.org/10.1007/BF02137351) |
| Tonal Distance | Pair | [0, inf) | [Harte et al., ACM MM 2006](https://dl.acm.org/doi/10.1145/1178723.1178727) |


## 5. Package Structure

```
smg_metric/
|-- pyproject.toml          # Package metadata & dependencies
|-- README.md               # This file
|-- test.py                 # Full 45-metric test script (165 tests)
|-- data/                   # Test MIDI files (classical piano)
|-- smg_metrics/            # Main package (v0.3.0)
|   |-- __init__.py         # Public API exports (45 metrics)
|   |-- __main__.py         # python -m smg_metrics
|   |-- py.typed            # PEP 561 marker
|   |-- _io.py              # Shared MIDI I/O (Note3/Note4, extract, quantise)
|   |-- _stats.py           # Shared statistics (overlap, KL, normal overlap)
|   |-- _edit.py            # Shared sequence editing (Levenshtein, melody extract)
|   |-- single.py           # single_file() + single_file_structural()
|   |-- pair.py             # pair_eval() + pair_eval_structural()
|   |-- muspy_ext.py        # 13 MusPy metrics
|   |-- note_f1.py          # 5 note-level pairwise metrics
|   |-- similarity.py       # 2 bar-level similarity metrics
|   |-- chord_accuracy.py   # Chord Accuracy (Viterbi HMM)
|   |-- distribution.py     # 6 distribution-level metrics
|   |-- advanced.py         # 14 advanced metrics
|   |-- structural.py       # 4 structural metrics
|   +-- cli.py              # CLI entry point
```

## 6. Testing

```bash
# Test all MIDI files in data/ directory
python test.py

# Test specific files
python test.py a.mid b.mid c.mid

# Quick single-file test
python test.py --single-only file.mid

# Quick pairwise test
python test.py --pair-only pred.mid ref.mid
```

`test.py` validates:
1. Single-file quality (13 metrics x N files)
2. Single-file structural (2 metrics x N files)
3. Pairwise note/structural/distribution/advanced (30 metrics x N pairs)
4. Self-consistency (same file -> perfect scores)


## 7. Citation

If you use this toolkit, please cite the relevant papers:

```bibtex
@article{dong2020muspy,
  title   = {MusPy: A Toolkit for Symbolic Music Generation},
  author  = {Dong, Hao et al.},
  journal = {Proc. ISMIR},
  year    = {2020},
  url     = {https://arxiv.org/abs/2008.01951}
}

@article{ou2025arrangement,
  title   = {Unifying Symbolic Music Arrangement with Track-aware Segments},
  author  = {Ou, Longshen and Zhao, Jingwei and Wang, Ziyu and Xia, Gus},
  journal = {Proc. NeurIPS},
  year    = {2025},
  url     = {https://arxiv.org/abs/2408.15176}
}

@article{lv2023getmusic,
  title   = {GETMusic: Generating Any Music Tracks with a Unified Model},
  author  = {Lv, Huan et al.},
  journal = {Proc. IJCAI},
  year    = {2023},
  url     = {https://arxiv.org/abs/2305.10841}
}

@article{wu2023morphose,
  title   = {MuseMorphose: Full-Song and Fine-Grained Piano Music Style Transfer},
  author  = {Wu, Shangda and Yang, Yuxuan},
  journal = {IEEE/ACM Trans. ASLP},
  year    = {2023},
  url     = {https://arxiv.org/abs/2105.04090}
}

@inproceedings{ren2020popmag,
  title     = {PopMAG: Pop Music Accompaniment Generation},
  author    = {Ren, Yi et al.},
  booktitle = {Proc. ACM Multimedia},
  year      = {2020},
  url       = {https://arxiv.org/abs/2008.07703}
}

@article{zhu2025fgg,
  title   = {Efficient Fine-Grained Guidance for Diffusion Model Based Symbolic Music Generation},
  author  = {Zhu, Tingyu and Liu, Haoyu and Wang, Ziyu and Jiang, Zhimin and Zheng, Zeyu},
  journal = {Proc. ICML},
  year    = {2025},
  url     = {https://arxiv.org/abs/2410.08435}
}

@inproceedings{hu2024ruleguided,
  title     = {Controllable Music Generation via Non-autoregressive Transformer and Randomized Guided Diffusion},
  author    = {Hu, Yifan et al.},
  booktitle = {Proc. ICML},
  year      = {2024},
  url       = {https://arxiv.org/abs/2402.14285}
}

@article{yadav2025text2midi,
  title   = {Text2midi: Generating Symbolic Music from Captions},
  author  = {Yadav, Abhinaba et al.},
  journal = {Proc. AAAI},
  year    = {2025},
  url     = {https://arxiv.org/abs/2412.16526}
}

@article{zeng2026musetok,
  title   = {MuseTok: Musical Discrete Tokenization},
  author  = {Zeng, Yun et al.},
  journal = {Proc. ICASSP},
  year    = {2026},
  url     = {https://arxiv.org/abs/2510.16273}
}

@inproceedings{papadopoulos2012chord,
  title     = {Large-scale Study of Chord Estimation Algorithms Based on Chroma},
  author    = {Papadopoulos, Helene and Peeters, Geoffroy},
  booktitle = {Proc. ISMIR},
  year      = {2012}
}

@article{yang2018evaluation,
  title   = {On the Evaluation of Generative Models in Music},
  author  = {Yang, Li-Chia and Lerch, Alexander},
  journal = {Neural Computing and Applications},
  year    = {2018},
  url     = {https://link.springer.com/article/10.1007/s00521-018-3759-5}
}

@article{mongeau1990comparison,
  title   = {Comparison of Musical Sequences},
  author  = {Mongeau, Marcel and Sankoff, David},
  journal = {Computers and the Humanities},
  year    = {1990}
}

@inproceedings{harte2006detecting,
  title     = {Detecting Harmonic Change in Musical Audio},
  author    = {Harte, Christopher and Sandler, Mark and Gasser, Martin},
  booktitle = {Proc. ACM MM Workshop},
  year      = {2006}
}
```


## License

MIT
