import time
import threading
import os
import psutil
import GPUtil as gputil
try:
    import pynvml
    pynvml.nvmlInit()
    HAS_NVML = True
except Exception:
    HAS_NVML = False
class SystemMonitor(threading.Thread):
    def __init__(self, interval=1.0):
        super().__init__()
        self.interval = interval
        self._stop_event = threading.Event()
        self.metrics = []
        self.daemon = True
    def stop(self):
        self._stop_event.set()
    def run(self):
        # Initial net/io counters for delta calculation
        last_net = psutil.net_io_counters()
        last_disk = psutil.disk_io_counters()
        last_time = time.time()
        while not self._stop_event.is_set():
            current_time = time.time()
            dt = current_time - last_time
            if dt <= 0: dt = 0.1
            
            # CPU
            cpu_usage = psutil.cpu_percent(interval=None)
            cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
            cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
            
            # RAM
            mem = psutil.virtual_memory()
            
            # GPU (NVIDIA)
            gpu_data = []
            if HAS_NVML:
                try:
                    deviceCount = pynvml.nvmlDeviceGetCount()
                    for i in range(deviceCount):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                        try:
                            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                        except:
                            power = 0
                        gpu_data.append({
                            "usage": util.gpu,
                            "vram_used": mem_info.used / (1024**2),
                            "vram_total": mem_info.total / (1024**2),
                            "temp": temp,
                            "power": power,
                            "name": pynvml.nvmlDeviceGetName(handle)
                        })
                except:
                    pass
            
            # Windows Generic GPU Fallback (for Intel/AMD iGPU)
            if not gpu_data and os.name == 'nt':
                try:
                    import subprocess
                    # Query performance counters for all GPU engines and sum them up
                    cmd = 'powershell -Command "Get-Counter \'\\GPU Engine(*)\\Utilization Percentage\' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Measure-Object -Property CookedValue -Sum | Select-Object -ExpandProperty Sum"'
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
                    if output:
                        gpu_data.append({
                            "usage": min(100.0, float(output)), # Cap at 100
                            "vram_used": 0, # Difficult to get generic shared vram
                            "vram_total": 0,
                            "temp": 0,
                            "power": 0,
                            "name": "Generic GPU"
                        })
                except:
                    pass

            if not gpu_data and gputil:
                try:
                    gpus = gputil.getGPUs()
                    for g in gpus:
                        gpu_data.append({
                            "usage": g.load * 100,
                            "vram_used": g.memoryUsed,
                            "vram_total": g.memoryTotal,
                            "temp": g.temperature,
                            "power": 0,
                            "name": g.name
                        })
                except:
                    pass
            # Disk
            curr_disk = psutil.disk_io_counters()
            disk_read_speed = (curr_disk.read_bytes - last_disk.read_bytes) / dt
            disk_write_speed = (curr_disk.write_bytes - last_disk.write_bytes) / dt
            
            # Network
            curr_net = psutil.net_io_counters()
            net_download = (curr_net.bytes_recv - last_net.bytes_recv) / dt
            net_upload = (curr_net.bytes_sent - last_net.bytes_sent) / dt
            
            # Temperature (Fallback for CPU)
            cpu_temp = 0
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Linux/Mac standard
                    for name, entries in temps.items():
                        if entries:
                            cpu_temp = entries[0].current
                            break
                
                # Windows Fallback via WMI/PowerShell
                if cpu_temp == 0 and os.name == 'nt':
                    try:
                        import subprocess
                        # Querying WMI for ThermalZoneTemperature (Kelvin * 10)
                        cmd = 'powershell -ExecutionPolicy Bypass -Command "Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root/wmi | Select-Object -ExpandProperty CurrentTemperature"'
                        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
                        if output:
                            # Convert from decikelvin to Celsius
                            cpu_temp = (float(output) / 10.0) - 273.15
                    except:
                        pass
            except:
                pass
            snapshot = {
                "timestamp": current_time,
                "cpu": {
                    "usage": cpu_usage,
                    "frequency": cpu_freq,
                    "cores": cpu_cores,
                    "temp": cpu_temp
                },
                "memory": {
                    "used": mem.used / (1024**2),
                    "available": mem.available / (1024**2),
                    "usage": mem.percent
                },
                "gpu": gpu_data,
                "disk": {
                    "read_speed": disk_read_speed,
                    "write_speed": disk_write_speed
                },
                "network": {
                    "download": net_download,
                    "upload": net_upload
                }
            }
            
            self.metrics.append(snapshot)
            
            # Update last state
            last_net = curr_net
            last_disk = curr_disk
            last_time = current_time
            
            time.sleep(self.interval)
    def get_latest_snapshot(self):
        return self.metrics[-1] if self.metrics else None

    def get_metrics(self):
        return self.metrics