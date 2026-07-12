# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal Python 3 playground for working through programming puzzles and books — primarily Knuth's *The Art of
Computer Programming* (TAOCP), *Gödel, Escher, Bach* (GEB), general search problems, and (in an optional separate
private repo) Project Euler. There is no application entry point or deployable artifact; each module is a
self-contained exploration, runnable and testable on its own.

## Setup

```bash
uv sync                        # create .venv and install deps (auto-installs Python 3.11 if needed)
```

## Common commands

```bash
./run <script.py> [args]       # uv run python <script.py> — run any module directly
./runtests [options]           # discover and run all inline unittest suites under the repo root
```

`runtests` wraps `runtests.py` (custom `unittest` runner with per-test timing). Useful flags:

- `-l`, `--longtests` — include slow tests (methods named `test_long_*`); excluded by default
- `-p PATTERN`, `--pattern PATTERN` — glob of modules to discover (default `*.py`)
- `-t SECONDS`, `--threshold SECONDS` — report tests slower than this as "slow" (default 5.0)
- `-v {0,1,2}` — verbosity

Run a single test directly with stdlib unittest (dotted path mirrors the directory path):

```bash
uv run python -m unittest com.github.wallberg.taocp.Backtrack.Test.test_n_queens
```

There is no separate lint/format command wired up; `pycodestyle` is a listed dependency for manual style checks
(`uv run pycodestyle <path>`).

Ignore the root `Makefile` — it is a stale leftover from an earlier Go-based iteration of this repo (`go build`,
`GOPACKAGES`, `.env`) and does not apply to the current Python codebase.

## Architecture

### Package layout

Code lives under `com/github/wallberg/<topic>/`, a Java-style reverse-DNS namespace (mirroring the GitHub
repo path) purely so modules can be imported as `com.github.wallberg.<topic>.<Module>`. Every directory needs an
`__init__.py`. Topics:

- `geb/` — puzzles from *Gödel, Escher, Bach* (e.g. `primes.py` recursively enumerates primes via the MU-puzzle-style
  formal system from Chapter 3; `mu_puzzle.py`).
- `search/` — general search algorithms (e.g. `Puzzle8.py`, an 8-puzzle solver).
- `taocp/` — TAOCP exercises and algorithm implementations, organized around Knuth's numbered algorithms
  (`Backtrack.py`, `DancingLinks.py`, `Trie.py`, `BooleanBasics.py`, `Commafree.py`, `Tuples.py`,
  `word_rectangles_exercise*.py`). `taocp.txt` at the repo root is the TAOCP table of contents kept for reference
  when cross-referencing section/exercise numbers used in comments and docstrings.
- `euler/` — Project Euler solutions. This is a **separate private repo**, not part of this one; it's gitignored
  here and only present locally if cloned per the README:
  `git clone git@github.com:wallberg/project-euler.git com/github/wallberg/euler`. Don't expect it to exist or be
  committable from this repo.

Knuth algorithm implementations follow the book's own structure closely: functions are commented with the book's
step labels (e.g. `# B1 [Initialize]`, `goto = 'B2'`) and implemented as explicit state-machine loops over those
labels rather than idiomatic control flow, so the code can be read side-by-side with the corresponding TAOCP
fascicle. Preserve that mapping (step labels, algorithm letter/number) when touching these files.

### Tests

There is no separate `tests/` tree for the Python code. Each module defines its own `class Test(unittest.TestCase)`
at the bottom of the file, alongside the code it tests, followed by:

```python
if __name__ == '__main__':
    unittest.main(exit=False)
```

`runtests` discovers these via `unittest`'s test discovery across the whole repo. Slow test methods are named
`test_long_...` (e.g. `test_long_n_queens`, `test_long_langford_pairs`) and are skipped unless `-l/--longtests` is
passed — follow this naming convention for any new expensive test.

The top-level `test/` directory is listed in `.gitignore` (`test/*`) and holds ad hoc local scratch files
(sample `.yaml`/`.go`/data files); it is not part of the Python test suite and nothing under it is tracked by git.

### Notable dependencies (see `pyproject.toml`)

`gmpy2` (fast arbitrary-precision arithmetic), `bitarray`, `networkx`, `numpy`, `more-itertools`, `ordered-set`,
`sortedcontainers`, `python-constraint` — several TAOCP/Euler modules lean on these rather than reimplementing
number-theory or graph primitives by hand.
