import numpy as np
import cv2
import cv_bridge
import torch
import ultralytics

for lib in (np, cv2, cv_bridge, torch, ultralytics):
    version = getattr(lib, "__version__", "unknown")
    print(f"{lib.__name__}: {version} ({lib.__file__})")

print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if torch.cuda.is_available():
    props = torch.cuda.get_device_properties(0)
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Total memory: {props.total_memory / 1024**3:.2f} GiB")
else:
    print("GPU: none")
