import os
import time
import random
from concurrent.futures import ThreadPoolExecutor

class DiskBenchmark:
    def __init__(self, target_dir=".", duration=10):
        self.test_file = os.path.join(target_dir, "CDM_test.tmp")
        self.duration = duration
        self.file_size = 512 * 1024 * 1024 # 512MB test file size

    def _prepare_test_file(self):
        # Create a large test file to bypass small cache buffers
        if not os.path.exists(self.test_file) or os.path.getsize(self.test_file) < self.file_size:
            data = os.urandom(1024 * 1024)
            with open(self.test_file, "wb") as f:
                for _ in range(self.file_size // (1024 * 1024)):
                    f.write(data)
            # Force OS to commit the file to disk
            f_temp = open(self.test_file, "ab")
            os.fsync(f_temp.fileno())
            f_temp.close()

    def _threaded_io(self, func, threads):
        # CDM uses threads and outstanding I/O to hit peak speeds
        start = time.time()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(func) for _ in range(threads)]
            results = [f.result() for f in futures]
        # Sum of MB/s or Ops/s from all threads
        return sum(results) / (time.time() - start)

    def seq_1m_q8t1(self, mode="write"):
        block_size = 1024 * 1024
        data = os.urandom(block_size)
        
        def write_task():
            count = 0
            start = time.time()
            with open(self.test_file, "r+b") as f:
                while time.time() - start < self.duration:
                    offset = (count * block_size) % (self.file_size - block_size)
                    f.seek(offset)
                    f.write(data)
                    count += 1
                f.flush()
                # Use fsync for true sequential write measurement
                os.fsync(f.fileno())
            return count * (block_size / 1024 / 1024)

        def read_task():
            count = 0
            start = time.time()
            with open(self.test_file, "rb") as f:
                while time.time() - start < self.duration:
                    offset = (count * block_size) % (self.file_size - block_size)
                    f.seek(offset)
                    f.read(block_size)
                    count += 1
            return count * (block_size / 1024 / 1024)

        return self._threaded_io(write_task if mode == "write" else read_task, threads=8)

    def rnd_4k_q32t1(self, mode="write"):
        block_size = 4096
        data = os.urandom(block_size)
        
        def write_task():
            count = 0
            start = time.time()
            with open(self.test_file, "r+b") as f:
                while time.time() - start < self.duration:
                    pos = (random.randint(0, self.file_size // block_size - 1)) * block_size
                    f.seek(pos)
                    f.write(data)
                    count += 1
                f.flush()
            return count

        def read_task():
            count = 0
            start = time.time()
            with open(self.test_file, "rb") as f:
                while time.time() - start < self.duration:
                    pos = (random.randint(0, self.file_size // block_size - 1)) * block_size
                    f.seek(pos)
                    f.read(block_size)
                    count += 1
            return count

        return self._threaded_io(write_task if mode == "write" else read_task, threads=32)

    def cleanup(self):
        if os.path.exists(self.test_file):
            try: os.remove(self.test_file)
            except: pass

    def run_all(self):
        results = {}
        try:
            print(f"  Preparing {self.file_size // 1024 // 1024}MB Test File...")
            self._prepare_test_file()
            
            print("  Running SEQ1M Q8T1 Write...")
            results['seq_write'] = self.seq_1m_q8t1(mode="write")
            
            print("  Running SEQ1M Q8T1 Read...")
            results['seq_read'] = self.seq_1m_q8t1(mode="read")
            
            print("  Running RND4K Q32T1 Write...")
            results['rand_write'] = self.rnd_4k_q32t1(mode="write")
            
            print("  Running RND4K Q32T1 Read...")
            results['rand_read'] = self.rnd_4k_q32t1(mode="read")
            
            # Simple combined metric
            results['iops'] = results['rand_read'] + results['rand_write']
        finally:
            self.cleanup()
        return results