"""
Classic Neural Style Transfer (Gatys et al.) with VGG19.
"""
from typing import Callable, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import vgg19, VGG19_Weights
from utils import pil_to_tensor_norm, denorm_tensor_to_pil

# VGG19 layers we will tap into
# Using indices from torchvision.models.vgg19(...).features
LAYER_MAP = {
    "conv1_1": 0,
    "conv2_1": 5,
    "conv3_1": 10,
    "conv4_1": 19,
    "conv4_2": 21,  # commonly used for content
    "conv5_1": 28,
}

def gram_matrix(feat: torch.Tensor) -> torch.Tensor:
    # feat: (N, C, H, W)
    N, C, H, W = feat.size()
    Fm = feat.view(N, C, H * W)
    G = torch.bmm(Fm, Fm.transpose(1, 2))  # (N, C, C)
    return G / (C * H * W)

def get_vgg_features(device: torch.device):
    from torchvision.models import vgg19, VGG19_Weights
    from torchvision.transforms import Normalize

    weights = VGG19_Weights.DEFAULT
    vgg = vgg19(weights=weights).features.to(device).eval()
    for p in vgg.parameters():
        p.requires_grad_(False)

    # Safe defaults (ImageNet)
    mean = (0.485, 0.456, 0.406)
    std  = (0.229, 0.224, 0.225)

    # 1) Prefer modern API: pull Normalize from weights.transforms()
    try:
        tfm = weights.transforms()
        if hasattr(tfm, "transforms"):  # Compose-like
            for t in tfm.transforms:
                if isinstance(t, Normalize):
                    mean = tuple(t.mean)
                    std  = tuple(t.std)
                    break
    except Exception:
        pass

    # 2) Fallback to legacy weights.meta if present
    try:
        meta = getattr(weights, "meta", {}) or {}
        mean = tuple(meta.get("mean", mean))
        std  = tuple(meta.get("std", std))
    except Exception:
        pass

    return vgg, mean, std


def extract_features(x: torch.Tensor, vgg: nn.Sequential, layers: dict):
    feats = {}
    out = x
    for i, module in enumerate(vgg):
        out = module(out)
        if i in layers.values():
            name = [k for k, v in layers.items() if v == i][0]
            feats[name] = out
        if len(feats) == len(layers):
            break
    return feats

def total_variation_loss(img: torch.Tensor) -> torch.Tensor:
    # Encourage smoothness
    tv_h = torch.mean(torch.abs(img[:, :, 1:, :] - img[:, :, :-1, :]))
    tv_w = torch.mean(torch.abs(img[:, :, :, 1:] - img[:, :, :, :-1]))
    return tv_h + tv_w

@torch.no_grad()
def _to_pil(x: torch.Tensor, mean, std):
    return denorm_tensor_to_pil(x, mean, std)

def run_style_transfer(
    content_pil,
    style_pil,
    num_steps: int = 200,
    style_weight: float = 1e6,
    content_weight: float = 1e0,
    tv_weight: float = 1e-4,
    lr: float = 0.03,
    device: Optional[torch.device] = None,
    progress_callback: Optional[Callable[[int, "Image.Image"], None]] = None,
):
    """
    Returns: final stylized PIL image.
    """
    if device is None:
        device = torch.device("cpu")

    vgg, mean, std = get_vgg_features(device)

    # Prepare tensors
    content = pil_to_tensor_norm(content_pil, mean, std, device)
    style = pil_to_tensor_norm(style_pil, mean, std, device)

    # Get target features once
    feat_layers_style = {k: LAYER_MAP[k] for k in ["conv1_1", "conv2_1", "conv3_1", "conv4_1", "conv5_1"]}
    feat_layers_content = {"conv4_2": LAYER_MAP["conv4_2"]}

    content_feats = extract_features(content, vgg, feat_layers_content)
    style_feats = extract_features(style, vgg, feat_layers_style)
    style_grams = {k: gram_matrix(v) for k, v in style_feats.items()}

    # Initialize with content image
    x = content.clone().requires_grad_(True)
    opt = torch.optim.Adam([x], lr=lr)

    display_every = max(10, num_steps // 10)

    for step in range(1, num_steps + 1):
        opt.zero_grad()

        feats = extract_features(x, vgg, {**feat_layers_content, **feat_layers_style})
        # Content loss
        c_loss = F.mse_loss(feats["conv4_2"], content_feats["conv4_2"])

        # Style loss
        s_loss = 0.0
        for k in style_grams:
            Gx = gram_matrix(feats[k])
            s_loss = s_loss + F.mse_loss(Gx, style_grams[k])
        s_loss = s_loss * style_weight

        # TV loss
        tv = total_variation_loss(x) * tv_weight

        loss = content_weight * c_loss + s_loss + tv
        loss.backward()
        opt.step()

        if progress_callback and (step % display_every == 0 or step == num_steps):
            preview = _to_pil(x, mean, std)
            progress_callback(step, preview)

    final_img = _to_pil(x, mean, std)
    return final_img
