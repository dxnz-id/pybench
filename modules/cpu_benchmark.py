import time
import math
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor


class CPUBenchmark:
    def __init__(self, duration=5, threads=None):
        self.duration = duration
        self.threads = threads or (os.cpu_count() or 4)

    def _run_timed(self, func):
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < self.duration:
            func()
            count += 1
        return count

    # ── Tests ─────────────────────────────────────────────────────────────────

    def single_thread(self):
        def workload():
            x = 0.0
            for i in range(1, 500):
                x += math.sqrt(i) * math.log(i + 1) * math.sin(i)
        return self._run_timed(workload)

    def multi_thread(self):
        cores = self.threads

        def workload():
            x = 0.0
            for i in range(1, 500):
                x += math.sqrt(i) * math.log(i + 1) * math.sin(i)
        total = 0
        with ThreadPoolExecutor(max_workers=cores) as ex:
            futures = [ex.submit(self._run_timed, workload)
                       for _ in range(cores)]
            total = sum(f.result() for f in futures)
        return total

    def compression(self):
        import zlib
        data = os.urandom(64 * 1024)
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < self.duration:
            zlib.compress(data, level=6)
            count += 1
        return count

    def encryption(self):
        data = os.urandom(64 * 1024)
        key = os.urandom(32)
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < self.duration:
            hashlib.pbkdf2_hmac("sha256", data, key, 1)
            count += 1
        return count

    def prime_sieve(self):
        def sieve(n):
            s = bytearray([1]) * (n + 1)
            s[0] = s[1] = 0
            for i in range(2, int(n ** 0.5) + 1):
                if s[i]:
                    s[i*i::i] = bytearray(len(s[i*i::i]))
        return self._run_timed(lambda: sieve(100_000))

    def run_all(self, verbose=False):
        results = {}
        if verbose:
            print("  Running Single-thread test...")
        results["single"] = self.single_thread()
        if verbose:
            print("  Running Multi-thread test (Stress Test)...")
        results["multi"] = self.multi_thread()
        if verbose:
            print("  Running Compression test...")
        results["compress"] = self.compression()
        if verbose:
            print("  Running Encryption simulation...")
        results["encrypt"] = self.encryption()
        if verbose:
            print("  Running Prime Sieve test...")
        results["prime"] = self.prime_sieve()
        if verbose:
            print("  " + "="*50)
        return results

    @staticmethod
    def score(results):
        return int(results.get("single", 0) + results.get("multi", 0) * 0.5)
