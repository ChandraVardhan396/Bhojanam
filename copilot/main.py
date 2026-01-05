import os
import easyocr
from PIL import Image
from openai import OpenAI

# =========================
# CONFIG
# =========================
os.environ["HF_TOKEN"] = "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"  # put your HF token here
IMAGE_PATH = "./dataset/food_label.jpg"  # path to your label image

# =========================
# STEP 1: OCR - Read text from image
# =========================
reader = easyocr.Reader(['en'], gpu=False)
ocr_result = reader.readtext(IMAGE_PATH, detail=0)

extracted_text = "\n".join(ocr_result)

print("---- OCR OUTPUT ----")
print(extracted_text)

# =========================
# STEP 2: Send text to HF Chat Model
# =========================
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

prompt = f"""
You are a food label expert.

Below is text extracted from a packaged food label.

TASK:
- Explain it in VERY SIMPLE language
- Avoid scientific terms
- Keep it short and clear
- Use bullet points
- Mention:
  • Is it healthy or not
  • High sugar / salt / fat (if any)
  • Allergens if present
  • Who should avoid it

Food label text:
{extracted_text}
"""

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Thinking",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.3,
)

print("\n---- EASY EXPLANATION ----")
print(completion.choices[0].message.content)
