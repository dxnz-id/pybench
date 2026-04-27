import statistics
def aggregate_metrics(metrics_list):
    if not metrics_list:
        return {}
    def get_stats(data):
        if not data: return {"avg": 0, "min": 0, "max": 0, "std_dev": 0}
        return {
            "avg": round(statistics.mean(data), 2),
            "min": round(min(data), 2),
            "max": round(max(data), 2),
            "std_dev": round(statistics.stdev(data), 2) if len(data) > 1 else 0
        }
    # Extract time series
    cpu_usage = [m['cpu']['usage'] for m in metrics_list]
    cpu_freq = [m['cpu']['frequency'] for m in metrics_list]
    cpu_temp = [m['cpu']['temp'] for m in metrics_list if m['cpu']['temp'] > 0]
    
    mem_usage = [m['memory']['usage'] for m in metrics_list]
    
    # GPU Aggregation
    gpu_usage = []
    gpu_temp = []
    gpu_vram = []
    if metrics_list[0]['gpu']:
        num_gpus = len(metrics_list[0]['gpu'])
        for i in range(num_gpus):
            gpu_usage.extend([m['gpu'][i]['usage'] for m in metrics_list])
            gpu_temp.extend([m['gpu'][i]['temp'] for m in metrics_list])
            gpu_vram.extend([m['gpu'][i]['vram_used'] for m in metrics_list])
    disk_read = [m['disk']['read_speed'] for m in metrics_list]
    disk_write = [m['disk']['write_speed'] for m in metrics_list]
    
    net_down = [m['network']['download'] for m in metrics_list]
    net_up = [m['network']['upload'] for m in metrics_list]
    return {
        "cpu": get_stats(cpu_usage),
        "cpu_freq": get_stats(cpu_freq),
        "cpu_temp": get_stats(cpu_temp),
        "ram": get_stats(mem_usage),
        "gpu": get_stats(gpu_usage),
        "gpu_temp": get_stats(gpu_temp),
        "gpu_vram": get_stats(gpu_vram),
        "disk_read": get_stats(disk_read),
        "disk_write": get_stats(disk_write),
        "network_download": get_stats(net_down),
        "network_upload": get_stats(net_up)
    }
