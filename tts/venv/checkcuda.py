import torch
print("CUDA:", torch.cuda.is_available())
print("MPS:", torch.backends.mps.is_available())