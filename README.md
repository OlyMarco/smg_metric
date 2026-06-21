# smg-metrics

> **S**ymbolic **M**usic **G**eneration **Metrics** — 51 objective evaluation metrics, zero config.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENCE)
[![PyPI version](https://img.shields.io/pypi/v/smg-metrics.svg)](https://pypi.org/project/smg-metrics/)

**8 categories, 51 metrics, 20 papers/projects (1990–2026), fully typed & tested.**

| Category | Count | Latest source | Year |
|----------|-------|---------------|------|
| A. Single-file Quality | 13 | [MusPy](https://arxiv.org/abs/2008.01951) / [XMusic](https://arxiv.org/abs/2501.08809) | 2025 |
| B. Note-level Pairwise | 5 | [Ou et al.](https://arxiv.org/abs/2408.15176) | 2025 |
| C. Bar-level Pairwise | 2 | [MuseMorphose](https://arxiv.org/abs/2105.04090) | 2023 |
| D. Chord-level Pairwise | 1 | [FGG](https://arxiv.org/abs/2410.08435) / [music-x-lab](https://github.com/music-x-lab/midi-chord-recognition) | 2025 |
| E. Distribution-level | 5 | [SongMASS](https://arxiv.org/abs/2010.02305) | 2020 |
| F. Advanced | 14 | [Text2midi](https://arxiv.org/abs/2412.16526) | 2025 |
| G. Structural | 4 | [MuseTok](https://arxiv.org/abs/2510.16273) | 2026 |
| H. Rhythmic/Temporal | 7 | [D3PIA](https://github.com/jech2/D3PIA) | 2026 |

## Quick Start

```bash
pip install smg-metrics
```

```python
from smg_metrics import single_file, single_file_rhythmic, pair_eval

# Single-file quality (13 MusPy metrics)
quality = single_file("generated.mid")
print(quality.pce, quality.ebr, quality.gs)

# Rhythmic metrics (4 D3PIA-style)
rhythm = single_file_rhythmic("generated.mid")
print(rhythm.mean_ioi, rhythm.rhythmic_density)

# Pairwise comparison (10 metrics)
pair = pair_eval("generated.mid", "reference.mid")
print(pair.note_f1, pair.sim_chr, pair.ca)
```

```bash
# CLI
smg-eval -m generated.mid
smg-eval -p gen.mid -r ref.mid
smg-eval -m gen.mid -p gen.mid -r ref.mid -d -a -S -R
smg-eval -m gen.mid --only pce ebr gs --json
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
| [`pretty-midi`](https://github.com/craffel/pretty-midi) | >= 0.2.10 | Beat tracking & bar-level parsing |
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
    distribution_eval,          # 5 distribution-level metrics
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
| `DistributionResult` | pd, dd, sc_sim, pce_sim, gs_sim | 5 |
| `AdvancedResult` | kl_duration, kl_ioi, kl_pitch, oa_duration, oa_ioi, oa_pitch_range, oa_density, ci_precision, ci_recall, ci_f1, cts, cr_pred, cr_ref, recon_acc | 14 |

Every result container is a frozen dataclass with `.to_dict()`.

### Chord Recognition

```python
from smg_metrics import recognize_chords, compute_ca

# Beat-level DP chord recognition (music-x-lab algorithm)
chords = recognize_chords("song.mid")
for iv in chords:
    print(f"{iv.start:.2f}-{iv.end:.2f}: {iv.label}")

# Chord Accuracy with DP method (default)
ca = compute_ca("pred.mid", "ref.mid", method="dp")

# Or use Viterbi method (GETMusic)
ca = compute_ca("pred.mid", "ref.mid", method="viterbi")
```

### Individual metrics

```python
from smg_metrics import (
    chord_histogram_entropy, ngram_diversity,
    melody_matchness, tonal_distance,
    compute_ca, midi_to_chords, midi_to_chords_dp,
    mean_ioi, rhythmic_intensity, rhythmic_density,
    voice_number, onset_xor_distance, note_overlap,
    grooving_pattern_similarity,
)

che = chord_histogram_entropy("file.mid")
ca = compute_ca("pred.mid", "ref.mid")
gs = grooving_pattern_similarity("pred.mid", "ref.mid")
```

## CLI Usage

```bash
# Single-file quality (13 metrics)
smg-eval -m generated.mid

# Single-file + structural + rhythmic (19 metrics)
smg-eval -m generated.mid -S -R

# Pairwise core (10 metrics)
smg-eval -p gen.mid -r ref.mid

# Full 51-metric run
smg-eval -m gen.mid -p gen.mid -r ref.mid -d -a -S -R

# Select specific metrics
smg-eval -m gen.mid --only pce ebr gs
smg-eval -p gen.mid -r ref.mid --only ca note_f1 grooving_pattern_similarity

# List all available metrics
smg-eval --list-metrics

# JSON output
smg-eval -m gen.mid --json

# Batch directory
smg-eval --pred_dir ./pred/ --ref_dir ./ref/

# Timing
smg-eval -m gen.mid --time
```

| Flag | Description | Default |
|------|-------------|---------|
| `-m, --music PATH` | Single-file mode | -- |
| `-p, --pred PATH` | Predicted MIDI for pair mode | -- |
| `-r, --ref PATH` | Reference MIDI for pair mode | -- |
| `--pred_dir DIR` | Batch predicted directory | -- |
| `--ref_dir DIR` | Batch reference directory | -- |
| `--root INT` | Root pitch for PISR | `0` |
| `--mode {major,minor}` | Scale mode for PISR | `major` |
| `-d, --dist` | Distribution-level metrics | `false` |
| `-a, --advanced` | Advanced metrics | `false` |
| `-S, --structural` | Structural metrics | `false` |
| `-R, --rhythmic` | Rhythmic metrics | `false` |
| `--only METRIC ...` | Select specific metrics | -- |
| `--list-metrics` | List all metric names | -- |
| `--json` | JSON output | `false` |
| `--time` | Print elapsed time | `false` |

## Metrics Reference

### A. Single-file Quality (13)

Sources: [MusPy](https://github.com/salu133445/muspy) / ISMIR 2020, [XMusic](https://arxiv.org/abs/2501.08809) / IEEE 2025.

| Metric | Symbol | Range | Reference |
|--------|--------|-------|-----------|
| Pitch Class Entropy | PCE | [0, log₂12] | Wu & Yang, ISMIR 2020; XMusic 2025 |
| Empty Beat Rate | EBR | [0, 1] | Dong et al., ISMIR 2018; XMusic 2025 |
| Groove Consistency | GS | [0, 1] | Wu & Yang, ISMIR 2020; XMusic 2025 |
| Scale Consistency | SC | [0, 1] | Mogren, NeurIPS-W 2016 |
| Pitch-in-Scale Rate | PISR | [0, 1] | Dong et al., AAAI 2018 |
| Polyphony | Poly | [1, ∞) | Dong et al., AAAI 2018 |
| Polyphony Rate | PR | [0, 1] | Dong et al., AAAI 2018 |
| Pitch Range | Range | [0, 127] | MusPy 2020 |
| Unique Pitches | N_p | [0, 128] | MusPy 2020 |
| Unique Pitch Classes | N_pc | [0, 12] | MusPy 2020 |
| Empty Measure Rate | EMR | [0, 1] | Dong et al., AAAI 2018 |
| Pitch Entropy | PE | [0, 7] | MusPy 2020 |
| Drum Pattern Consistency | DPC | [0, 1] | Dong et al., AAAI 2018 |

### B. Note-level Pairwise (5)

Source: [Ou et al.](https://arxiv.org/abs/2408.15176), NeurIPS 2025.

| Metric | Symbol | Range |
|--------|--------|-------|
| Note F1 | F1 | [0, 1] |
| Notei F1 | F1i | [0, 1] |
| Melody F1 | F1mel | [0, 1] |
| Instrument IoU | I-IoU | [0, 1] |
| Voice Error Rate | VER | [0, ∞) |

### B2. Pairwise Rhythmic (3)

Sources: [D3PIA](https://github.com/jech2/D3PIA) ICASSP 2026, [mir_eval](https://github.com/craffel/mir_eval) ISMIR 2014, [Wu & Yang](https://arxiv.org/abs/2008.01951) ISMIR 2020.

| Metric | Symbol | Range |
|--------|--------|-------|
| Onset XOR Distance | XOR | [0, 1] |
| Note Overlap | NOvlp | [0, 1] |
| Grooving Pattern Similarity | GS_d3pia | [0, ∞) |

### C. Bar-level Pairwise (2)

Source: [MuseMorphose](https://arxiv.org/abs/2105.04090), IEEE/ACM TASLP 2023.

| Metric | Symbol | Range |
|--------|--------|-------|
| Chroma Similarity | simChr | [0, 1] |
| Groove Similarity | simGrv | [0, 1] |

### D. Chord-level Pairwise (1)

Source: [FGG](https://arxiv.org/abs/2410.08435) ICML 2025, [music-x-lab/midi-chord-recognition](https://github.com/music-x-lab/midi-chord-recognition).

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Chord Accuracy | CA | [0, 1] | Beat-level DP chord recognition + exact match |

**Chord Recognition Pipeline** (adapted from music-x-lab):
1. Extract beat/downbeat positions from MIDI tempo map
2. Quantise notes to beat grid → per-beat 12-dim treble chroma + bass chroma
3. Channel-weighted aggregation (thickness + bass reweighting)
4. Score each chord template per beat (with bass bonus)
5. Dynamic-programming decode with span-length reward and transition penalty
6. Output interval-level chord labels

Two methods available: `'dp'` (default, beat-level) and `'viterbi'` (bar-level HMM).

### E. Distribution-level (5)

Sources: [SongMASS](https://arxiv.org/abs/2010.02305) ACM-MM 2020, [MusPy](https://github.com/salu133445/muspy) ISMIR 2020.

| Metric | Symbol | Range |
|--------|--------|-------|
| Pitch Distribution | PD | [0, 1] |
| Duration Distribution | DD | [0, 1] |
| Scale Consistency Sim | SC_sim | [0, 1] |
| Pitch Class Entropy Sim | PCE_sim | [0, 1] |
| Groove Consistency Sim | GS_sim | [0, 1] |

### F. Advanced (14)

Sources: [GETMusic](https://arxiv.org/abs/2305.10841) IJCAI 2025, [Rule Guided](https://arxiv.org/abs/2410.08435) ICML 2024, [Text2midi](https://arxiv.org/abs/2412.16526) AAAI 2025, [MuseTok](https://arxiv.org/abs/2510.16273) ICASSP 2026.

| Metric | Symbol | Range |
|--------|--------|-------|
| KL Divergence (Duration) | KL_dur | [0, ∞) |
| KL Divergence (IOI) | KL_ioi | [0, ∞) |
| KL Divergence (Pitch) | KL_pitch | [0, ∞) |
| Overlapping Area ×4 | OA | [0, 1] |
| Instrument Coverage ×3 | CI | [0, 1] |
| Correct Time Signature | CTS | {0, 1} |
| Compression Ratio ×2 | CR | [0, ∞) |
| Reconstruction Accuracy | ReconAcc | [0, 1] |

### G. Structural (4)

Sources: [Papadopoulos & Peeters](https://hal.science/hal-00726774) ISMIR 2012, [Yang & Lerch](https://link.springer.com/article/10.1007/s00521-018-3548-1) NCA 2018, [Mongeau & Sankoff](https://link.springer.com/article/10.1007/BF00788892) CH 1990, [Harte et al.](https://dl.acm.org/doi/10.1145/1180639.1180720) ACM MM 2006.

| Metric | Symbol | Type | Range |
|--------|--------|------|-------|
| Chord Histogram Entropy | CHE | single | [0, log₂C] |
| N-gram Diversity | Ngram | single | [0, 1] |
| Melody Matchness | MM | pair | [0, 1] |
| Tonal Distance | TD | pair | [0, ∞) |

### H. Rhythmic/Temporal Single-file (4)

Source: [D3PIA](https://github.com/jech2/D3PIA) ICASSP 2026, MIDISym feature extraction.

| Metric | Symbol | Range |
|--------|--------|-------|
| Mean IOI | IOI | [0, ∞) |
| Rhythmic Intensity | RI | [0, ∞) |
| Rhythmic Density | RD | [0, 1] |
| Voice Number | VN | [0, ∞) |

## v5.0 Changelog

### New features
- **Beat-level DP chord recognition** (music-x-lab algorithm): replaces bar-level Viterbi as default CA method
- **D3PIA Grooving Pattern Similarity**: pairwise within-file XOR similarity metric
- **`--only` flag**: select specific metrics for faster evaluation
- **`--list-metrics`**: display all available metric names
- **Short flags**: `-m`, `-p`, `-r`, `-d`, `-a`, `-S`, `-R` for faster CLI usage
- **Lazy imports**: faster CLI startup time

### Removed
- **OOK (Out-of-Key Rate)**: requires external key annotations, limited standalone utility
- **Chord Similarity (CS)**: requires pretrained chord encoder model

### Changed
- **CA default method**: `'dp'` (beat-level) instead of `'viterbi'` (bar-level)
- **Distribution metrics**: removed OOK (PD, DD, SC_sim, PCE_sim, GS_sim remain)
- **Numpy**: removed `<2.0` upper bound
- **Version**: 0.4.0 → 5.0.0

## License

MIT — see [LICENCE](LICENCE).

## Citation

If you use smg-metrics in your research, please cite:

```bibtex
@software{smg_metrics,
  title  = {smg-metrics: Objective Evaluation Metrics for Symbolic Music Generation},
  author = {Temmie Pratt},
  year   = {2026},
  url    = {https://github.com/OlyMarco/smg_metric},
}
```
