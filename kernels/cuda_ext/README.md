# CUDA/C++ extension milestone (optional but recommended)

Implement a tiny CUDA op + PyBind wrapper, e.g.:
- top-k sampling / logits warp (temperature + topk + sample)
- or a fused bias+gelu

Add:
- kernels/cuda_ext/topk_sample.cu
- kernels/cuda_ext/binding.cpp
- kernels/cuda_ext/setup.py

Build in Colab GPU, then import from Python and benchmark.

