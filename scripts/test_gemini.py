import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


for model in client.models.list():
    print(f"Model Name: {model.name}")

"""
model = genai.GenerativeModel("gemini-3.5-flash-lite")

response = model.generate_content("Say hello in one sentence.")
print(response.text)
"""