import time
import numpy as np
class MemoryBenchmark:
    def __init__(self, duration=10):
        self.duration = duration
    def sequential_bandwidth(self, size_mb=100):
        size = size_mb * 1024 * 1024 // 8
        arr = np.random.rand(size)
        start = time.time()
        total_bytes = 0
        while time.time() - start < self.duration:
            _ = np.sum(arr)
            arr *= 1.0001
            total_bytes += size * 8 * 2
        return total_bytes / (time.time() - start) / (1024**2)

    def random_access_latency(self, size_mb=64):
        size = size_mb * 1024 * 1024 // 8
        indices = np.random.permutation(size)
        arr = np.random.rand(size)
        start = time.time()
        total_ops = 0
        while time.time() - start < self.duration:
            for i in range(100_000):
                _ = arr[indices[i % size]]
            total_ops += 100_000
        return total_ops / (time.time() - start)

    def memory_copy(self, size_mb=100):
        size = size_mb * 1024 * 1024 // 8
        arr1 = np.random.rand(size)
        start = time.time()
        total_bytes = 0
        while time.time() - start < self.duration:
            arr2 = np.copy(arr1)
            total_bytes += size * 8
        return total_bytes / (time.time() - start) / (1024**2)

    def allocation_stress(self):
        start = time.time()
        count = 0
        while time.time() - start < self.duration:
            objs = [np.zeros(1024 * 1024) for _ in range(20)]
            del objs
            count += 1
        return count
    def run_all(self):
        results = {}
        print("  Running Sequential Bandwidth test...")
        results['bandwidth'] = self.sequential_bandwidth()
        
        print("  Running Random Access Latency test...")
        results['latency'] = self.random_access_latency()
        
        print("  Running Memory Copy test...")
        results['copy'] = self.memory_copy()
        
        print("  Running Allocation Stress test...")
        results['stress'] = self.allocation_stress()
        
        return results