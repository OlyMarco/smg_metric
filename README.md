# smg-metrics

> **S**ymbolic **M**usic **G**eneration **Metrics** — 52 objective evaluation metrics, zero config.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENCE)
[![PyPI version](https://img.shields.io/pypi/v/smg-metrics.svg)](https://pypi.org/project/smg-metrics/)

**8 categories, 52 metrics, 21 papers/projects (1990–2026), fully typed & tested.**

| Category | Count | Latest source | Year |
|----------|-------|---------------|------|
| A. Single-file Quality | 13 | [FGG](https://arxiv.org/abs/2410.08435) / [MusPy](https://arxiv.org/abs/2008.01951) / [XMusic](https://arxiv.org/abs/2501.08809) | 2025 |
| B. Note-level Pairwise | 5 | [Ou et al.](https://arxiv.org/abs/2408.15176) | 2025 |
| C. Bar-level Pairwise | 2 | [MuseMorphose](https://arxiv.org/abs/2105.04090) | 2023 |
| D. Chord-level Pairwise | 2 | [FGG](https://arxiv.org/abs/2410.08435) / [Wang et al. ISMIR](https://arxiv.org/abs/2008.07122) | 2025/2020 |
| E. Distribution-level | 5 | [SongMASS](https://arxiv.org/abs/2012.05168) | 2020 |
| F. Advanced | 14 | [Text2midi](https://arxiv.org/abs/2412.16526) | 2025 |
| G. Structural | 4 | [MuseTok](https://arxiv.org/abs/2510.16273) | 2026 |
| H. Rhythmic/Temporal | 7 | Standard MIR Features / [D3PIA](https://github.com/jech2/D3PIA) | Various |

## Quick Start

```bash
pip install smg-metrics
```

```python
from smg_metrics import single_file, single_file_rhythmic, pair_eval, compute_ook

# Single-file quality (12 MusPy metrics)
quality = single_file("generated.mid")
print(quality.pce, quality.ebr, quality.sc)

# Out-of-Key fraction (FGG 2025)
ook = compute_ook("generated.mid")
print(f"OOK: {ook:.4f}")

# Rhythmic metrics (4 D3PIA-style)
rhythm = single_file_rhythmic("generated.mid")
print(rhythm.mean_ioi, rhythm.rhythmic_density)

# Pairwise comparison (11 metrics including deep chord similarity)
pair = pair_eval("generated.mid", "reference.mid")
print(pair.note_f1, pair.sim_chr, pair.ca, pair.cs)
```

```bash
# CLI
smg-eval -m generated.mid
smg-eval -p gen.mid -r ref.mid
smg-eval -m gen.mid -p gen.mid -r ref.mid -d -a -S -R
smg-eval -m gen.mid --only pce ebr sc --json
```

## Installation

```bash
pip install smg-metrics

# Optional: Install torch for deep chord similarity (CS metric)
pip install smg-metrics[torch]
# Or: pip install torch>=2.0.0

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
| [`torch`](https://pytorch.org/) | >= 2.0.0 | **Optional**: Deep chord similarity (CS metric) |
| `numpy` | >= 1.24 | Numerical computation |
| `scipy` | >= 1.10 | Scientific computing |

## Python API

```python
from smg_metrics import (
    single_file,                # 13 MusPy quality metrics
    single_file_structural,     # 2 structural single-file metrics
    single_file_rhythmic,       # 5 rhythmic metrics (4 D3PIA + GS)
    pair_eval,                  # 11 core pairwise metrics (incl. CS)
    pair_eval_structural,       # 2 structural pairwise metrics
    distribution_eval,          # 5 distribution-level metrics
    advanced_eval,              # 14 advanced metrics
    compute_ook,                # Out-of-Key fraction (FGG 2025)
    compute_cs,                 # Chord Similarity (Wang et al. 2020)
)
```

| Container | Fields | Count |
|-----------|--------|-------|
| `SingleFileResult` | pce, ebr, sc, pisr, polyphony, polyphony_rate, pitch_range, n_pitches_used, n_pitch_classes_used, emr, pe, dpc, ook | 13 |
| `StructuralSingleResult` | che, ngram_div | 2 |
| `RhythmicResult` | mean_ioi, rhythmic_intensity, rhythmic_density, voice_number, gs | 5 |
| `PairResult` | note_f1, notei_f1, mel_f1, i_iou, ver, sim_chr, sim_grv, ca, cs, onset_xor, note_overlap | 11 |
| `StructuralPairResult` | melody_match, tonal_dist | 2 |
| `DistributionResult` | pd, dd, sc_sim, pce_sim, gsc | 5 |
| `AdvancedResult` | kl_duration, kl_ioi, kl_pitch, oa_duration, oa_ioi, oa_pitch_range, oa_density, ci_precision, ci_recall, ci_f1, cts, cr_pred, cr_ref, recon_acc | 14 |

Every result container is a frozen dataclass with `.to_dict()`.

### Chord Recognition

```python
from smg_metrics import recognize_chords, compute_ca, compute_cs

# Advanced DP-based chord recognition (17 qualities + inversions)
chords = recognize_chords("music.mid")
for interval in chords:
    print(f"{interval.start:.2f}s - {interval.end:.2f}s: {interval.label}")
# Output: 0.00s - 2.50s: C:maj
#         2.50s - 5.00s: G:7/5  (second inversion)

# Chord Accuracy (rule-based DP method, FGG 2025)
ca = compute_ca("generated.mid", "reference.mid")
print(f"Chord Accuracy: {ca:.2%}")

# Chord Similarity (deep embedding, Wang et al. 2020)
cs = compute_cs("generated.mid", "reference.mid")
print(f"Chord Similarity: {cs:.4f}")
```

**Note**: CS metric requires downloading model weights (29 MB). See [Model Weights](#model-weights) section below.

### Out-of-Key Notes

```python
from smg_metrics import compute_ook

# Compute percentage of 16th-note steps with out-of-key notes
ook = compute_ook("generated.mid")
print(f"Out-of-Key: {ook:.4f}")

# Get detailed breakdown
ook, details = compute_ook("generated.mid", return_details=True)
print(f"Key: {details['key']}")
print(f"OOK steps: {details['ook_steps']}/{details['total_steps']}")
print(f"OOK notes: {details['ook_notes']}")
```

**Reference**: FGG (Zhu et al., ICML 2025) uses OOK to measure dissonance. Well-controlled generation should have OOK ≈ 0–0.02.

## Model Weights

The **Chord Similarity (CS)** metric requires pretrained model weights:

### Quick Download

```bash
# Download lightweight model (29 MB, recommended)
cd smg_metrics/model_weights
https://github.com/OlyMarco/smg_metric/blob/main/smg_metrics/model_weights/polydis-v1-chd_encoder_only.pt
```

### Model Details

- **Architecture**: Bidirectional GRU chord encoder (36 → 1024 → 256)
- **Training**: EC2-VAE (Wang et al., ISMIR 2020)
- **Size**: 29 MB (pruned from 104 MB full model, 72.3% reduction)
- **License**: Inherits from original PolyDisVAE

**Citation**:
```bibtex
@inproceedings{wang2020learning,
  title={Learning interpretable representation for controllable polyphonic music generation},
  author={Wang, Ziyu and Wang, Dingsu and Zhang, Yixiao and Xia, Gus},
  booktitle={Proceedings of the 21st International Society for Music Information Retrieval Conference},
  year={2020}
}
```

See `smg_metrics/model_weights/README.md` for more details.

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

## Test Suite

```bash
# Quick single-file test
python test.py --single-only data/gt/seg_40_48.mid

# Full test on directories (auto multi-core + progress bar when >= 2 files)
python test.py data/gen/ data/gt/

# Pairwise only
python test.py --pair-only pred.mid ref.mid

# Select specific metrics
python test.py --only pce ebr note_f1 ca sim_chr kl_pitch pred.mid ref.mid

# Save results to JSON
python test.py data/gen/ data/gt/ --json
```

| Flag | Description |
|------|-------------|
| `--single-only` | Run single-file metrics only |
| `--pair-only` | Run pairwise metrics only |
| `--only METRIC ...` | Run only selected metrics |
| `--json` | Save results to `test_results.json` |

Notes:
- When evaluating 2 or more files, test.py uses multi-core evaluation with a tqdm progress bar.
- Output file: `test_results.json` in the project root.

## CLI Usage

```bash
# Single-file quality (14 metrics: 13 MusPy + OOK)
smg-eval -m generated.mid

# Single-file + structural + rhythmic (20 metrics)
smg-eval -m generated.mid -S -R

# Pairwise core (11 metrics: includes CS with deep embedding)
smg-eval -p gen.mid -r ref.mid

# Full 52-metric run
smg-eval -m gen.mid -p gen.mid -r ref.mid -d -a -S -R

# Select specific metrics
smg-eval -m gen.mid --only pce ebr sc ook
smg-eval -p gen.mid -r ref.mid --only ca cs note_f1

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

Sources: [MusPy](https://github.com/salu133445/muspy) / ISMIR 2020, [XMusic](https://arxiv.org/abs/2501.08809) / IEEE 2025, [FGG](https://arxiv.org/abs/2410.08435) ICML 2025.

| Metric | Symbol | Range | Reference |
|--------|--------|-------|-----------|
| Pitch Class Entropy | PCE | [0, log₂12] | [Wu & Yang, ISMIR 2020](https://archives.ismir.net/ismir2020/paper/000339.pdf); XMusic 2025 |
| Empty Beat Rate | EBR | [0, 1] | Dong et al., ISMIR 2018; XMusic 2025 |
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
| Out-of-Key Fraction | OOK | [0, 1] | FGG 2025, Krumhansl-Kessler key detection |

### B. Note-level Pairwise (5)

Source: [Ou et al.](https://arxiv.org/abs/2408.15176), NeurIPS 2025.

| Metric | Symbol | Range |
|--------|--------|-------|
| Note F1 | F1 | [0, 1] |
| Notei F1 | F1i | [0, 1] |
| Melody F1 | F1mel | [0, 1] |
| Instrument IoU | I-IoU | [0, 1] |
| Voice Error Rate | VER | [0, ∞) |

### B2. Pairwise Rhythmic (2)

Sources: Standard MIR rhythmic comparison metrics. XOR implementation from [D3PIA](https://github.com/jech2/D3PIA) ICASSP 2026, NOvlp from [mir_eval](https://github.com/craffel/mir_eval) ISMIR 2014.

| Metric | Symbol | Range |
|--------|--------|-------|
| Onset XOR Distance | XOR | [0, 1] |
| Note Overlap | NOvlp | [0, 1] |

### C. Bar-level Pairwise (2)

Source: [MuseMorphose](https://arxiv.org/abs/2105.04090), IEEE/ACM TASLP 2023.

| Metric | Symbol | Range |
|--------|--------|-------|
| Chroma Similarity | simChr | [0, 1] |
| Groove Similarity | simGrv | [0, 1] |

### D. Chord-level Pairwise (2)

Sources: [FGG](https://arxiv.org/abs/2410.08435) ICML 2025, [Wang et al. ISMIR](https://arxiv.org/abs/2008.07122) 2020, [music-x-lab/midi-chord-recognition](https://github.com/music-x-lab/midi-chord-recognition).

| Metric | Symbol | Range | Description |
|--------|--------|-------|-------------|
| Chord Accuracy | CA | [0, 1] | Beat-level DP chord recognition + exact match |
| Chord Similarity | CS | [0, 1] | Deep chord embedding similarity (requires PyTorch) |

**Chord Recognition Pipeline** (adapted from music-x-lab):
1. Extract beat/downbeat positions from MIDI tempo map
2. Quantise notes to beat grid → per-beat 12-dim treble chroma + bass chroma
3. Channel-weighted aggregation (thickness + bass reweighting)
4. Score each chord template per beat (with bass bonus)
5. Dynamic-programming decode with span-length reward and transition penalty
6. Output interval-level chord labels

Two methods available: `'dp'` (default, beat-level) and `'viterbi'` (bar-level HMM).

### E. Distribution-level (5)

Sources: [SongMASS](https://arxiv.org/abs/2012.05168) ACM-MM 2020, [MusPy](https://github.com/salu133445/muspy) ISMIR 2020, [Wu & Yang](https://archives.ismir.net/ismir2020/paper/000339.pdf) ISMIR 2020.

| Metric | Symbol | Range |
|--------|--------|-------|
| Pitch Distribution | PD | [0, 1] |
| Duration Distribution | DD | [0, 1] |
| Scale Consistency Sim | SC_sim | [0, 1] |
| Pitch Class Entropy Sim | PCE_sim | [0, 1] |
| Groove Pattern Similarity Consistency | GSC | [0, 1] |

### F. Advanced (14)

Sources: [GETMusic](https://arxiv.org/abs/2305.10841) IJCAI 2025, [Text2midi](https://arxiv.org/abs/2412.16526) AAAI 2025, [MuseTok](https://arxiv.org/abs/2510.16273) ICASSP 2026.

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

### H. Rhythmic/Temporal Single-file (5)

Sources: Standard MIR rhythmic features. Implementation conventions from [D3PIA](https://github.com/jech2/D3PIA)/MIDISym (ICASSP 2026), [Wu & Yang](https://archives.ismir.net/ismir2020/paper/000339.pdf) ISMIR 2020.

| Metric | Symbol | Range |
|--------|--------|-------|
| Mean IOI | IOI | [0, ∞) |
| Rhythmic Intensity | RI | [0, ∞) |
| Rhythmic Density | RD | [0, 1] |
| Voice Number | VN | [0, ∞) |
| Grooving Pattern Similarity | GS | [0, 1] |

## v5.3 Changelog

### Major Refactoring
- **GS Metric Correction**: Grooving Pattern Similarity (GS) reimplemented following original paper definition
  - Now uses 64-dimensional binary onset vectors per bar (as per Wu & Yang ISMIR 2020)
  - Computes normalized Hamming similarity between all bar pairs: GS = 1 - (1/64) · Σ XOR
  - Removed dependency on `muspy.groove_consistency()` (incorrect implementation)
  - Range: [0, 1] — measures rhythmic pattern consistency within a piece
  - `RhythmicResult` now contains 5 metrics: IOI, RI, RD, VN, GS

- **GSC Update**: Distribution-level metric now uses corrected GS implementation
  - Updated `_gsc()` in `distribution.py` to use new `grooving_pattern_similarity()`
  - Definition unchanged: GSC = 1 - |GS_pred - GS_ref|
  - Clearer distinction from single-file GS metric

### Performance Optimization
- **CLI Startup Speed**: Implemented lazy imports via `__getattr__` in `__init__.py`
  - Startup time reduced from ~6.3s to ~0.14s (~45× faster)
  - `--help` now responds instantly
  - API remains fully compatible: `from smg_metrics import single_file` still works

### Code Changes
- Reimplemented `grooving_pattern_similarity()` in `rhythmic.py` with paper-accurate algorithm
- Updated `_gsc()` in `distribution.py` to use corrected GS implementation
- Removed `muspy` dependency from GS calculation
- Added comprehensive docstrings with paper references and formulas

### Documentation Updates
- Updated metric counts: Single-file (14→13), Rhythmic single (4→5), Rhythmic pair (3→2)
- Corrected Wu & Yang ISMIR 2020 paper citations and links
- Added comprehensive source references for rhythmic metrics
- Clarified metric categories, ranges, and purposes

### API Changes
- **Modified**: `grooving_pattern_similarity(midi_path)` — now uses 64-dim vectors, normalized Hamming similarity
- **Unchanged**: `gsc` in `DistributionResult` (name unchanged from v5.2)
- **Removed**: `gs` field from `SingleFileResult`
- **Added**: `gs` field to `RhythmicResult`

### Changed
- **Version**: 5.2.0 → 5.3.0
- **Total metrics**: 52 (reorganized for clarity and consistency)

## v5.2 Changelog

### Optimizations
- **CS Model Caching**: Chord Similarity model now cached for batch evaluation
  - Model loaded once and reused across multiple `compute_cs()` calls
  - ~1.6× faster per call after initial load, ~39% time savings on large batches
  - Example: 153 file pairs reduced from 34.6s → 21.2s
  - Thread-safe caching with automatic device management
  - New API: `clear_cs_model_cache()` to manually free GPU/CPU memory after batch processing
- **Memory Management**: Users can explicitly release CS model memory when needed

### API Changes
- **New function**: `clear_cs_model_cache()` — Clear cached CS models to free memory
- **Improved**: `compute_cs()` now automatically caches model for subsequent calls

### Changed
- **Version**: 5.1.0 → 5.2.0
- **Performance**: Batch CS evaluation significantly faster (model loaded once vs. per-call)

### Example
```python
from smg_metrics import compute_cs, clear_cs_model_cache

# Batch evaluation - model loaded once, reused for all pairs
for pred, ref in file_pairs:
    cs = compute_cs(pred, ref)  # Fast after first call
    
# Free memory after batch
clear_cs_model_cache()  # Returns: 1 (number of models cleared)
```

## v5.1 Changelog

### New features
- **Chord Similarity (CS)**: Deep chord embedding metric using pruned PolyDisVAE encoder ([Wang et al. ISMIR 2020](https://arxiv.org/abs/2008.07122))
  - Optional dependency: requires `torch>=2.0.0` (install with `pip install smg-metrics[torch]`)
  - Lightweight model (29 MB): `polydis-v1-chd_encoder_only.pt`
  - Supports 17 chord qualities + inversions via dynamic programming recognition
- **Out-of-Key (OOK)**: Percentage of notes outside detected key using Krumhansl-Kessler algorithm
  - Standalone single-file metric, no external annotations needed
  - Integrated into CLI with `--only ook` support

### Changed
- **PyTorch**: Moved to optional dependencies (`torch` extra)
- **Metric count**: 51 → 53 (added CS + OOK)
- **Version**: 5.0.0 → 5.1.0

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
