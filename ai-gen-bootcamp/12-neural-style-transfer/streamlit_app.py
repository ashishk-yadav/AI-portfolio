import streamlit as st
from PIL import Image
import torch
from utils import pick_device, load_image, image_to_bytes
from nst import run_style_transfer

import certifi
print(certifi.where())
import os

# Option 1: hard-code your cert bundle path
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = os.environ["SSL_CERT_FILE"]

st.set_page_config(page_title="Neural Style Transfer (Beginner Demo)", page_icon="🎨", layout="centered")

st.title("🎨 Neural Style Transfer — Beginner Demo")
st.write("""
Upload a **content image** (what to paint) and a **style image** (how to paint).
This app blends them using a pre-trained VGG19 feature extractor.
""")

with st.expander("What is this doing? "):
    st.markdown("""
- We use a pre-trained **VGG19** network as a feature extractor (no training from scratch!).  
- **Content loss** keeps the main structure of your content image (e.g., shapes).  
- **Style loss** uses **Gram matrices** to capture texture/colors from the style image.  
- We start from the content image and **optimize pixels** to minimize a weighted sum of these losses.
""")

tab_app, tab_howto = st.tabs(["App", "How it works"])

with tab_app:
    col1, col2 = st.columns(2)
    with col1:
        content_file = st.file_uploader("Upload Content Image", type=["jpg", "jpeg", "png"])
        if content_file is None:
            st.caption("Or use the built-in sample below.")
            sample_content = "samples/content.jpg"
    with col2:
        style_file = st.file_uploader("Upload Style Image", type=["jpg", "jpeg", "png"])
        if style_file is None:
            st.caption("Or use the built-in sample below.")
            sample_style = "samples/style.jpg"

    max_size = st.slider("Max image size (shorter side)", 128, 768, 384, step=64)
    steps = st.slider("Optimization steps (higher = better & slower)", 50, 400, 150, step=25)
    style_weight = st.select_slider("Style strength", options=[1e5, 5e5, 1e6, 5e6, 1e7], value=1e6)
    content_weight = st.select_slider("Content strength", options=[1.0, 2.0, 5.0], value=1.0)
    tv_weight = st.select_slider("Smoothness (TV) weight", options=[0.0, 1e-5, 1e-4, 1e-3], value=1e-4)

    device = pick_device()
    st.caption(f"Using device: **{device}**")

    # Load images with fallback to samples
    if content_file:
        content_img = load_image(content_file.read(), max_size=max_size)
    else:
        content_img = load_image(sample_content, max_size=max_size)

    if style_file:
        style_img = load_image(style_file.read(), max_size=max_size)
    else:
        style_img = load_image(sample_style, max_size=max_size)

    c1, c2 = st.columns(2)
    with c1:
        st.image(content_img, caption="Content", use_container_width=True)
    with c2:
        st.image(style_img, caption="Style", use_container_width=True)

    if st.button("🎬 Stylize!", type="primary"):
        prog = st.progress(0, text="Starting optimization...")
        preview_slot = st.empty()

        def cb(step, img):
            prog.progress(min(step/steps, 1.0), text=f"Optimizing... step {step}/{steps}")
            preview_slot.image(img, caption=f"Preview at step {step}", use_container_width=True)

        with st.spinner("Cooking pixels..."):
            out = run_style_transfer(
                content_img, style_img,
                num_steps=steps,
                style_weight=style_weight,
                content_weight=content_weight,
                tv_weight=tv_weight,
                device=device,
                progress_callback=cb
            )

        st.success("Done!")
        st.image(out, caption="Final Output", use_column_width=True)
        st.download_button(
            "⬇️ Download result",
            data=image_to_bytes(out, fmt="JPEG", quality=95),
            file_name="stylized.jpg",
            mime="image/jpeg",
        )

with tab_howto:
    st.markdown("""
### Under the hood (simple version)
1. Load a pre-trained **VGG19** network (used only for feature extraction).
2. Compute **content features** from layer `conv4_2` and **style features** from multiple layers.
3. Build losses:
   - Content Loss = MSE between features of output and content at `conv4_2`  
   - Style Loss = MSE between Gram matrices of output and style at several layers  
   - TV Loss = smoothness regularizer
4. Optimize the output image pixels with Adam for N steps.
5. Show intermediate previews to see progress.

> Tip: If you're on CPU, use smaller image sizes and fewer steps to keep it fast.
""")
