import { Link } from "react-router-dom";

const STEPS = [
  {
    title: "Scanner un produit",
    text: "Utilisez l'app Open Food Facts pour photographier le code-barres et enrichir la base.",
    link: "https://world.openfoodfacts.org/contribute",
  },
  {
    title: "Compléter les informations",
    text: "Ajoutez le Nutri-Score, les ingrédients, les allergènes et les magasins de vente.",
    link: "https://fr.openfoodfacts.org/",
  },
  {
    title: "Rejoindre la communauté",
    text: "Des milliers de citoyens améliorent chaque jour la transparence alimentaire en open data.",
    link: "https://wiki.openfoodfacts.org/Communaut%C3%A9",
  },
];

export default function Contribute() {
  return (
    <div className="contribute-page">
      <div className="contribute-hero card">
        <h1>Contribuer à Open Food Facts</h1>
        <p>
          FoodFacts Hub s'appuie sur les données ouvertes de la communauté. Vous aussi, aidez à
          rendre l'alimentation plus transparente pour tous.
        </p>
        <div className="contribute-actions">
          <Link to="/barcode" className="btn btn-primary" style={{ textDecoration: "none" }}>
            Rechercher un produit ici
          </Link>
          <a
            href="https://world.openfoodfacts.org/contribute"
            target="_blank"
            rel="noreferrer"
            className="btn btn-secondary"
            style={{ textDecoration: "none" }}
          >
            Contribuer sur Open Food Facts →
          </a>
        </div>
      </div>

      <div className="contribute-steps">
        {STEPS.map((step) => (
          <article key={step.title} className="card contribute-step">
            <h2>{step.title}</h2>
            <p>{step.text}</p>
            <a href={step.link} target="_blank" rel="noreferrer">
              En savoir plus →
            </a>
          </article>
        ))}
      </div>

      <div className="card contribute-tip">
        <h2>Pourquoi contribuer ?</h2>
        <ul>
          <li>Améliorer les recommandations de substituts plus sains</li>
          <li>Aider les personnes allergiques à trouver des alternatives sûres</li>
          <li>Renforcer une base de données libre et réutilisable (ODbL)</li>
        </ul>
      </div>
    </div>
  );
}
