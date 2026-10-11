import os
import io
import time
import hashlib
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from google import genai
from pypdf import PdfReader

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Ordre d'essai : si un modèle échoue (quota ou surcharge), on passe au suivant
MODELES = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
]

# Change ce numéro quand tu modifies les consignes, pour régénérer les résultats
VERSION = "v2"

BASE = (
    "Tu es un professeur expert qui prépare des supports de révision pour un étudiant. "
    "Base-toi uniquement sur le cours fourni et n'invente aucune information absente du cours. "
    "Réponds en français. N'utilise ni titres Markdown avec #, ni tableaux : "
    "utilise des **mots en gras** et des puces commençant par un tiret. "
)

TACHES = {
    "resume": (
        "Fais un résumé structuré : une phrase d'introduction sur le sujet, puis 5 à 8 idées clés "
        "(une puce chacune, avec le terme principal en gras), puis une dernière ligne "
        "'**À retenir absolument :**' avec l'idée la plus importante. Maximum 20 lignes."
    ),
    "fiches": (
        "Crée une fiche de révision par notion importante du cours. Pour chaque fiche, écris : "
        "**Titre**, **Définition** (1 à 2 phrases), **Points à retenir** (3 puces maximum), "
        "**Exemple concret**, **Piège à éviter**. "
        "Sépare les fiches par une ligne contenant uniquement ———."
    ),
    "qcm": (
        "Crée un QCM de 10 questions de difficulté progressive : 4 faciles, 4 moyennes, "
        "2 difficiles qui demandent de comprendre et non de réciter. "
        "Chaque question a 4 choix (A, B, C, D) avec une seule bonne réponse et des mauvaises réponses plausibles. "
        "N'utilise jamais 'toutes les réponses ci-dessus'. Répartis les bonnes réponses entre A, B, C et D. "
        "Après les questions, écris **Corrigé** avec, pour chaque question, la lettre correcte "
        "et une justification d'une phrase."
    ),
    "flashcards": (
        "Crée 15 flashcards couvrant tout le cours, une seule idée par carte, au format exact :\n"
        "Q : question\nR : réponse courte (1 à 2 phrases)\n"
        "Alterne définitions, questions 'pourquoi', comparaisons et exemples. "
        "Laisse une ligne vide entre les cartes."
    ),
    "examen": (
        "Crée 8 questions d'examen ouvertes dans cet ordre : 3 questions de cours, "
        "3 questions d'application ou d'étude de cas, 2 questions de réflexion ou de comparaison. "
        "Indique le barème de chaque question (total sur 20) et donne pour chacune un corrigé détaillé "
        "avec les mots-clés attendus par un correcteur."
    ),
    "plan": (
        "Crée un plan de révision sur 7 jours. Pour chaque jour, indique : les notions à revoir, "
        "la méthode (relecture, flashcards, QCM, auto-test) et une durée conseillée entre 1h et 2h. "
        "Le jour 7 est une révision générale avec un examen blanc. "
        "Termine par 3 conseils pour mieux mémoriser."
    ),
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

os.makedirs("cache", exist_ok=True)


def generer(consigne, texte):
    prompt = BASE + consigne + "\n\nCours :\n" + texte
    for tour in range(2):
        for modele in MODELES:
            try:
                reponse = client.models.generate_content(model=modele, contents=prompt)
                if reponse.text:
                    print(f"Modèle utilisé : {modele}")
                    return reponse.text
            except Exception as e:
                print(f"{modele} : {str(e)[:100]}")
        time.sleep(10)
    return None


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/generer/<nom>", methods=["POST"])
def generer_route(nom):
    if nom not in TACHES:
        return jsonify(erreur="Type inconnu"), 404

    fichier = request.files.get("pdf")
    if not fichier:
        return jsonify(erreur="Aucun fichier reçu"), 400

    contenu = fichier.read()
    empreinte = hashlib.sha256(contenu).hexdigest()[:16]
    chemin = f"cache/{empreinte}_{VERSION}_{nom}.txt"

    if os.path.exists(chemin):
        print(f"Cache utilisé : {nom}")
        with open(chemin, "r", encoding="utf-8") as f:
            return jsonify(resultat=f.read())

    reader = PdfReader(io.BytesIO(contenu))
    texte = ""
    for page in reader.pages:
        texte += (page.extract_text() or "") + "\n"

    if not texte.strip():
        return jsonify(erreur="Aucun texte lisible dans ce PDF (PDF scanné ?)"), 400

    print(f"Appel à l'IA : {nom}")
    resultat = generer(TACHES[nom], texte)
    if not resultat:
        return jsonify(erreur="Tous les modèles sont indisponibles ou le quota est atteint, réessaie dans quelques minutes."), 503

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(resultat)

    return jsonify(resultat=resultat)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)