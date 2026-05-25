import argparse
from PIL import Image
from utils import pick_device, load_image
from nst import run_style_transfer

import certifi
print(certifi.where())
import os

# Option 1: hard-code your cert bundle path
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = os.environ["SSL_CERT_FILE"]

def main():
    """
    --content (path, required)
    The photo you want to keep the structure of (shapes/objects). Example: a selfie or a landscape.

    --style (path, required)
    The art image whose colors/textures/brushstrokes you want to transfer. Example: a painting or abstract pattern.

    --out (path, default: stylized.jpg)
    Where to save the result. Change if you want a different filename or folder.

    --size (int, default: 384)
    Resizes both images so the shorter side is at most this many pixels (keeps aspect ratio).
    Smaller = faster but less detail. Bigger = slower but more detail.
    CPU tip: 256–384. GPU/MPS: 384–512+.

    --steps (int, default: 150)
    How many optimization iterations to run. More steps generally = cleaner, richer style, but slower.
    CPU tip: 100–200. Diminishing returns after ~300 for most images.

    --style_weight (float, default: 1e6)
    How strongly to match the style (higher → more stylized, sometimes warps content).
    Try 1e5 (subtle), 1e6 (balanced), 5e6+ (very strong style).

    --content_weight (float, default: 1.0)
    How much to preserve original structure (higher → more faithful to content, less stylization).
    Try 1.0–5.0. If faces/objects get too distorted, bump this up.

    --tv_weight (float, default: 1e-4)
    Total Variation (TV) smoothness: reduces noisy pixels / speckle.
    0 = no smoothing (can look noisy). 1e-4 = gentle. 1e-3 = smoother but may blur fine detail.

    Quick “when to change what”

    Too slow? ↓ --size, ↓ --steps.

    Not stylized enough? ↑ --style_weight (or ↓ --content_weight a bit).

    Content too distorted? ↑ --content_weight, ↓ --style_weight.

    Looks speckly/noisy? ↑ --tv_weight slightly.

    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True, help="Path to content image")
    ap.add_argument("--style", required=True, help="Path to style image")
    ap.add_argument("--out", default="stylized.jpg", help="Output path")
    ap.add_argument("--size", type=int, default=384, help="Max shorter side")
    ap.add_argument("--steps", type=int, default=150)
    ap.add_argument("--style_weight", type=float, default=1e6)
    ap.add_argument("--content_weight", type=float, default=1.0)
    ap.add_argument("--tv_weight", type=float, default=1e-4)
    args = ap.parse_args()

    device = pick_device()
    content = load_image(args.content, max_size=args.size)
    style = load_image(args.style, max_size=args.size)

    out = run_style_transfer(
        content, style,
        num_steps=args.steps,
        style_weight=args.style_weight,
        content_weight=args.content_weight,
        tv_weight=args.tv_weight,
        device=device,
    )
    out.save(args.out, quality=95)
    print(f"Saved: {args.out}")

if __name__ == "__main__":
    main()
