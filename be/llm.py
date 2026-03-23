from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask(user_input):
   try:
        response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=user_input
)
        print(response.text)
        return response.text
   except Exception as e:
        print(f"An error occurred: {e}")
        return None
    