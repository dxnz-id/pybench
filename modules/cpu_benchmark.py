import time
import math
import zlib
import lzma
import hashlib
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True
def prime_sieve(limit=100000):
    count = 0
    for i in range(limit):
        if is_prime(i):
            count += 1
    return count
def aes_simulation(data_size_mb=10):
    # Use SHA512 repeatedly to simulate heavy crypto workload
    data = np.random.bytes(1024 * 1024) # 1MB
    start = time.time()
    for _ in range(data_size_mb):
        hashlib.sha256(data).hexdigest()
    return time.time() - start
def compression_test(data_size_mb=20):
    data = np.random.bytes(data_size_mb * 1024 * 1024)
    
    start_zlib = time.time()
    zlib.compress(data)
    zlib_time = time.time() - start_zlib
    
    start_lzma = time.time()
    # LZMA is very slow, use smaller sample if needed
    lzma.compress(data[:1024*1024*5]) # 5MB
    lzma_time = time.time() - start_lzma
    
    return zlib_time + lzma_time
def math_workload(iterations=10_000_000):
    # Mix of float and integer
    res = 0
    for i in range(iterations):
        res += math.sqrt(i) * (i % 100)
    return res

def run_single_thread_proc(dur):
    start = time.time()
    count = 0
    while time.time() - start < dur:
        math_workload(50_000)
        count += 1
    return count

class CPUBenchmark:
    def __init__(self, duration=10, threads=None):
        self.duration = duration
        self.threads = threads or 1

    def run_single_thread(self):
        return run_single_thread_proc(self.duration)

    def run_multi_thread(self):
        start = time.time()
        operations = 0
        cpu_count = self.threads
        # True multi-core stress using Multiple Processes
        with ProcessPoolExecutor(max_workers=cpu_count) as executor:
            futures = [executor.submit(run_single_thread_proc, self.duration) for _ in range(cpu_count)]
            for f in futures:
                operations += f.result()
        return operations

    def run_all(self):
        results = {}
        print("  Running Single-thread test...")
        results['single_thread'] = self.run_single_thread()
        
        print("  Running Multi-thread test (Stress Test)...")
        results['multi_thread'] = self.run_multi_thread()
        
        print("  Running Compression test...")
        # Normalize
        start = time.time()
        compression_test()
        results['compression'] = 1.0 / (time.time() - start + 0.001)

        print("  Running Encryption simulation...")
        start = time.time()
        aes_simulation()
        results['encryption'] = 1.0 / (time.time() - start + 0.001)

        print("  Running Prime Sieve test...")
        start = time.time()
        prime_sieve(50000)
        results['prime_sieve'] = 1.0 / (time.time() - start + 0.001)
        
        return results
