import time
import os
import random
import gc


class MemoryBenchmark:
    def __init__(self, duration=5):
        self.duration = duration

    # ── Sequential bandwidth ──────────────────────────────────────────────────

    def seq_bandwidth(self):
        """MB/s of raw memory read/write using bytearray copies."""
        BUF_SIZE = 128 * 1024 * 1024  # 128 MB
        buf = bytearray(os.urandom(BUF_SIZE))
        total_bytes = 0
        start = time.perf_counter()
        while time.perf_counter() - start < self.duration:
            # write pass
            buf2 = bytearray(BUF_SIZE)
            buf2[:] = buf
            # read pass
            _ = buf2[0]
            total_bytes += BUF_SIZE * 2  # write + read
            del buf2
        elapsed = time.perf_counter() - start
        del buf
        if elapsed < 1e-6:
            return 0.0
        return (total_bytes / elapsed) / (1024 ** 2)

    # ── Random access speed ───────────────────────────────────────────────────

    def random_latency(self):
        """IOPS of random 8-byte reads from a 64 MB buffer."""
        SIZE = 64 * 1024 * 1024
        INTS = SIZE // 8
        buf = [random.random()
               for _ in range(min(INTS, 1_000_000))]  # keep tractable
        count = 0
        start = time.perf_counter()
        rng = random.Random()
        blen = len(buf)
        while time.perf_counter() - start < self.duration:
            _ = buf[rng.randint(0, blen - 1)]
            count += 1
        elapsed = time.perf_counter() - start
        return count / elapsed if elapsed > 1e-6 else 0.0

    # ── Memory copy speed ─────────────────────────────────────────────────────

    def copy_speed(self):
        """GB/s of memoryview-based copy."""
        CHUNK = 256 * 1024 * 1024  # 256 MB
        src = bytearray(CHUNK)
        dst = bytearray(CHUNK)
        total = 0
        start = time.perf_counter()
        while time.perf_counter() - start < self.duration:
            mv_src = memoryview(src)
            mv_dst = memoryview(dst)
            mv_dst[:] = mv_src
            total += CHUNK
        elapsed = time.perf_counter() - start
        return (total / elapsed) / (1024 ** 3) if elapsed > 1e-6 else 0.0

    # ── Allocation stress ─────────────────────────────────────────────────────

    def alloc_stress(self):
        """Alloc+free cycles per second."""
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < self.duration:
            _ = bytearray(1024 * 1024)
            count += 1
        gc.collect()
        elapsed = time.perf_counter() - start
        return count / elapsed if elapsed > 1e-6 else 0.0

    def run_all(self, verbose=False):
        results = {}
        if verbose:
            print("  Running Sequential Bandwidth test...")
        results["seq_bw"] = self.seq_bandwidth()
        if verbose:
            print("  Running Random Access Speed test...")
        results["rand_lat"] = self.random_latency()
        if verbose:
            print("  Running Memory Copy test...")
        results["copy"] = self.copy_speed()
        if verbose:
            print("  Running Allocation Stress test...")
        results["alloc"] = self.alloc_stress()
        if verbose:
            print("  " + "="*50)
        return results

    @staticmethod
    def score(results):
        bw = results.get("seq_bw",   0) or 0
        copy = results.get("copy",     0) or 0
        lat = results.get("rand_lat", 0) or 0
        return int(bw * 0.4 + copy * 500 + lat / 5_000)
