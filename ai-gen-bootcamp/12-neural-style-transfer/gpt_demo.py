# hardcoded_style_transfer_gpt_image.py
# -------------------------------------------------------
# 1) Put your absolute paths below (Mac examples shown)
# 2) export OPENAI_API_KEY="sk-..."  (set your key)
# 3) pip install openai pillow
# 4) python hardcoded_style_transfer_gpt_image.py
# -------------------------------------------------------
import os

from openai import OpenAI
from io import BytesIO
from PIL import Image
import base64

from dotenv import load_dotenv
load_dotenv()

# <<< EDIT THESE PATHS >>>
CONTENT_PATH = "content-images/content.jpg"   # e.g., your photo
STYLE_PATH   = "style-images/style.jpg"     # e.g., a painting
OUT_PATH     = "stylized.jpg"   # where to save result

# Output controls
SIZE = "1024x1024"   # 1024x1024, 1536x1024, 1024x1536, or "auto"
QUALITY = "auto"     # "low" | "medium" | "high" | "auto"
PROMPT = (
    "Apply the colors, textures, and brushstrokes of the second image to the first "
    "while preserving the original layout and subject. High fidelity to content; "
    "do not change positions or geometry."
)

def save_b64_image(b64, out_path):
    data = base64.b64decode(b64)
    img = Image.open(BytesIO(data))
    img.save(out_path)
    return out_path

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Read both local images (content + style)
    with open(CONTENT_PATH, "rb") as f_content, open(STYLE_PATH, "rb") as f_style:
        # Some SDK versions expose images.edits(...). If yours exposes images.edit(...),
        # the try/except below will fall back automatically.
        try:
            result = client.images.edits(
                model="gpt-image-1",
                image=[f_content, f_style],   # content first, style second
                prompt=PROMPT,
                size=SIZE,
                quality=QUALITY,
            )
        except AttributeError:
            # Fallback for older/newer method name
            result = client.images.edit(
                model="gpt-image-1",
                image=[f_content, f_style],
                prompt=PROMPT,
                size=SIZE,
                quality=QUALITY,
            )

    b64 = result.data[0].b64_json
    out_file = save_b64_image(b64, OUT_PATH)
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    main()
