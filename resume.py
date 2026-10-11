import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.8-flash"

with open("cours.txt", "r", encoding="utf-8") as f:
    texte = f.read()

prompt = "Fais un résumé clair de ce cours en français, en 15 lignes maximum :\n\n" + texte

for essai in range(5):
    try:
        reponse = client.models.generate_content(model=MODEL, contents=prompt)
        print(reponse.text)
        break
    except Exception:
        print(f"Essai {essai + 1} échoué, nouvelle tentative dans 10 secondes...")
        time.sleep(10)