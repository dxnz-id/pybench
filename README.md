# 🧪 PyBench

[![GitHub](https://img.shields.io/badge/GitHub-dxnz--id-181717?style=flat-square&logo=github)](https://github.com/dxnz-id)
[![Repo](https://img.shields.io/badge/Repo-PyBench-181717?style=flat-square&logo=github)](https://github.com/dxnz-id/pybench)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

> A cross-platform, terminal-based hardware benchmark tool written in Python.  
> Measures CPU, Memory, Disk, and GPU performance — with real-time system monitoring and structured JSON export.

---

## Overview

PyBench is a lightweight benchmark suite designed to stress-test and profile hardware components using pure Python and OpenCL. It provides reproducible, comparable results across machines with a clean terminal UI powered by [Rich](https://github.com/Textualize/rich).

---

## Features

| Module      | Tests                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------- |
| **CPU**     | Single-thread math, multi-thread parallel, zlib compression, PBKDF2 encryption, prime sieve                         |
| **Memory**  | Sequential bandwidth, random access latency, memoryview copy speed, allocation stress                               |
| **Disk**    | SEQ1M Q8T1 read/write, RND4K Q32T1 read/write, total IOPS                                                           |
| **GPU**     | OpenCL compute kernel (sqrt · log · sin), host↔device memory bandwidth                                              |
| **Monitor** | Real-time CPU %, frequency, RAM usage, GPU %, temperature, VRAM, disk I/O, network — with Avg / Min / Max / Std Dev |
| **Scoring** | Weighted score per module + overall composite score                                                                 |
| **Export**  | Full results saved as structured JSON with timestamp-based run ID                                                   |

---

## Demo

```text
╔══════════════════════════════════════╗
║         PyBench  v1.0                ║
║  Python Hardware Benchmark Tool      ║
╚══════════════════════════════════════╝

Select benchmarks (e.g. 1,2,3) or 'all' (all): all

⠋ Running CPU Benchmark...      ████████████████████ 100%
⠋ Running Memory Benchmark...   ████████████████████ 100%
⠋ Running Disk Benchmark...     ████████████████████ 100%
⠋ Running GPU Benchmark...      ████████████████████ 100%

Benchmark Completed Successfully!

🔍 RAW BENCHMARK DETAILS
┌───────────┬─────────────────────────┬──────────────────┐
│ Component │ Test Case               │           Result │
├───────────┼─────────────────────────┼──────────────────┤
│ DISK      │ Sequential Read (Q8T1)  │        8.20 GB/s │
│ DISK      │ Sequential Write (Q8T1) │      626.00 MB/s │
│ DISK      │ Random Read (Q32T1)     │    40787.11 IOPS │
│ DISK      │ Random Write (Q32T1)    │    17604.28 IOPS │
│ MEMORY    │ Sequential Bandwidth    │        4.09 GB/s │
│ MEMORY    │ Random Access Latency   │  529456.12 Ops/s │
│ MEMORY    │ Memory Copy Speed       │        5.63 MB/s │
│ CPU       │ Multi-thread (Math)     │        9,882 Ops │
│ CPU       │ Single-thread (Math)    │        4,319 Ops │
│ GPU       │ Compute Performance     │      2.02 MOps/s │
│ GPU       │ VRAM Bandwidth          │              N/A │
└───────────┴─────────────────────────┴──────────────────┘

🏆 SCORE SUMMARY
┌───────────────┬───────────┐
│ Category      │     Score │
├───────────────┼───────────┤
│ CPU           │     9,260 │
│ MEMORY        │     4,594 │
│ DISK          │    70,520 │
│ GPU           │        10 │
│ OVERALL SCORE │    21,096 │
└───────────────┴───────────┘

📊 HARDWARE MONITORING SUMMARY
┌───────┬──────────────────────────────────────────────────┐
│ Group │ Metric Details (AVG / MIN-MAX)                   │
├───────┼──────────────────────────────────────────────────┤
│ CPU   │ Usage: 36.17% | Clock: 763MHz | Temp: 64.6°      │
│ RAM   │ Usage: 61.27% (61.1% - 61.9%)                    │
│ GPU   │ N/A (No GPU Sensor detected)                     │
└───────┴──────────────────────────────────────────────────┘

📂 Report: results/run_20260501_175030.json
```

---

## Project Structure

```text
pybench/
│
├── main.py                  # Entry point — CLI selector & benchmark runner
├── config.py                # Duration, thread count, result path settings
├── requirements.txt         # Standard pip dependencies
├── pyproject.toml           # Modern Python packaging (uv/build)
├── uv.lock                  # Lockfile for reproducible environments
│
├── modules/
│   ├── cpu_benchmark.py     # Single/multi-thread, compression, encryption, prime sieve
│   ├── memory_benchmark.py  # Bandwidth, latency, copy speed, allocation
│   ├── disk_benchmark.py    # Sequential & random I/O, IOPS
│   └── gpu_benchmark.py     # OpenCL compute kernel + VRAM bandwidth
│
├── monitor/
│   ├── system_monitor.py    # Background thread — polls psutil & nvidia-smi every 0.5s
│   └── aggregator.py        # Computes Avg / Min / Max / Std Dev from raw samples
│
├── scoring/
│   └── scorer.py            # Score formulas per module + overall composite
│
├── reporter/
│   └── exporter.py          # Serializes results to timestamped JSON
│
├── ui/
│   ├── dashboard.py         # Live stats panel (Rich Live)
│   ├── formatter.py         # Welcome screen & log helpers
│   └── results_view.py      # Final results table renderer
│
└── results/                 # Auto-created — stores run_YYYYMMDD_HHMMSS.json
```

---

## Installation

**Requirements:** Python 3.12+, pip

```bash
# 1. Clone the repository
git clone https://github.com/dxnz-id/pybench.git
cd pybench

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **Note — OpenCL:** GPU benchmarking requires OpenCL drivers.
>
> - NVIDIA: install CUDA Toolkit
> - Intel / AMD integrated: install the vendor's OpenCL runtime
> - If OpenCL is unavailable, the GPU compute test falls back to a CPU scalar implementation automatically.

---

## Usage

```bash
# Run interactively (recommended)
python main.py

# Run with verbose logging
python main.py --verbose
```

At the prompt, enter the benchmarks you want to run:

```text
Select benchmarks (e.g. 1,2,3) or 'all' (all): all

1 → CPU Benchmark
2 → Memory Benchmark
3 → Disk Benchmark
4 → GPU Benchmark
all → Run everything
```

Results are automatically saved to `results/run_<timestamp>.json`.

---

## Benchmark Methodology

All tests use a **time-bounded loop** pattern: each sub-test runs for a fixed duration (`DEFAULT_DURATION`, default **10 seconds**) and scores by counting how many operations were completed — not by measuring how long a fixed task takes.

---

### CPU

Focuses on raw processor throughput across floating-point math, cryptography, compression, and parallel workloads.

**Single-thread** — Measures pure single-core performance by repeatedly executing a 500-iteration FPU-heavy loop (`sqrt · log · sin`). Stresses the Floating Point Unit (FPU) without any parallelism.

```python
def workload():
    x = 0.0
    for i in range(1, 500):
        x += math.sqrt(i) * math.log(i + 1) * math.sin(i)
```

**Multi-thread** — Dispatches the same workload across all available logical cores via `ThreadPoolExecutor`. Scores are the sum of all thread completions, reflecting total parallel throughput.

```python
with ThreadPoolExecutor(max_workers=cores) as ex:
    futures = [ex.submit(self._run_timed, workload) for _ in range(cores)]
    total = sum(f.result() for f in futures)
```

**Compression** — Repeatedly compresses a 64 KB random buffer with `zlib` at level 6. Stresses integer instruction throughput and memory manipulation.

**Encryption** — Runs `hashlib.pbkdf2_hmac(sha256)` on 64 KB data per iteration. Simulates cryptographic workloads found in real-world security applications.

**Prime Sieve** — Implements the Sieve of Eratosthenes up to n = 100,000 using a `bytearray`. Tests CPU branching logic and array traversal patterns.

```python
def sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i*i::i] = bytearray(len(s[i*i::i]))
```

---

### Memory

Focuses on RAM throughput and latency — how fast the system can move large blocks of data and how quickly it responds to non-sequential access patterns.

**Sequential Bandwidth** — Allocates a 128 MB `bytearray`, copies it into a new buffer (write pass), then performs a single read. Measures raw bulk transfer speed in MB/s.

```python
BUF_SIZE = 128 * 1024 * 1024
buf2 = bytearray(BUF_SIZE)
buf2[:] = buf        # write pass
_ = buf2[0]          # read pass
total_bytes += BUF_SIZE * 2
```

**Random Access Latency** — Populates a 64 MB in-memory list of floats, then performs random index reads. Simulates cache miss pressure since accesses do not follow a predictable pattern. Result reported in ops/s.

**Copy Speed** — Uses Python's `memoryview` to copy a 256 MB buffer directly at the memory level, minimizing Python object overhead. Reported in GB/s.

```python
mv_dst[:] = mv_src   # low-level bulk copy via memoryview
```

**Allocation Stress** — Continuously allocates and discards 1 MB `bytearray` objects, then forces a `gc.collect()`. Tests OS memory management and the Python garbage collector under sustained pressure.

---

### Disk

Modeled after the **CrystalDiskMark** methodology. A 1 GB temporary file (`CDM_test.tmp`) is created before testing and deleted automatically on completion.

| Sub-test        | Block Size | Threads | Use case simulated                               |
| --------------- | ---------- | ------- | ------------------------------------------------ |
| **SEQ1M Q8T1**  | 1 MB       | 8       | Large file transfers (video, ISO, game installs) |
| **RND4K Q32T1** | 4 KB       | 32      | OS boot, app launch, small file I/O (IOPS-bound) |

Sequential tests move through the file in ordered offsets. Random tests use `random.randint` to seek to arbitrary 4 KB-aligned positions, stressing the drive's IOPS capability. All writes call `os.fsync()` to ensure data is committed to hardware rather than OS cache.

```python
# RND4K — random sector seek before every operation
pos = random.randint(0, self.file_size // block_size - 1) * block_size
f.seek(pos)
f.write(data)   # or f.read(block_size)
```

---

### GPU

Uses **PyOpenCL** to execute compute workloads on the GPU. If no OpenCL platform is detected, the compute test falls back to a CPU scalar loop automatically — `vram_bw` returns `null` in that case.

**GPU Compute** — Compiles and dispatches an OpenCL C kernel on-the-fly that applies `sqrt · log · sin` to every element of a 1M-element `float32` array in parallel across all GPU compute units. Result is reported in **MOps/s** (million operations per second).

```c
__kernel void compute(__global float* src, __global float* dst) {
    int i = get_global_id(0);
    dst[i] = sqrt(src[i]) * log(src[i] + 1.0f) * sin(src[i]);
}
```

**VRAM Bandwidth** — Repeatedly transfers a 256 MB `float32` NumPy array from host RAM to device VRAM (`cl.Buffer` with `COPY_HOST_PTR`) and back (`cl.enqueue_copy`). Measures PCIe bus throughput and VRAM read/write speed in MB/s.

---

### System Monitor

A background daemon thread polls system state every `0.5s` for the entire duration of the benchmark run using `psutil`, `nvidia-smi` (via subprocess), and WMI fallbacks. Raw samples are collected into lists and aggregated into **Avg / Min / Max / Std Dev** by `monitor/aggregator.py` after the run completes. Monitored metrics include: CPU usage %, CPU frequency, RAM usage, GPU usage %, GPU temperature, VRAM used, disk I/O speed, and network throughput.

---

## Scoring System

Higher score = better performance. Scores are unitless integers calibrated so mid-range hardware scores roughly in the same order of magnitude across modules.

```
CPU Score    = single_ops + (multi_ops × 0.5)

Memory Score = (seq_bw × 0.4) + (copy_gb × 500) + (rand_lat / 5,000)

Disk Score   = (seq_total_MB × 0.05) + (rnd_total_IOPS × 1.2)

GPU Score    = (compute_MOps × 5) + (vram_bw_MB × 0.1)

Overall      = average of all modules with score > 0
```

---

## Output Format

Each run produces a JSON file in `results/` with the following structure:

```json
{
  "run_id": "20260428_122852",
  "timestamp": "Tue Apr 28 12:28:52 2026",
  "hardware": {
    "cpu": "13th Gen Intel(R) Core(TM) i5-13450HX",
    "cpu_cores": 10,
    "cpu_threads": 16,
    "cpu_base_clock": "2400.00 MHz",
    "ram": "11.71 GB",
    "gpu": "NVIDIA GeForce RTX 3050 6GB Laptop GPU",
    "gpu_vram": "6144.0 MB",
    "disk_total": "237.41 GB",
    "os": "Windows 11"
  },
  "system_monitor": {
    "cpu": { "avg": 20.32, "min": 0.0, "max": 73.7, "std_dev": 15.02 },
    "cpu_freq": {
      "avg": 2171.2,
      "min": 1520.0,
      "max": 2400.0,
      "std_dev": 386.97
    },
    "ram": { "avg": 59.56, "min": 57.0, "max": 63.6, "std_dev": 2.05 },
    "gpu": { "avg": 4.11, "min": 0.0, "max": 48.0, "std_dev": 9.59 },
    "gpu_temp": { "avg": 44.21, "min": 43.0, "max": 49.0, "std_dev": 1.77 }
  },
  "benchmark_results": {
    "cpu": {
      "single": 126391,
      "multi": 184701,
      "compress": 5843,
      "encrypt": 2506329,
      "prime": 45899
    },
    "memory": {
      "seq_bw": 4634.33,
      "rand_lat": 1430777.29,
      "copy": 8.23,
      "alloc": 3077.19
    },
    "disk": {
      "seq_write": 3566.22,
      "seq_read": 5960.72,
      "rand_write": 70188.45,
      "rand_read": 75401.3,
      "iops": 145589.76
    },
    "gpu": { "compute": 3545.31, "vram_bw": 1216.46, "opencl_ok": true }
  },
  "scores": {
    "cpu": 218741,
    "memory": 6254,
    "disk": 175184,
    "gpu": 17848,
    "overall": 104506
  }
}
```

---

## Dependencies

| Package        | Purpose                                          |
| -------------- | ------------------------------------------------ |
| `rich`         | Terminal UI — progress bars, live panels, tables |
| `psutil`       | CPU, RAM, and disk metrics                       |
| `nvidia-ml-py` | Hardware identification (NVML) in exporter.py    |
| `py-cpuinfo`   | Detailed CPU model information                   |
| `pyopencl`     | GPU compute kernel execution                     |
| `numpy`        | Array operations for GPU benchmark               |

---

## Limitations

- **CPU temperature** requires platform-specific drivers (e.g., OpenHardwareMonitor on Windows, `lm-sensors` on Linux). PyBench reports `null` if unavailable.
- **GPU monitoring** via `nvidia-smi` only supports NVIDIA GPUs. Intel/AMD integrated graphics are not monitored via this method (though hardware info might still be detected via OpenCL), and temperature/usage stats may fall back to WMI on Windows if `nvidia-smi` is unavailable.
- **Disk benchmark** creates a 1 GB temporary file. Ensure the target directory has sufficient free space.
- **Python GIL** affects multi-thread CPU scores — results reflect Python-level concurrency, not raw hardware throughput. Results are still consistent and comparable across machines running the same Python version.
- **Score comparability** is only valid between runs using the same `DEFAULT_DURATION` setting.

---

## Support the Developer

If you find PyBench useful and would like to support its development, you can buy me a coffee:

<a href="https://www.ko-fi.com/dxnzid">
  <img src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" width="160" alt="Support on Ko-fi" />
</a>

---

_PyBench is a hardware benchmarking utility built to explore and demonstrate systems-level programming performance in Python._  
_Results are relative benchmarks and should not be compared to native-compiled tools such as CrystalDiskMark, Cinebench, or 3DMark._  
_Disclaimer: This program was primarily written with the assistance of AI._
