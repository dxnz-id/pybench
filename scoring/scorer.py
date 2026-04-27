class Scorer:
    # Basic normalization constants based on a "decent" mid-range system
    # These can be adjusted to match real-world "1000 point" baselines
    BASELINES = {
        "cpu_single": 1000.0, 
        "cpu_multi": 5000.0,
        "mem_bandwidth": 5000.0, # MB/s
        "disk_seq": 500.0,      # MB/s
        "gpu_compute": 100.0    # GFLOPS or MOps
    }
    def __init__(self, weights=None):
        self.weights = weights or {
            "cpu": 0.35,
            "memory": 0.25,
            "disk": 0.20,
            "gpu": 0.20
        }
    def calculate_cpu_score(self, results):
        # Weighted sub-score for CPU
        # single_thread, multi_thread, compression, encryption, prime_sieve
        s = (results.get('single_thread', 0) / 10) * 0.4 + \
            (results.get('multi_thread', 0) / 50) * 0.4 + \
            (results.get('compression', 0) * 100) * 0.1 + \
            (results.get('encryption', 0) * 100) * 0.1
        return int(s)
    def calculate_memory_score(self, results):
        # bandwidth, latency, copy, stress
        s = (results.get('bandwidth', 0) / 10) * 0.5 + \
            (results.get('latency', 0) / 1000) * 0.3 + \
            (results.get('copy', 0) / 10) * 0.2
        return int(s)
    def calculate_disk_score(self, results):
        # seq_read, seq_write, rand_read, rand_write, iops
        s = (results.get('seq_read', 0) + results.get('seq_write', 0)) * 0.4 + \
            (results.get('iops', 0) * 2) * 0.6
        return int(s)
    def calculate_gpu_score(self, results):
        # compute, vram_bandwidth, stress
        s = (results.get('compute', 0) * 10) * 0.7 + \
            (results.get('vram_bandwidth', 0) / 2) * 0.3
        return int(s)
    def calculate_overall(self, sub_scores):
        overall = sum(sub_scores[k] * self.weights.get(k, 0) for k in sub_scores)
        return int(overall)
    def get_full_breakdown(self, modules_results):
        cpu = self.calculate_cpu_score(modules_results.get('cpu', {}))
        mem = self.calculate_memory_score(modules_results.get('memory', {}))
        disk = self.calculate_disk_score(modules_results.get('disk', {}))
        gpu = self.calculate_gpu_score(modules_results.get('gpu', {}))
        
        sub_scores = {
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "gpu": gpu
        }
        
        overall = self.calculate_overall(sub_scores)
        sub_scores['overall'] = overall
        
        return sub_scores
