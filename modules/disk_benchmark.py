import os
import time
import random
from concurrent.futures import ThreadPoolExecutor


class DiskBenchmark:
    def __init__(self, target_dir=".", duration=10):
        self.test_file = os.path.join(target_dir, "CDM_test.tmp")
        self.duration = duration
        self.file_size = 1 * 1024 * 1024 * 1024  # 1 GB

    # ── File preparation ──────────────────────────────────────────────────────

    def _prepare_test_file(self):
        if not os.path.exists(self.test_file) or \
                os.path.getsize(self.test_file) < self.file_size:
            chunk = os.urandom(1024 * 1024)
            with open(self.test_file, "wb") as f:
                for _ in range(self.file_size // (1024 * 1024)):
                    f.write(chunk)
                os.fsync(f.fileno())

    # ── Thread runner ─────────────────────────────────────────────────────────

    def _threaded_io(self, func, threads):
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(func) for _ in range(threads)]
            total = sum(f.result() for f in futures)
        return total

    # ── SEQ 1M Q8T1 ───────────────────────────────────────────────────────────

    def seq_1m_q8t1(self, mode="write"):
        block_size = 1024 * 1024
        data = os.urandom(block_size)

        def write_task():
            total_mb = 0
            start = time.perf_counter()
            with open(self.test_file, "r+b") as f:
                idx = 0
                while time.perf_counter() - start < self.duration:
                    offset = (idx * block_size) % (self.file_size - block_size)
                    f.seek(offset)
                    f.write(data)
                    idx += 1
                    total_mb += 1
                f.flush()
                os.fsync(f.fileno())
            elapsed = time.perf_counter() - start
            return total_mb / elapsed if elapsed > 1e-6 else 0.0

        def read_task():
            total_mb = 0
            start = time.perf_counter()
            with open(self.test_file, "rb") as f:
                idx = 0
                while time.perf_counter() - start < self.duration:
                    offset = (idx * block_size) % (self.file_size - block_size)
                    f.seek(offset)
                    f.read(block_size)
                    idx += 1
                    total_mb += 1
            elapsed = time.perf_counter() - start
            return total_mb / elapsed if elapsed > 1e-6 else 0.0

        task = write_task if mode == "write" else read_task
        raw = self._threaded_io(task, threads=8)   # MB/s per thread summed
        return raw

    # ── RND 4K Q32T1 ──────────────────────────────────────────────────────────

    def rnd_4k_q32t1(self, mode="write"):
        block_size = 4096
        data = os.urandom(block_size)

        def write_task():
            count = 0
            start = time.perf_counter()
            with open(self.test_file, "r+b") as f:
                while time.perf_counter() - start < self.duration:
                    pos = random.randint(
                        0, self.file_size // block_size - 1) * block_size
                    f.seek(pos)
                    f.write(data)
                    count += 1
                f.flush()
                os.fsync(f.fileno())
            elapsed = time.perf_counter() - start
            return count / elapsed if elapsed > 1e-6 else 0.0

        def read_task():
            count = 0
            start = time.perf_counter()
            with open(self.test_file, "rb") as f:
                while time.perf_counter() - start < self.duration:
                    pos = random.randint(
                        0, self.file_size // block_size - 1) * block_size
                    f.seek(pos)
                    f.read(block_size)
                    count += 1
            elapsed = time.perf_counter() - start
            return count / elapsed if elapsed > 1e-6 else 0.0

        task = write_task if mode == "write" else read_task
        return self._threaded_io(task, threads=32)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def cleanup(self):
        if os.path.exists(self.test_file):
            try:
                os.remove(self.test_file)
            except Exception:
                pass

    def run_all(self, verbose=False):
        results = {}
        try:
            if verbose:
                print(
                    f"  Preparing {self.file_size // 1024 // 1024}MB Test File...")
            self._prepare_test_file()

            if verbose:
                print("  Running SEQ1M Q8T1 Write...")
            results["seq_write"] = self.seq_1m_q8t1(mode="write")

            if verbose:
                print("  Running SEQ1M Q8T1 Read...")
            results["seq_read"] = self.seq_1m_q8t1(mode="read")

            if verbose:
                print("  Running RND4K Q32T1 Write...")
            results["rand_write"] = self.rnd_4k_q32t1(mode="write")

            if verbose:
                print("  Running RND4K Q32T1 Read...")
            results["rand_read"] = self.rnd_4k_q32t1(mode="read")

            results["iops"] = results["rand_read"] + results["rand_write"]
        finally:
            self.cleanup()
        if verbose:
            print("  " + "="*50)
        return results

    @staticmethod
    def score(results):
        seq = (results.get("seq_read",  0) or 0) + \
            (results.get("seq_write", 0) or 0)
        rnd = (results.get("rand_read", 0) or 0) + \
            (results.get("rand_write", 0) or 0)
        return int(seq * 0.05 + rnd * 1.2)
