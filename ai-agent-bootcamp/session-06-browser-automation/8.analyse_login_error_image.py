"""
Analyse Login Error Image — GPT-4o Vision Demo

NOTE: This script requires a `login_error.png` screenshot.
To generate it, first run `7.login_demo_error.py` which saves the screenshot.
Then run this script to analyse the error via GPT-4o vision.

Status: Placeholder — see README for setup instructions.
"""
import os
from dotenv import load_dotenv
load_dotenv()

def analyse_screenshot(image_path: str) -> str:
    """Analyse a login error screenshot using GPT-4o vision."""
    from openai import OpenAI
    import base64

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Screenshot not found: {image_path}\n"
            "Run 7.login_demo_error.py first to generate the screenshot."
        )

    client = OpenAI(api_key=api_key)
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this login error screenshot. What went wrong?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
            ]
        }]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    result = analyse_screenshot("login_error.png")
    print(result)
