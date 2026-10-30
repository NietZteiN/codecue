"""NVML sampling tied to the CUDA device UUID, avoiding Slurm index remapping."""
import subprocess

from .throughput import Monitor


def gpu_selector(properties_uuid, slurm_gpu=None):
    value = str(properties_uuid)
    if value.startswith('GPU-') or value.startswith('MIG-'):
        return value
    if len(value) == 36 and value.count('-') == 4:
        return 'GPU-' + value
    return str(slurm_gpu).split(',')[0] if slurm_gpu else None


class UUIDMonitor(Monitor):
    def __init__(self):
        import os
        import torch
        super().__init__()
        self.device = gpu_selector(getattr(torch.cuda.get_device_properties(0), 'uuid', None),
                                   os.environ.get('SLURM_JOB_GPUS'))
        self.verified = False
        self.driver = None
        if self.device:
            try:
                result = subprocess.run(['nvidia-smi', '-i', self.device,
                                         '--query-gpu=uuid,driver_version', '--format=csv,noheader'],
                                        capture_output=True, text=True, timeout=3)
                fields = [v.strip() for v in result.stdout.strip().split(',')]
                if result.returncode == 0 and len(fields) == 2:
                    self.verified = self.device == fields[0] or self.device.isdigit()
                    self.device, self.driver = fields
            except (OSError, subprocess.TimeoutExpired):
                pass
        if not self.verified:
            self.device = None

    def summary(self):
        return {**super().summary(), 'gpu_uuid': self.device,
                'selector_verified': self.verified, 'driver_version': self.driver,
                'memory_scope': 'whole allocated GPU, including allocator reservations and KV cache'}
