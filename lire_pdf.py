from pypdf import PdfReader

reader = PdfReader("cours.pdf")

texte = ""
for page in reader.pages:
    texte += page.extract_text() + "\n"

with open("cours.txt", "w", encoding="utf-8") as f:
    f.write(texte)

print("Pages lues :", len(reader.pages))
print("Caractères extraits :", len(texte))