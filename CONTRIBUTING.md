# Contributing to PyBench

First off, thank you for considering contributing to PyBench! It's people like you that make open-source tools better for everyone.

This document outlines the guidelines and architectural rules for contributing to the project. By following these guidelines, you help us keep the codebase clean, stable, and easy to maintain.

---

## 1. Contribution Scope

Before starting work on a major feature, please check if it aligns with PyBench's goals.

**✅ We Welcome:**

- New benchmark workloads (e.g., Cryptography, Network, Machine Learning).
- Performance optimizations for existing tests.
- UI/UX enhancements in the Rich terminal dashboard.
- New hardware sensor fallbacks for systems currently unsupported by the monitor.
- Bug fixes and documentation improvements.

**❌ Please Avoid:**

- **Heavy External Dependencies:** We want to keep the tool lightweight and fast to install.
- **Platform-specific Hacks:** Code that only works on one OS without a graceful fallback on others.
- **GUI Frameworks:** PyBench is strictly a terminal-based interface (TUI) tool.

---

## 2. Setting Up the Development Environment

PyBench uses `uv` for lightning-fast environment management.

1.  **Fork and Clone:**
    Fork the repository on GitHub, then clone your fork locally:

    ```bash
    git clone https://github.com/YOUR_USERNAME/pybench.git
    cd pybench
    ```

2.  **Install Dependencies:**
    Set up the virtual environment and install dependencies using `uv`:

    ```bash
    uv venv
    uv sync
    ```

    _(Alternatively, you can use `uv pip install -r requirements.txt`)_

3.  **Run the Project:**
    Verify everything works by running:
    ```bash
    uv run python main.py -v
    ```

---

## 3. Coding Standards & Tooling

To maintain a clean and professional codebase, we enforce strict formatting rules.

- **Formatter:** We use **Black**. All code must be formatted with Black before submitting.
- **Linter:** We use **flake8** to catch logical and stylistic errors.
- **Line Length:** Strict **88 characters** limit (Black's default).
- **Readability:** Avoid overly complex one-liners. Prioritize readable and maintainable code over clever tricks.

---

## 4. Architectural Guidelines (The Core)

PyBench is designed around a specific set of architectural rules. Please read this carefully before adding new features.

### A. Adding a New Benchmark

Benchmarks in PyBench **DO NOT** measure how long a fixed task takes. Instead, they measure **how much work is done within a fixed time window**.

- **Time-bounded Loop:** You must use `time.perf_counter()` checked against `self.duration`.
- **Fixed Iteration is Forbidden:** Do not use `for i in range(1000):` as the primary loop constraint. Hardware speeds vary wildly, and fixed loops do not scale.
- **Return Metric:** Must return _throughput_ (e.g., Ops/sec, MB/s, IOPS). NEVER return total elapsed time.
- **Reproducibility:** If your test relies on random data generation, use a seeded `random.Random()` instance to ensure the cache pressure is deterministic across runs.

**Standard Benchmark Template:**

```python
import time

def new_benchmark(self):
    """Description of what this tests. Result reported in Ops/s."""
    count = 0
    start = time.perf_counter()

    # Time-bounded loop
    while time.perf_counter() - start < self.duration:
        # --- YOUR WORKLOAD HERE ---
        count += 1

    elapsed = time.perf_counter() - start
    # Return operations per second (throughput)
    return count / elapsed if elapsed > 1e-6 else 0.0
```

### B. Monitoring System Rules

The `monitor/system_monitor.py` runs in a background thread and updates the UI real-time.

- **Non-blocking:** The polling logic must be extremely lightweight.
- **Low Overhead:** Do not introduce heavy subprocess calls without aggressive timeouts or caching.
- **Graceful Degradation:** If a hardware sensor fails (e.g., unable to read GPU temp), the function must catch the exception and return `0`, `None`, or `"N/A"`. It must **never** crash the monitoring thread.

### C. Scoring System Integrity

The `scorer.py` module maintains historical consistency so users can compare scores across versions.

- **Rule:** Do not blindly alter scoring weights for existing tests.
- If a new test is added, its score multiplier must be carefully calibrated so that a modern high-end consumer system scores roughly `50,000` to `100,000` points for that specific category. Document your scoring rationale in the PR.

---

## 5. Pre-PR Checklist

Before opening a Pull Request, verify that your branch passes this checklist:

- [ ] Benchmarks complete 100% without crashing (`uv run python main.py`).
- [ ] Output JSON (`results/run_*.json`) is structurally valid and contains the new metrics.
- [ ] No unexplained `NaN`, `null`, or `0.0` values in the final metrics (unless hardware is genuinely missing).
- [ ] The performance scores remain sane and within expected boundaries.
- [ ] Code passes `flake8` and is formatted completely with `black .`.

---

## 6. Commit Convention

We use Conventional Commits to keep our history clean and readable. Please use one of the following prefixes for your commits:

- `feat:` A new feature or benchmark.
- `fix:` A bug fix (e.g., fixing a broken sensor parser).
- `perf:` A code change that improves performance.
- `docs:` Updates to documentation (README, CONTRIBUTING, etc).
- `refactor:` Code restructuring without changing logic or behavior.
- `chore:` Routine tasks, dependency updates, or tooling configuration.

---

## 7. Good First Contributions

If you are new to the project and looking for a place to start, consider these areas:

- Improving error handling and fallbacks for WMI (Windows) or NVML (Nvidia) edge cases.
- Adding robust unit tests for `reporter/aggregator.py` or `ui/formatter.py`.
- Refining the Rich UI layout to ensure it renders perfectly on smaller terminal windows.

Again, thank you for contributing to PyBench! 🚀
