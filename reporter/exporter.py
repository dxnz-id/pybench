import json
import os
import time
import platform
import cpuinfo
try:
    import pynvml
    HAS_NVML = True
except:
    HAS_NVML = False
try:
    import pyopencl as cl
    HAS_OPENCL = True
except:
    HAS_OPENCL = False
class Exporter:
    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    def get_hardware_info(self):
        info = {}
        try:
            c = cpuinfo.get_cpu_info()
            info['cpu'] = c.get('brand_raw', "Unknown CPU")
        except:
            info['cpu'] = platform.processor()
            
        mem = platform.uname()
        info['ram'] = f"{round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.**3) if hasattr(os, 'sysconf') else 0, 2)} GB"
        # Windows fallback for RAM if sysconf fails
        if info['ram'] == "0.0 GB":
            import psutil
            info['ram'] = f"{round(psutil.virtual_memory().total / (1024.**3), 2)} GB"
        info['os'] = f"{platform.system()} {platform.release()}"
        
        # GPU info
        info['gpu'] = "No GPU found"
        
        # 1. Try NVIDIA NVML
        if HAS_NVML:
            try:
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info['gpu'] = pynvml.nvmlDeviceGetName(handle)
                if isinstance(info['gpu'], bytes):
                    info['gpu'] = info['gpu'].decode('utf-8')
            except:
                pass
        
        # 2. Try OpenCL (for Intel, AMD, Apple, etc.)
        if info['gpu'] == "No GPU found" and HAS_OPENCL:
            try:
                platforms = cl.get_platforms()
                gpu_names = []
                for p in platforms:
                    devs = p.get_devices(device_type=cl.device_type.GPU)
                    for d in devs:
                        gpu_names.append(d.name.strip())
                if gpu_names:
                    info['gpu'] = " / ".join(list(set(gpu_names)))
            except:
                pass
        
        return info
    def export(self, results, system_monitor_data, scores):
        run_id = time.strftime("%Y%m%d_%H%M%S")
        filename = f"run_{run_id}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        report = {
            "run_id": run_id,
            "timestamp": time.ctime(),
            "hardware": self.get_hardware_info(),
            "system_monitor": system_monitor_data,
            "benchmark_results": results,
            "scores": scores
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
            
        return filepath
