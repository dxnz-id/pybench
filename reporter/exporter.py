import json
import os
import time
import platform
import cpuinfo
try:
    import pynvml
    HAS_NVML = True
except Exception:
    HAS_NVML = False
try:
    import pyopencl as cl
    HAS_OPENCL = True
except Exception:
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
        except Exception:
            info['cpu'] = platform.processor()

        import psutil
        info['cpu_cores'] = psutil.cpu_count(logical=False)
        info['cpu_threads'] = psutil.cpu_count(logical=True)
        try:
            freq = psutil.cpu_freq()
            info['cpu_base_clock'] = f"{freq.max:.2f} MHz" if freq and freq.max > 0 else f"{freq.current:.2f} MHz" if freq else "Unknown"
        except Exception:
            pass

        info['ram'] = f"{round(psutil.virtual_memory().total / (1024.**3), 2)} GB"
        info['os'] = f"{platform.system()} {platform.release()}"
        info['python_version'] = platform.python_version()

        try:
            disk = psutil.disk_usage(os.path.abspath(os.sep))
            info['disk_total'] = f"{round(disk.total / (1024.**3), 2)} GB"
        except Exception:
            pass

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
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                info['gpu_vram'] = f"{round(mem_info.total / (1024.**2), 2)} MB"
            except Exception:
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
            except Exception:
                pass

        # 3. Windows WMI Generic fallback
        if info['gpu'] == "No GPU found" and platform.system() == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                gpus = w.Win32_VideoController()
                if gpus:
                    info['gpu'] = " / ".join(list(set(g.Name for g in gpus)))
            except Exception:
                pass

        # 4. Linux lspci fallback (for Intel/AMD iGPUs)
        if info['gpu'] == "No GPU found" and platform.system() == "Linux":
            try:
                import subprocess
                out = subprocess.check_output(
                    "lspci | grep -i 'vga\\|3d\\|display'", shell=True, text=True)
                gpus = []
                for line in out.strip().split('\n'):
                    # Output looks like: "00:02.0 VGA compatible controller: Intel Corporation Alder Lake-P Integrated Graphics Controller (rev 0c)"
                    if ":" in line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            name = parts[2].strip()
                            # remove generic prefixes like 'Intel Corporation' if you want, but raw is fine.
                            gpus.append(name)
                if gpus:
                    info['gpu'] = " / ".join(gpus)
            except Exception:
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
