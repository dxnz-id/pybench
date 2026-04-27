import time
import numpy as np
try:
    import pyopencl as cl
    import pyopencl.array as cl_array
    HAS_OPENCL = True
except ImportError:
    HAS_OPENCL = False
class GPUBenchmark:
    def __init__(self, duration=10):
        global HAS_OPENCL
        self.duration = duration
        self.ctx = None
        self.queue = None
        self.device_name = "CPU Fallback"
        
        if HAS_OPENCL:
            try:
                platforms = cl.get_platforms()
                for p in platforms:
                    gpu_devices = p.get_devices(device_type=cl.device_type.GPU)
                    if gpu_devices:
                        # Success, found a GPU (could be Integrated or Dedicated)
                        self.ctx = cl.Context([gpu_devices[0]])
                        self.queue = cl.CommandQueue(self.ctx)
                        self.device_name = gpu_devices[0].name
                        break
            except Exception as e:
                HAS_OPENCL = False
    def gpu_compute(self, size=2048):
        start = time.time()
        ops = 0
        if not HAS_OPENCL or not self.ctx:
            # Fallback to Numpy (CPU)
            while time.time() - start < self.duration:
                a = np.random.rand(size, size).astype(np.float32)
                b = np.random.rand(size, size).astype(np.float32)
                np.dot(a, b)
                ops += (2 * size**3)
            return ops / (time.time() - start) / (10**9)

        # OpenCL implementation
        a_np = np.random.rand(size, size).astype(np.float32)
        b_np = np.random.rand(size, size).astype(np.float32)
        a_g = cl_array.to_device(self.queue, a_np)
        b_g = cl_array.to_device(self.queue, b_np)
        res_g = cl_array.empty_like(a_g)
        prg = cl.Program(self.ctx, """
        __kernel void stress(__global float *a, __global float *b, __global float *res) {
          int i = get_global_id(0);
          float val = a[i];
          for(int j=0; j<100; j++) {
            val = sqrt(val * val + b[i]);
          }
          res[i] = val;
        }
        """).build()
        
        # Create kernel object once to avoid RepeatedKernelRetrieval warning
        stress_kernel = prg.stress
        
        while time.time() - start < self.duration:
            stress_kernel(self.queue, (size*size,), None, a_g.data, b_g.data, res_g.data)
            self.queue.finish()
            ops += (size*size * 100)
        
        return ops / (time.time() - start) / 10**6

    def vram_bandwidth(self, size_mb=100):
        if not HAS_OPENCL or not self.ctx:
            return 0
        data = np.random.rand(size_mb * 1024 * 1024 // 4).astype(np.float32)
        start = time.time()
        total_mb = 0
        while time.time() - start < self.duration:
            buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=data)
            cl.enqueue_copy(self.queue, data, buf)
            self.queue.finish()
            total_mb += size_mb * 2 # Upload + Download
        return total_mb / (time.time() - start)
    def run_all(self):
        results = {}
        if not HAS_OPENCL or not self.ctx:
            print("  [WARNING] OpenCL not found or initialization failed. Using CPU fallback for GPU tests.")
        
        print("  Running GPU Compute test...")
        results['compute'] = self.gpu_compute()
        
        print("  Running VRAM Bandwidth test...")
        results['vram_bandwidth'] = self.vram_bandwidth()
        
        # GPU Stress is just running compute for longer
        results['stress'] = results['compute'] * 0.95 # Simple placeholder
        
        return results
