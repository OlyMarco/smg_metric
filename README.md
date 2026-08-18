# smg-metrics

> **S**ymbolic **M**usic **G**eneration **Metrics** — a toolkit of 25 objective evaluation metrics for Symbolic Music Generation, spanning harmony, rhythmic complexity, polyphony, distribution, and structural coherence — zero‑config, fully typed.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENCE)
[![PyPI version](https://img.shields.io/pypi/v/smg-metrics.svg)](https://pypi.org/project/smg-metrics/)

---

## Overview

`smg-metrics` provides 25 objective evaluation metrics for symbolic music generation, organized into 5 categories. Each metric traces back to a specific paper or project (2012–2026), with formulas verified against original source code and literature descriptions.

| Category | Single-file | Pairwise | Total | Key sources |
|----------|-------------|----------|-------|-------------|
| [A. Harmony & Tonality](#a-harmony--tonality-7) | 5 | 2 | 7 | [Jazz Transformer](https://archives.ismir.net/ismir2020/paper/000339.pdf), [MuseGAN](https://arxiv.org/abs/1709.06298), [FGG](https://arxiv.org/abs/2410.08435) |
| [B. Rhythm & Temporal](#b-rhythm--temporal-6) | 4 | 2 | 6 | [D3PIA](https://github.com/jech2/D3PIA), [Jazz Transformer](https://archives.ismir.net/ismir2020/paper/000339.pdf) |
| [C. Polyphony & Quality](#c-polyphony--quality-6) | 6 | 0 | 6 | [MuseGAN](https://arxiv.org/abs/1709.06298), [MusPy](https://arxiv.org/abs/2008.01951) |
| [D. Note-level Pairwise](#d-note-level-pairwise-2) | 0 | 2 | 2 | [USMA](https://arxiv.org/abs/2408.15176) |
| [E. Bar-level Pairwise](#e-bar-level-pairwise-2) | 0 | 2 | 2 | [MuseMorphose](https://arxiv.org/abs/2105.04090) |
| [F. Distribution-level](#f-distribution-level-2) | 0 | 2 | 2 | [SongMASS](https://arxiv.org/abs/2012.05168) |
| **Total** | **15** | **10** | **25** | 18 papers/projects |

---

## Quick Start

```bash
pip install smg-metrics
```

```python
from smg_metrics import (
    single_file_harmony,    # 5 harmony metrics: PCE, SC, PISR, OOK, CHE
    single_file_rhythm,     # 4 rhythm metrics: IOI, GS, Ngram, EBR
    single_file_quality,    # 6 quality metrics: Poly, PR, PE, Range, Np, Npc
    pair_eval,              # 8 pairwise metrics: F1, F1i, simChr, simGrv, CA, CS, OXD, NOvlp
    distribution_eval,      # 2 distribution metrics: PD, DD
)

# Evaluate a single generated MIDI file (15 metrics)
harmony = single_file_harmony("generated.mid")  # PCE, SC, PISR, OOK, CHE
rhythm  = single_file_rhythm("generated.mid")   # IOI, GS, Ngram, EBR
quality = single_file_quality("generated.mid")  # Polyphony, PR, PE, Range, Np, Npc

# Compare generated vs. reference (10 metrics)
pair = pair_eval("generated.mid", "reference.mid")  # F1, F1i, simChr, simGrv, CA, CS, OXD, NOvlp
dist = distribution_eval("gen.mid", "ref.mid")      # PD, DD

print(f"PCE={harmony.pce:.3f}  SC={harmony.sc:.3f}  OOK={harmony.ook:.3f}")
print(f"Note F1={pair.note_f1:.3f}  CA={pair.ca:.3f}  CS={pair.cs:.3f}")
```

### Optional: Deep Chord Similarity (CS)

The [CS metric](#cs--chord-similarity-pair) uses a pretrained [EC2-VAE](https://arxiv.org/abs/2008.07122) chord encoder (29 MB). It requires [PyTorch](https://pytorch.org/):

```bash
pip install smg-metrics[torch]
```

If PyTorch or model weights are unavailable, CS is skipped with a warning and defaults to 0.0. All other 24 metrics work without PyTorch.

---

## Installation

```bash
# From PyPI (default: no PyTorch, 24/25 metrics work)
pip install smg-metrics

# With PyTorch for CS metric (25/25 metrics)
pip install smg-metrics[torch]

# From source
pip install -e .
pip install -e ".[torch]"
```

### Dependencies

| Package | Version | Required by | Notes |
|---------|---------|-------------|-------|
| [muspy](https://github.com/salu133445/muspy) | >= 0.5.0 | PCE, SC, PISR, Poly, PR, PE, Range, Np, Npc, EBR | MusPy wraps MuseGAN metrics with explicit citations |
| [miditoolkit](https://github.com/music-x-lab/midi-toolkit) | >= 1.0 | All MIDI loading | Fast MIDI parsing by music-x-lab |
| [pretty_midi](https://github.com/craffel/pretty-midi) | >= 0.2.10 | simChr, simGrv, CA (dp) | Beat tracking and bar-level segmentation |
| [mir-eval](https://github.com/mir-evaluation/mir_eval) | >= 0.7 | NOvlp | Standard MIR evaluation toolkit |
| [numpy](https://numpy.org/) | >= 1.24 | All metrics | Numerical computation |
| [scipy](https://scipy.org/) | >= 1.10 | (transitive) | Required by muspy/mir-eval |
| [torch](https://pytorch.org/) | >= 2.0.0 | CS only (optional) | Deep chord embedding via EC2-VAE encoder |

---

## CLI Usage

```bash
# All 15 single-file metrics on one MIDI file
smg-eval -m generated.mid --all-single

# All 15 single-file metrics on a directory (recursive: finds all .mid files)
smg-eval -m ./data/pred --all-single

# Only harmony metrics (PCE, SC, PISR, OOK, CHE)
smg-eval -m generated.mid --harmony

# Only rhythm metrics (IOI, GS, Ngram, EBR)
smg-eval -m generated.mid --rhythm

# Only quality metrics (Poly, PR, PE, Range, Np, Npc)
smg-eval -m generated.mid --quality

# All 10 pairwise metrics (8 pair + 2 distribution)
smg-eval -p gen.mid -r ref.mid -d

# Only pairwise core (8 metrics, no distribution)
smg-eval -p gen.mid -r ref.mid

# Select specific metrics by name (comma-separated)
smg-eval -m gen.mid --only pce,sc,gs,ebr
smg-eval -p gen.mid -r ref.mid --only note_f1,ca,cs

# Directory input with --only (recursive)
smg-eval -m ./data/pred --only pce,gs --json

# List all 25 available metric names
smg-eval --list-metrics

# Output as JSON (for scripting / pipeline integration)
smg-eval -m gen.mid --json

# Batch evaluation: compare every file in pred_dir against ref_dir
smg-eval --pred_dir ./predictions/ --ref_dir ./references/

# Print elapsed time
smg-eval -m gen.mid --time
```

### CLI Flags

| Flag | Description |
|------|-------------|
| `-m, --music PATH` | MIDI file **or directory** for single-file metrics (harmony, rhythm, quality). If a directory, recursively finds all .mid files |
| `-p, --pred PATH` | Predicted / generated MIDI file for pairwise metrics |
| `-r, --ref PATH` | Reference / ground-truth MIDI file for pairwise metrics |
| `--pred_dir DIR` | Directory of predicted MIDI files (batch mode, auto-pairs by sorted filename) |
| `--ref_dir DIR` | Directory of reference MIDI files (batch mode) |
| `--root INT` | Root pitch class for PISR (0=C, 1=C#, ..., 11=B; default 0) |
| `--mode {major,minor}` | Scale mode for PISR (default: major) |
| `--harmony` | Run 5 harmony metrics: PCE, SC, PISR, OOK, CHE |
| `--rhythm` | Run 4 rhythm metrics: IOI, GS, Ngram, EBR |
| `--quality` | Run 6 quality metrics: Poly, PR, PE, Range, Np, Npc |
| `--all-single` | Run all 15 single-file metrics (equivalent to `--harmony --rhythm --quality`) |
| `-d, --dist` | Run 2 distribution metrics: PD, DD (requires `-p` and `-r`) |
| `--only M1,M2,...` | Run only the specified metrics (comma-separated, see `--list-metrics` for valid names) |
| `--list-metrics` | Print all 25 metric names grouped by category, then exit |
| `--json` | Output results as JSON to stdout (NaN/inf converted to null) |
| `--time` | Print elapsed time in seconds to stderr |

---

## Python API

### Single-file Metrics

```python
from smg_metrics import single_file_harmony, single_file_rhythm, single_file_quality

# 5 harmony metrics (PCE, SC, PISR, OOK, CHE)
h = single_file_harmony("music.mid", root=0, mode="major")
# h.pce, h.sc, h.pisr, h.ook, h.che

# 4 rhythm metrics (IOI, GS, Ngram, EBR)
r = single_file_rhythm("music.mid")
# r.mean_ioi, r.gs, r.ngram_div, r.ebr

# 6 quality metrics (Polyphony, PR, PE, Range, Np, Npc)
q = single_file_quality("music.mid")
# q.polyphony, q.polyphony_rate, q.pitch_entropy, q.pitch_range,
# q.n_pitches_used, q.n_pitch_classes_used
```

### Pairwise Metrics

```python
from smg_metrics import pair_eval, distribution_eval

# 8 pairwise metrics (Note F1, Notei F1, simChr, simGrv, CA, CS, OXD, NOvlp)
pair = pair_eval("pred.mid", "ref.mid")
# pair.note_f1, pair.notei_f1, pair.sim_chr, pair.sim_grv,
# pair.ca, pair.cs, pair.onset_xor, pair.note_overlap

# 2 distribution metrics (PD, DD)
dist = distribution_eval("pred.mid", "ref.mid")
# dist.pd, dist.dd

# Disable CS (skip PyTorch dependency)
pair = pair_eval("pred.mid", "ref.mid", enable_cs=False)
```

### Individual Metric Functions

Each metric is also available as a standalone function:

```python
from smg_metrics import (
    pitch_class_entropy,       # PCE
    scale_consistency,         # SC
    pitch_in_scale_rate,       # PISR
    out_of_key_fraction,      # OOK
    chord_histogram_entropy,   # CHE
    mean_ioi,                  # IOI
    grooving_pattern_similarity,  # GS
    ngram_diversity,           # Ngram
    empty_beat_rate,           # EBR
    onset_xor_distance,        # OXD
    note_overlap,              # NOvlp
    polyphony,                 # Poly
    polyphony_rate,            # PR
    pitch_entropy,             # PE
    pitch_range,               # Range
    n_pitches_used,            # N_p
    n_pitch_classes_used,      # N_pc
    compute_ca,                # CA
    compute_cs,                # CS
)
```

### Result Containers

Every result is a frozen dataclass with `.to_dict()`:

| Container | Fields | Count |
|-----------|--------|-------|
| `HarmonySingleResult` | pce, sc, pisr, ook, che | 5 |
| `RhythmicResult` | mean_ioi, gs, ngram_div, ebr | 4 |
| `QualityResult` | polyphony, polyphony_rate, pitch_entropy, pitch_range, n_pitches_used, n_pitch_classes_used | 6 |
| `PairResult` | note_f1, notei_f1, sim_chr, sim_grv, ca, cs, onset_xor, note_overlap | 8 |
| `DistributionResult` | pd, dd | 2 |

---

## Metrics Reference

### A. Harmony & Tonality (7)

Sources: [Jazz Transformer](https://archives.ismir.net/ismir2020/paper/000339.pdf) (ISMIR 2020), [C-RNN-GAN](https://arxiv.org/abs/1611.09904) (NeurIPS-W 2016), [MuseGAN](https://arxiv.org/abs/1709.06298) (AAAI 2018), [FGG](https://arxiv.org/abs/2410.08435) (ICML 2025), [Yeh et al.](https://arxiv.org/abs/2001.02360) (2020), [EC2-VAE](https://arxiv.org/abs/2008.07122) (ISMIR 2020), [PopMAG](https://arxiv.org/abs/2008.07703) (ACM-MM 2020).

#### PCE — Pitch Class Entropy (single-file)

Shannon entropy of the 12-bin pitch-class histogram. Measures how dispersed the pitch-class distribution is. Lower PCE means the music is more tonally focused (fewer pitch classes dominate). The [Amadeus](https://arxiv.org/abs/2508.20665) paper reports PCE around 1.97–2.15 for well-trained models.

- Formula: `PCE = -sum(P(i) * log2(P(i)))` for i = 0..11
- Range: [0, log2(12)] ≈ [0, 3.585]
- Direction: lower is better (more tonally focused)
- Reference: [Wu & Yang, ISMIR 2020](https://archives.ismir.net/ismir2020/paper/000339.pdf)
- Implementation: [muspy.pitch_class_entropy()](https://github.com/salu133445/muspy/blob/main/src/muspy/metrics/metrics.py)
- Code: `harmony.py` → `pitch_class_entropy()`

#### SC — Scale Consistency (single-file)

The largest pitch-in-scale rate over all 24 major/minor scales. Indicates how well the music conforms to some diatonic scale. Higher SC means better key adherence. [Amadeus](https://arxiv.org/abs/2508.20665) reports SC around 0.96–0.98.

- Formula: `SC = max over (root, mode) of PISR(root, mode)`
- Range: [0, 1]
- Direction: higher is better
- Reference: [Mogren, NeurIPS-W 2016](https://arxiv.org/abs/1611.09904)
- Implementation: [muspy.scale_consistency()](https://github.com/salu133445/muspy/blob/main/src/muspy/metrics/metrics.py)
- Code: `harmony.py` → `scale_consistency()`

#### PISR — Pitch-in-Scale Rate (single-file)

Ratio of notes belonging to a specified musical scale (given root and mode) to total notes. Unlike SC which auto-selects the best key, PISR requires the user to specify the key. [MusPy](https://salu133445.github.io/muspy/metrics.html) documentation explicitly cites [MuseGAN (AAAI 2018)](https://arxiv.org/abs/1709.06298) as the source.

- Formula: `PISR = count(in-scale notes) / count(total notes)`
- Range: [0, 1]
- Direction: higher is better
- Reference: [Dong et al., AAAI 2018](https://arxiv.org/abs/1709.06298)
- Implementation: [muspy.pitch_in_scale_rate()](https://github.com/salu133445/muspy/blob/main/src/muspy/metrics/metrics.py)
- Code: `harmony.py` → `pitch_in_scale_rate(midi_path, root, mode)`

#### OOK — Out-of-Key Fraction (single-file)

Percentage of 16th-note steps containing at least one out-of-key note. Uses [Krumhansl-Schmuckler](https://en.wikipedia.org/wiki/Key_finding_algorithm) key detection to determine the key, then checks each 16th-note step. [FGG (ICML 2025)](https://arxiv.org/abs/2410.08435) reports that baseline methods have OOK around 2–4%, while well-controlled generation should achieve near 0%.

- Formula: `OOK = count(steps with out-of-key note) / count(total 16th-note steps)`
- Range: [0, 1]
- Direction: lower is better
- Reference: [Zhu et al., ICML 2025](https://arxiv.org/abs/2410.08435)
- Code: `harmony.py` → `out_of_key_fraction()`

#### CHE — Chord Histogram Entropy (single-file)

Shannon entropy of the chord-type histogram. Extracts chords per bar using chroma template matching (10 chord types: maj, min, dim, aug, 7, maj7, min7, dim7, sus4, sus2), builds a histogram, and computes its entropy. Higher CHE means more chord diversity.

- Formula: `CHE = -sum(p(c) * log2(p(c)))` over chord types c
- Range: [0, log2(C)] where C = number of distinct chord types
- Direction: higher is better (more diverse chords)
- Reference: [Yeh et al., 2020](https://arxiv.org/abs/2001.02360)
- Code: `harmony.py` → `chord_histogram_entropy()`

#### CA — Chord Accuracy (pairwise)

Exact-match accuracy between predicted and reference chord labels. Two methods available:

- **DP method** (default): Beat-level chord recognition using dynamic programming from [music-x-lab/midi-chord-recognition](https://github.com/music-x-lab/midi-chord-recognition). Used by [FGG (ICML 2025)](https://arxiv.org/abs/2410.08435) for Direct Chord Accuracy (DCA). Chords are compared per beat after normalizing to root:major/minor.
- **Viterbi method**: Bar-level HMM Viterbi decoder from [GETMusic (IJCAI 2025)](https://arxiv.org/abs/2305.10841), using Magenta's chord inference. Chords are compared per bar.

[FGG](https://arxiv.org/abs/2410.08435) notes that exact-match accuracy may not capture nuanced harmonic similarity (e.g., C major vs Cmaj7 is harmonically close but counts as a mismatch), which motivates the CS metric.

- Formula: `CA = count(matching frames) / count(total frames)`
- Range: [0, 1]
- Direction: higher is better
- Reference: [FGG, ICML 2025](https://arxiv.org/abs/2410.08435); [PopMAG, ACM-MM 2020](https://arxiv.org/abs/2008.07703)
- Code: `chord_accuracy.py` → `compute_ca(pred, ref, method='dp')`

#### CS — Chord Similarity (pairwise)

Cosine similarity of 256-dimensional chord progression embeddings from a pretrained [EC2-VAE](https://arxiv.org/abs/2008.07122) chord encoder (bidirectional GRU: 36 → 1024 → 256). Each MIDI file is divided into non-overlapping 2-measure segments (8 beats), each segment is encoded into a 256-dim latent vector, and cosine similarity is computed between corresponding segments. [FGG (ICML 2025)](https://arxiv.org/abs/2410.08435) uses this to capture nuanced harmonic similarity that exact-match CA misses.

- Formula: `CS = mean(cosine_sim(encode(pred_segment_i), encode(ref_segment_i)))`
- Range: [0, 1]
- Direction: higher is better
- Requires: PyTorch + model weights (29 MB, included in package)
- Reference: [Wang et al., ISMIR 2020](https://arxiv.org/abs/2008.07122)
- Code: `chord_similarity.py` → `compute_cs()`

---

### B. Rhythm & Temporal (6)

Sources: [D3PIA](https://github.com/jech2/D3PIA) (ICASSP 2026), [Jazz Transformer](https://archives.ismir.net/ismir2020/paper/000339.pdf) (ISMIR 2020), [Yang & Lerch](https://doi.org/10.1007/s00521-018-3849-7) (NCA 2018), [MusPy](https://arxiv.org/abs/2008.01951) (ISMIR 2020), [mir_eval](https://github.com/mir-evaluation/mir_eval) (ISMR 2014).

#### IOI — Mean Inter-Onset Interval (single-file)

Average time interval between consecutive note onsets, measured in seconds. Accounts for tempo changes via a tick-to-second mapper. Smaller IOI means denser note activity. Standard MIR feature; implementation convention from [D3PIA](https://github.com/jech2/D3PIA).

- Formula: `IOI = mean(diff(sorted_onset_times_in_seconds))`
- Range: [0, inf)
- Direction: descriptive (context-dependent)
- Code: `rhythm.py` → `mean_ioi()`

#### GS — Grooving Pattern Similarity (single-file)

Measures rhythmic pattern consistency within a piece. Each bar is represented as a 64-dimensional binary onset vector (64 positions per bar), and GS is the average normalized Hamming similarity between ALL pairs of bars.

**Important**: [MusPy](https://github.com/salu133445/muspy)'s `groove_consistency()` only compares adjacent bars (`groove_patterns[:-1] != groove_patterns[1:]`), which differs from the [Jazz Transformer (ISMIR 2020)](https://archives.ismir.net/ismir2020/paper/000339.pdf) paper that uses all bar pairs. This implementation follows the original paper.

- Formula: `GS = mean(1 - hamming(bar_i, bar_j))` for all i < j
- Range: [0, 1]
- Direction: higher is better (more consistent rhythm)
- Reference: [Wu & Yang, ISMIR 2020](https://archives.ismir.net/ismir2020/paper/000339.pdf)
- Code: `rhythm.py` → `grooving_pattern_similarity()`

#### Ngram — N-gram Note Diversity (single-file)

Ratio of unique 4-gram pitch-class sequences to total 4-grams. Higher diversity means the music uses more varied melodic patterns. Uses n=4 following [Yang & Lerch (NCA 2018)](https://doi.org/10.1007/s00521-018-3849-7).

- Formula: `Diversity = count(unique 4-grams) / count(total 4-grams)`
- Range: [0, 1]
- Direction: higher is better (more diverse)
- Reference: [Yang & Lerch, NCA 2018](https://doi.org/10.1007/s00521-018-3849-7)
- Code: `rhythm.py` → `ngram_diversity()`

#### EBR — Empty Beat Rate (single-file)

Ratio of beats with no note sounding. Lower EBR means fewer empty beats, indicating denser musical content. Originally from [Pypianoroll](https://github.com/salu133445/pypianoroll) (ISMIR 2018 LBD), implemented via [MusPy](https://github.com/salu133445/muspy).

- Formula: `EBR = count(empty beats) / count(total beats)`
- Range: [0, 1]
- Direction: lower is better (fewer empty beats)
- Reference: [Dong et al., ISMIR 2018](https://arxiv.org/abs/2008.01951)
- Code: `rhythm.py` → `empty_beat_rate()`

#### OXD — Onset XOR Distance (pairwise)

Mean absolute difference between aligned binary onset bar matrices. Both files are quantised to 16 positions per bar, padded to the same number of bars, then compared element-wise. Lower OXD means more similar onset patterns. Implementation from [D3PIA (ICASSP 2026)](https://github.com/jech2/D3PIA).

- Formula: `OXD = mean(|pred_binary - ref_binary|)` per bar position
- Range: [0, 1]
- Direction: lower is better (more similar onsets)
- Reference: [Choi et al., ICASSP 2026](https://github.com/jech2/D3PIA)
- Code: `rhythm.py` → `onset_xor_distance()`

#### NOvlp — Note Overlap (pairwise)

Average overlap score from [mir_eval](https://github.com/mir-evaluation/mir_eval)'s `transcription.precision_recall_f1_overlap()` function. Matches notes by onset time (within 50ms tolerance) and pitch, then computes the average overlap ratio of matched note pairs. Higher NOvlp means better note-level alignment.

- Formula: Uses `mir_eval.transcription.precision_recall_f1_overlap()` overlap return value
- Range: [0, 1]
- Direction: higher is better (better note alignment)
- Reference: [Raffel et al., ISMIR 2014](https://github.com/mir-evaluation/mir_eval)
- Code: `rhythm.py` → `note_overlap()`

---

### C. Polyphony & Quality (6)

Sources: [MuseGAN](https://arxiv.org/abs/1709.06298) (AAAI 2018), [MusPy](https://arxiv.org/abs/2008.01951) (ISMIR 2020). [MusPy documentation](https://salu133445.github.io/muspy/metrics.html) explicitly cites MuseGAN for polyphony and polyphony_rate.

#### Polyphony (single-file)

Average number of pitches played concurrently at active timesteps (timesteps where at least one note is sounding). Higher polyphony means thicker musical texture. [MuseGAN (AAAI 2018)](https://arxiv.org/abs/1709.06298) uses this to measure the degree of polyphony.

- Formula: `Polyphony = sum(active pitches at active timesteps) / count(active timesteps)`
- Range: [1, inf)
- Direction: descriptive
- Code: `quality.py` → `polyphony()`

#### PR — Polyphony Rate (single-file)

Ratio of timesteps where 2 or more pitches are simultaneously on. Called "polyphonicity" in [MuseGAN (AAAI 2018)](https://arxiv.org/abs/1709.06298). Higher PR means more polyphonic content.

- Formula: `PR = count(timesteps with >= 2 pitches) / count(total timesteps)`
- Range: [0, 1]
- Direction: descriptive
- Code: `quality.py` → `polyphony_rate()`

#### PE — Pitch Entropy (single-file)

Shannon entropy of the 128-bin pitch histogram (one bin per MIDI pitch 0–127). Higher PE means more diverse pitch usage. [Amadeus](https://arxiv.org/abs/2508.20665) reports PE around 2.20–2.91, where lower values indicate more focused pitch usage.

- Formula: `PE = -sum(P(i) * log2(P(i)))` for i = 0..127
- Range: [0, log2(128)] = [0, 7]
- Direction: descriptive (lower = more focused in some contexts)
- Code: `quality.py` → `pitch_entropy()`

#### Pitch Range (single-file)

Difference between the highest and lowest MIDI pitch used. Larger range means wider pitch span.

- Formula: `Range = max(pitch) - min(pitch)`
- Range: [0, 127]
- Direction: descriptive
- Code: `quality.py` → `pitch_range()`

#### N_p — Unique Pitches Used (single-file)

Number of distinct MIDI pitches (0–127) used in the piece. Higher means more pitch variety.

- Formula: `N_p = count(distinct MIDI pitches)`
- Range: [0, 128]
- Direction: descriptive
- Code: `quality.py` → `n_pitches_used()`

#### N_pc — Unique Pitch Classes Used (single-file)

Number of distinct pitch classes (0–11, i.e., pitch mod 12) used. Higher means more chromatic diversity.

- Formula: `N_pc = count(distinct pitch classes mod 12)`
- Range: [0, 12]
- Direction: descriptive
- Code: `quality.py` → `n_pitch_classes_used()`

---

### D. Note-level Pairwise (2)

Source: [USMA](https://arxiv.org/abs/2408.15176), NeurIPS 2025, Appendix C.1.

#### Note F1 (pairwise)

F1 score of greedy one-to-one note matching by (onset, pitch) on a quantised 16th-note grid. Notes are quantised by dividing onset tick by ticks-per-16th-note. The greedy matching is provably optimal for exact-match keys (onset + pitch tuples).

- Formula: `F1 = 2 * P * R / (P + R)` where `P = matched / pred_count`, `R = matched / ref_count`
- Range: [0, 1]
- Direction: higher is better
- Reference: [USMA, NeurIPS 2025](https://arxiv.org/abs/2408.15176)
- Code: `note_f1.py` → `compute_all()`

#### Notei F1 (pairwise)

Same as Note F1 but the matching key includes the instrument (MIDI program number). For single-instrument MIDI (e.g., solo piano), Notei F1 equals Note F1 since all notes share the same program.

- Formula: Same as Note F1 with key = (onset, pitch, instrument)
- Range: [0, 1]
- Direction: higher is better
- Reference: [USMA, NeurIPS 2025](https://arxiv.org/abs/2408.15176)
- Code: `note_f1.py` → `compute_all()`

---

### E. Bar-level Pairwise (2)

Source: [MuseMorphose](https://arxiv.org/abs/2105.04090), Wu & Yang, IEEE/ACM TASLP 2023.

#### simChr — Chroma Similarity (pairwise)

For each bar, a 12-dimensional L2-normalised chroma vector (pitch-class histogram, count-based) is extracted. For each generated bar, the maximum cosine similarity over all reference bars is computed, then averaged across all generated bars. Empty bars fall back to a uniform vector (similarity = 1.0 with itself).

- Formula: `simChr = mean over gen bars of max over ref bars of cosine(chroma_gen, chroma_ref)`
- Range: [0, 1]
- Direction: higher is better
- Reference: [Wu & Yang, IEEE/ACM TASLP 2023](https://arxiv.org/abs/2105.04090)
- Code: `similarity.py` → `compute_all()`

#### simGrv — Groove Similarity (pairwise)

Same aggregation as simChr but using 48-dimensional onset-position vectors (pos_per_bar=48 = 4 beats x 12 sub-divisions) instead of chroma. Measures rhythmic similarity at the bar level.

- Formula: `simGrv = mean over gen bars of max over ref bars of cosine(groove_gen, groove_ref)`
- Range: [0, 1]
- Direction: higher is better
- Reference: [Wu & Yang, IEEE/ACM TASLP 2023](https://arxiv.org/abs/2105.04090)
- Code: `similarity.py` → `compute_all()`

---

### F. Distribution-level (2)

Sources: [SongMASS](https://arxiv.org/abs/2012.05168) (ACM-MM 2020), [TeleMelody](https://arxiv.org/abs/2109.09617) (2021). Implementation verified against [microsoft/muzic](https://github.com/microsoft/muzic) `telemelody/evaluation/cal_similarity.py`.

#### PD — Pitch Distribution (pairwise)

Overlap area between L1-normalised 128-bin pitch histograms of predicted and reference MIDI files. Each note increments its MIDI pitch bin by 1. Higher PD means more similar pitch distributions.

- Formula: `PD = sum(min(norm_a[i], norm_b[i]))` for i = 0..127
- Range: [0, 1]
- Direction: higher is better
- Reference: [SongMASS, ACM-MM 2020](https://arxiv.org/abs/2012.05168)
- Code: `distribution.py` → `compute_all()`

#### DD — Duration Distribution (pairwise)

Overlap area between L1-normalised 64-bin duration histograms. Durations are quantised to bins based on the minimum duration in the piece. Higher DD means more similar duration distributions.

- Formula: `DD = sum(min(norm_a[i], norm_b[i]))` for i = 0..63
- Range: [0, 1]
- Direction: higher is better
- Reference: [SongMASS, ACM-MM 2020](https://arxiv.org/abs/2012.05168)
- Code: `distribution.py` → `compute_all()`

---

## Chord Recognition

smg-metrics includes a full chord recognition pipeline for the CA and CS metrics:

```python
from smg_metrics import recognize_chords, recognize_chords_beat

# Interval-level chord recognition (DP method, 17 qualities + inversions)
chords = recognize_chords("song.mid")
for iv in chords:
    print(f"{iv.start:.2f}s - {iv.end:.2f}s: {iv.label}")
# Example output:
#   0.00s - 2.50s: C:maj
#   2.50s - 5.00s: G:7/5

# Beat-level chord labels
beat_chords = recognize_chords_beat("song.mid")
# Returns list of (start, end, label) tuples per beat
```

The DP chord recognition pipeline (adapted from [music-x-lab/midi-chord-recognition](https://github.com/music-x-lab/midi-chord-recognition)):

1. Extract beat/downbeat positions from MIDI tempo map
2. Quantise notes to beat grid, compute per-beat treble + bass chroma (12-dim each)
3. Channel-weighted aggregation (thickness reweighting + bass boost)
4. Score 17 chord templates per beat (with bass bonus for inversions)
5. Dynamic-programming decode with span-length reward and transition penalty
6. Output interval-level chord labels with inversions

For CA, two backends are available:
- `method='dp'` (default): Beat-level DP from music-x-lab, used by [FGG](https://arxiv.org/abs/2410.08435)
- `method='viterbi'`: Bar-level HMM from [GETMusic](https://arxiv.org/abs/2305.10841)

---

## Model Weights

The CS metric uses a pretrained chord encoder from [EC2-VAE / PolyDisVAE](https://arxiv.org/abs/2008.07122) (Wang et al., ISMIR 2020):

| Property | Value |
|----------|-------|
| Architecture | Bidirectional GRU (input: 36-dim, hidden: 1024, output: 256) |
| Input format | (batch, 8, 36) — 8 beats × [root(12) + chroma(12) + bass(12)] |
| Training data | EC2-VAE chord progressions |
| File size | 29 MB (pruned from 104 MB full model, 72% reduction) |
| Location | `smg_metrics/model_weights/polydis-v1-chd_encoder_only.pt` |
| License | Inherits from original PolyDisVAE model |

The model weights are bundled in the PyPI package. No manual download required.

```python
from smg_metrics import clear_cs_model_cache

# CS model is cached automatically for batch evaluation
for pred, ref in file_pairs:
    cs = compute_cs(pred, ref)  # Model loaded once, reused

# Free memory after batch
clear_cs_model_cache()
```

---

## Test Suite

```bash
# Quick single-file test (15 metrics on one file)
python test.py --single-only data/ref/seg_0_8.mid

# Full test on all data files (auto multi-core + progress bar)
python test.py data/pred/ data/ref/

# Pairwise only (10 metrics, needs >= 2 files)
python test.py --pair-only data/pred/seg_0_8.mid data/ref/seg_0_8.mid

# Select specific metrics only
python test.py --only pce,ebr,note_f1,ca,sim_chr data/pred/seg_0_8.mid data/ref/seg_0_8.mid

# Save results to JSON
python test.py data/pred/ data/ref/ --json
```

| Flag | Description |
|------|-------------|
| `--single-only` | Run only single-file metrics (15 metrics per file) |
| `--pair-only` | Run only pairwise metrics (10 metrics per pair, needs >= 2 files) |
| `--only METRIC ...` | Run only the specified metrics (see `--list-metrics` for names) |
| `--json` | Save results to `test_results.json` in project root |

Notes:
- When evaluating 2+ files, `test.py` uses multi-core evaluation with a [tqdm](https://github.com/tqdm/tqdm) progress bar.
- Self-consistency checks verify that comparing a file to itself yields perfect scores (Note F1=1.0, CA=1.0, OXD=0.0, etc.).
- Output file: `test_results.json` in the project root.

---

## Project Structure

```
smg_metric/
  smg_metrics/
    __init__.py          # Lazy imports for fast CLI startup
    __main__.py          # CLI entry: python -m smg_metrics
    cli.py               # argparse CLI with --harmony/--rhythm/--quality flags
    harmony.py           # PCE, SC, PISR, OOK, CHE (single-file harmony)
    rhythm.py            # IOI, GS, Ngram, EBR, OXD, NOvlp (rhythm + rhythmic pair)
    quality.py           # Poly, PR, PE, Range, Np, Npc (single-file quality)
    note_f1.py           # Note F1, Notei F1 (note-level pair)
    similarity.py        # simChr, simGrv (bar-level pair)
    chord_accuracy.py    # CA with DP + Viterbi backends
    chord_recognition.py # DP chord recognition pipeline (music-x-lab)
    chord_similarity.py  # CS with EC2-VAE encoder
    distribution.py      # PD, DD (distribution-level pair)
    _io.py               # Shared MIDI I/O: Note3, Note4, extract_notes, load_midi
    _stats.py            # Shared stats: histogram_overlap
    model_weights/
      polydis-v1-chd_encoder_only.pt  # 29 MB EC2-VAE chord encoder
      README.md
  data/                  # Test MIDI files (9 gen + 9 gt segments)
  test.py                # Full test suite (25 metrics + self-consistency)
  pyproject.toml         # Package config (setuptools, PyPI)
  README.md              # This file
  LICENCE                # MIT
```

---

## v5.4.3 Changelog

### Structural Refactoring

Reorganized all metric files by category for clean decoupling:

| New file | Metrics | Merged from |
|---------|---------|-------------|
| `harmony.py` | PCE, SC, PISR, OOK, CHE | muspy_ext + out_of_key + structural |
| `rhythm.py` | IOI, GS, Ngram, EBR, OXD, NOvlp | rhythmic + structural + muspy_ext |
| `quality.py` | Poly, PR, PE, Range, Np, Npc | muspy_ext |
| `note_f1.py` | Note F1, Notei F1 | (unchanged) |
| `similarity.py` | simChr, simGrv | (unchanged) |
| `distribution.py` | PD, DD | (unchanged) |

Deleted files: `muspy_ext.py`, `structural.py`, `out_of_key.py`, `rhythmic.py`, `advanced.py`, `_edit.py`

### Metric Verification

All 25 metrics verified against original literature descriptions and source code:
- MusPy source code confirmed for PCE, SC, PISR, Poly, PR, PE, Range, Np, Npc, EBR
- [Amadeus](https://arxiv.org/abs/2508.20665) paper confirms SC↑, PE↓, PCE↓ directions
- [FGG](https://arxiv.org/abs/2410.08435) paper confirms OOK (16th-note steps), CA (beat-level exact match), CS (2-measure segments, 256-dim, cosine)
- [SongMASS](https://arxiv.org/abs/2012.05168) `cal_overlap` implementation confirmed for PD/DD
- GS implementation confirmed different from MusPy's `groove_consistency` (all pairs vs adjacent only)

### Changes

- Version: 5.3.0 -> 5.4.3
- Total metrics: 52 -> 25
- CLI: New `--harmony`, `--rhythm`, `--quality`, `--all-single` flags
- test.py: Updated to use new module structure
- pyproject.toml: Excluded temp directories from packaging
- _stats.py: Removed unused kl_divergence and overlap_normal functions

---

## License

MIT — see [LICENCE](LICENCE).

## Citation

```bibtex
@software{smg_metrics,
  title  = {smg-metrics: Objective Evaluation Metrics for Symbolic Music Generation},
  author = {Temmie Pratt},
  year   = {2026},
  url    = {https://github.com/OlyMarco/smg_metric},
}
```
