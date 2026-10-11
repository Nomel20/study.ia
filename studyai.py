import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELES = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.7-flash"]

with open("cours.txt", "r", encoding="utf-8") as f:
    texte = f.read()

TACHES = {
    "resume": "Fais un résumé clair du cours en 15 lignes maximum.",
    "fiches": "Crée des fiches de révision : une fiche par notion clé avec un titre, une définition et les points à retenir.",
    "qcm": "Crée un QCM de 10 questions avec 4 choix (A, B, C, D). Donne les réponses correctes à la fin avec une courte justification.",
    "flashcards": "Crée 15 flashcards au format :\nQ : question\nR : réponse",
    "examen": "Crée 8 questions d'examen ouvertes de difficulté variée, avec un corrigé court pour chacune.",
    "plan": "Crée un plan de révision sur 7 jours pour ce cours, avec les notions à revoir chaque jour et la durée conseillée.",
}

os.makedirs("resultats", exist_ok=True)


def generer(consigne):
    prompt = consigne + " Réponds en français.\n\nCours :\n" + texte
    for tour in range(3):
        for modele in MODELES:
            try:
                return client.models.generate_content(model=modele, contents=prompt).text
            except Exception as e:
                print(f"  {modele} : {str(e)[:120]}")
        attente = 20 * (tour + 1)
        print(f"  Pause de {attente} secondes...")
        time.sleep(attente)
    return None


for nom, consigne in TACHES.items():
    chemin = f"resultats/{nom}.md"
    if os.path.exists(chemin):
        print(f"{nom} : déjà généré, on passe.")
        continue
    print(f"Génération : {nom}...")
    resultat = generer(consigne)
    if resultat:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(resultat)
        print(f"  OK -> {chemin}")
        time.sleep(5)
    else:
        print(f"  Échec pour {nom}")