# Triton kernel milestone (optional but recommended)

Implement a small transformer-relevant kernel (e.g., RMSNorm) and benchmark:
- torch baseline vs triton kernel
- measure speedup, and explain if memory-bound/launch overhead dominates on T4

Add:
- kernels/triton/rmsnorm.py
- kernels/triton/bench_rmsnorm.py

