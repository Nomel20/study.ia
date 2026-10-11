// Bulles flottantes
const emojis = ["📚", "✏️", "💡", "🧠", "⭐", "🎯", "📖"];
const conteneur = document.getElementById("bulles");

for (let i = 0; i < 18; i++) {
  const bulle = document.createElement("span");
  bulle.className = "bulle";
  bulle.textContent = emojis[Math.floor(Math.random() * emojis.length)];
  bulle.style.left = Math.random() * 100 + "%";
  bulle.style.fontSize = 20 + Math.random() * 30 + "px";
  bulle.style.animationDuration = 10 + Math.random() * 15 + "s";
  bulle.style.animationDelay = Math.random() * 10 + "s";
  conteneur.appendChild(bulle);
}

// Texte qui s'écrit tout seul
const mots = ["résumés", "fiches de révision", "QCM", "flashcards", "questions d'examen", "un plan de révision"];
const zoneMot = document.getElementById("mot");
let indexMot = 0;
let indexLettre = 0;
let enEffacement = false;

function ecrire() {
  const mot = mots[indexMot];
  if (!enEffacement) {
    indexLettre++;
    zoneMot.textContent = mot.slice(0, indexLettre);
    if (indexLettre === mot.length) {
      enEffacement = true;
      return setTimeout(ecrire, 1500);
    }
  } else {
    indexLettre--;
    zoneMot.textContent = mot.slice(0, indexLettre);
    if (indexLettre === 0) {
      enEffacement = false;
      indexMot = (indexMot + 1) % mots.length;
    }
  }
  setTimeout(ecrire, enEffacement ? 40 : 90);
}
ecrire();

// Apparition au défilement
const observateur = new IntersectionObserver((entrees) => {
  entrees.forEach((e) => {
    if (e.isIntersecting) e.target.classList.add("visible");
  });
}, { threshold: 0.15 });

document.querySelectorAll(".reveal").forEach((el) => observateur.observe(el));

// Zone de dépôt du PDF
const depot = document.getElementById("depot");
const champFichier = document.getElementById("fichier");
const texteDepot = document.getElementById("depot-texte");
const boutonGenerer = document.getElementById("btn-generer");
const blocResultat = document.getElementById("resultat");
const contenuResultat = document.getElementById("resultat-contenu");
const onglets = document.querySelectorAll(".onglet");

let fichierChoisi = null;
let typeActif = "resume";
const cache = {};

function choisirFichier(fichier) {
  if (!fichier || fichier.type !== "application/pdf") {
    texteDepot.textContent = "❌ Merci de choisir un fichier PDF";
    return;
  }
  fichierChoisi = fichier;
  for (const cle in cache) delete cache[cle];
  blocResultat.hidden = true;
  texteDepot.textContent = "✅ " + fichier.name;
  depot.classList.add("pret");
  boutonGenerer.disabled = false;
}

depot.addEventListener("click", () => champFichier.click());
champFichier.addEventListener("change", () => choisirFichier(champFichier.files[0]));

depot.addEventListener("dragover", (e) => {
  e.preventDefault();
  depot.classList.add("survol");
});
depot.addEventListener("dragleave", () => depot.classList.remove("survol"));
depot.addEventListener("drop", (e) => {
  e.preventDefault();
  depot.classList.remove("survol");
  choisirFichier(e.dataTransfer.files[0]);
});

// Affichage du résultat
function afficher(texte) {
  const propre = texte
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/^\s*[\*\-] /gm, "• ")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  contenuResultat.innerHTML = propre;
}

// Chargement d'un onglet (généré à la demande, puis gardé en mémoire)
async function charger(type) {
  typeActif = type;
  onglets.forEach((o) => o.classList.toggle("actif", o.dataset.type === type));
  blocResultat.hidden = false;

  if (cache[type]) {
    afficher(cache[type]);
    return;
  }

  contenuResultat.textContent = "⏳ L'IA prépare ça pour toi...";

  const donnees = new FormData();
  donnees.append("pdf", fichierChoisi);

  try {
    const reponse = await fetch("/generer/" + type, { method: "POST", body: donnees });
    const json = await reponse.json();
    if (reponse.ok) {
      cache[type] = json.resultat;
      if (typeActif === type) afficher(json.resultat);
    } else if (typeActif === type) {
      contenuResultat.textContent = "❌ " + json.erreur;
    }
  } catch (e) {
    if (typeActif === type) {
      contenuResultat.textContent = "❌ Impossible de contacter le serveur. Vérifie que python app.py tourne.";
    }
  }
}

onglets.forEach((o) => {
  o.addEventListener("click", () => charger(o.dataset.type));
});

// Bouton Générer
boutonGenerer.addEventListener("click", async () => {
  if (!fichierChoisi) return;

  boutonGenerer.disabled = true;
  boutonGenerer.classList.add("charge");
  boutonGenerer.textContent = "⏳ L'IA lit ton cours...";

  await charger("resume");
  blocResultat.scrollIntoView({ behavior: "smooth" });

  boutonGenerer.disabled = false;
  boutonGenerer.classList.remove("charge");
  boutonGenerer.textContent = "✨ Générer mes outils";
});