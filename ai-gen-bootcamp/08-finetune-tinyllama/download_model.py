"""Run this once before training: python download_model.py"""
from huggingface_hub import snapshot_download
print("Downloading TinyLlama-1.1B-Chat-v1.0 (~2.2 GB)...")
snapshot_download("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
print("Done. Model cached in HuggingFace cache directory.")
