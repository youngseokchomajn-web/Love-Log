import os
from google import genai
from dotenv import load_dotenv

env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
print("API Key exists:", bool(api_key))

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Respond with the word Hello.'
)
print("Response:", response.text.strip())
