import io
from typing import Tuple
from PIL import Image
import torch
import torchvision.transforms as T

def pick_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

def load_image(img_path_or_bytes, max_size: int = 512) -> Image.Image:
    if isinstance(img_path_or_bytes, (bytes, bytearray, io.BytesIO)):
        img = Image.open(io.BytesIO(img_path_or_bytes)).convert("RGB")
    else:
        img = Image.open(img_path_or_bytes).convert("RGB")
    img.thumbnail((max_size, max_size))
    return img

def pil_to_tensor_norm(img: Image.Image, mean, std, device) -> torch.Tensor:
    transform = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=mean, std=std),
    ])
    return transform(img).unsqueeze(0).to(device)

def denorm_tensor_to_pil(t: torch.Tensor, mean, std) -> Image.Image:
    t = t.detach().cpu().clone().squeeze(0)
    for c in range(3):
        t[c] = t[c] * std[c] + mean[c]
    t = torch.clamp(t, 0, 1)
    to_pil = T.ToPILImage()
    return to_pil(t)

def image_to_bytes(img: Image.Image, fmt="JPEG", quality=95) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=quality)
    return buf.getvalue()
