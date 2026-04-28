class Scorer:
    def __init__(self, weights=None):
        pass

    def calculate_cpu_score(self, results):
        return int(results.get("single", 0) + results.get("multi", 0) * 0.5)

    def calculate_memory_score(self, results):
        bw   = results.get("seq_bw",   0) or 0
        copy = results.get("copy",     0) or 0
        lat  = results.get("rand_lat", 0) or 0
        return int(bw * 0.4 + copy * 500 + lat / 5_000)

    def calculate_disk_score(self, results):
        seq  = (results.get("seq_read",  0) or 0) + (results.get("seq_write", 0) or 0)
        rnd  = (results.get("rand_read", 0) or 0) + (results.get("rand_write",0) or 0)
        return int(seq * 0.05 + rnd * 1.2)

    def calculate_gpu_score(self, results):
        compute = results.get("compute", 0) or 0
        vram    = results.get("vram_bw", 0) or 0
        return int(compute * 5 + vram * 0.1)

    def calculate_overall(self, sub_scores):
        count = sum(1 for k, v in sub_scores.items() if v > 0)
        if count == 0:
            return 0
        return int(sum(sub_scores.values()) / count)

    def get_full_breakdown(self, modules_results):
        cpu = self.calculate_cpu_score(modules_results.get('cpu', {})) if 'cpu' in modules_results else 0
        mem = self.calculate_memory_score(modules_results.get('memory', {})) if 'memory' in modules_results else 0
        disk = self.calculate_disk_score(modules_results.get('disk', {})) if 'disk' in modules_results else 0
        gpu = self.calculate_gpu_score(modules_results.get('gpu', {})) if 'gpu' in modules_results else 0
        
        sub_scores = {
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "gpu": gpu
        }
        
        overall = self.calculate_overall({k:v for k,v in sub_scores.items() if v > 0})
        sub_scores['overall'] = overall
        
        return sub_scores
