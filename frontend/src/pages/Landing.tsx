import { Brand } from "../components/Header";
import { CriterionCard } from "../components/CriterionCard";
import { RainCurtain } from "../components/RainCurtain";
import { KAOLACK_RAIN, KAOLACK_START, TRIGGER_INDEX } from "../landing-data";
import { EXAMPLE_CRITERIA } from "../landing-example";
import { frDay } from "../labels";

const dayOf = (index: number) => {
  const d = new Date(`${KAOLACK_START}T00:00:00`);
  d.setDate(d.getDate() + index);
  return frDay(d.toISOString().slice(0, 10));
};

const CROPS = [
  ["Arachide", "Bassin arachidier"],
  ["Mil", "Bassin arachidier, Ferlo, Sénégal oriental"],
  ["Riz", "Vallée du fleuve, Casamance"],
  ["Tomate", "Niayes, vallée du fleuve"],
];

export function Landing() {
  return (
    <>
      <section className="hero">
        <RainCurtain
          values={KAOLACK_RAIN}
          height={290}
          title="Pluie quotidienne à Kaolack, de juin à septembre 2025"
          markIndex={TRIGGER_INDEX}
          markLabel={`${dayOf(TRIGGER_INDEX)} : 20 mm en 3 jours, le signal de semis`}
        />
        <span className="sun" aria-hidden="true" />
        <header className="hero-header">
          <Brand />
          <nav aria-label="Sur cette page">
            <a href="#exemple">Un exemple</a>
            <a href="#etapes">Comment ça marche</a>
            <a href="#cultures">Cultures</a>
            <a className="pill-cta" href="#/analyse">Vérifier pour mon champ</a>
          </nav>
        </header>
        <div className="hero-text">
          <p className="kicker">Aide à la décision pour le semis, au Sénégal</p>
          <h1>Puis-je semer&nbsp;?</h1>
          <p className="lead">
            AgriMétéo lit la pluie et la chaleur des derniers jours à l'endroit de votre choix, puis vous dit si les
            conditions sont bonnes pour semer, et pourquoi.
          </p>
          <p className="hero-actions">
            <a className="button gold" href="#/analyse">Vérifier pour mon champ</a>
            <a className="link-light" href="#exemple">Voir un exemple de réponse</a>
          </p>
        </div>
        <svg className="furrows" viewBox="0 0 1440 150" preserveAspectRatio="none" aria-hidden="true">
          <path d="M0 70 L1440 20 V150 H0Z" fill="#7A3B22" />
          <path d="M0 100 L1440 56 V150 H0Z" fill="#9A4529" />
          <path d="M0 128 L1440 98 V150 H0Z" fill="#B8452A" />
          <path d="M0 146 L1440 132 V150 H0Z" fill="#EEF4F1" />
        </svg>
      </section>

      <section className="wrap section" id="exemple" aria-labelledby="t-exemple">
        <h2 id="t-exemple">À quoi ressemble une réponse</h2>
        <p className="intro">
          Un exemple réel : arachide à Kaolack, pendant les 30 jours jusqu'au 20 août 2025. Chaque repère est une
          mesure posée sur une échelle : vert, c'est bon ; rouge, c'est défavorable.
        </p>
        <div className="example">
          <div className="verdict tone-reserve">
            <p className="verdict-for">Arachide · Kaolack · du 22 juillet au 20 août 2025</p>
            <h3>Oui, sous réserve</h3>
            <p>Les trois repères sont dans le vert. La réponse reste prudente : les repères de la culture sont encore à valider.</p>
            <p className="verdict-fiab">Fiabilité de la réponse : moyenne</p>
          </div>
          <ul className="criteria stack">{EXAMPLE_CRITERIA.map((c) => <CriterionCard key={c.id} c={c} />)}</ul>
        </div>
      </section>

      <section className="wrap section" id="etapes" aria-labelledby="t-etapes">
        <h2 id="t-etapes">Comment ça marche</h2>
        <ol className="steps">
          <li><strong>Vous choisissez</strong><span>La culture, puis le lieu. Un nom de village ou de ville suffit.</span></li>
          <li><strong>L'outil récupère la météo</strong><span>La pluie et les températures des 30 derniers jours, depuis la base ouverte Open-Meteo.</span></li>
          <li><strong>Il répond en clair</strong><span>Oui, oui sous réserve, non, ou «&nbsp;on ne peut pas conclure&nbsp;», avec les raisons chiffrées.</span></li>
        </ol>
      </section>

      <section className="wrap section" id="cultures" aria-labelledby="t-cultures">
        <h2 id="t-cultures">Quatre cultures</h2>
        <ul className="crops">
          {CROPS.map(([name, zones]) => (
            <li key={name}><strong>{name}</strong><span>{zones}</span></li>
          ))}
        </ul>
        <p className="muted">Les données couvrent le monde entier : vous pouvez analyser n'importe quel lieu, même hors du Sénégal.</p>
      </section>

      <section className="wrap section two-col" aria-labelledby="t-limites">
        <div>
          <h2 id="t-limites" className="h-md">Ce que vous obtenez</h2>
          <ul className="dashes">
            <li>Une réponse en quatre niveaux, dite simplement.</li>
            <li>Les raisons, avec la valeur mesurée et la limite à laquelle elle est comparée.</li>
            <li>La qualité des données et un niveau de fiabilité.</li>
            <li>Les courbes de pluie et de température de la période.</li>
          </ul>
        </div>
        <div className="panel-dark">
          <h2 className="h-md">Ce que l'outil ne dit pas</h2>
          <ul className="dashes">
            <li>Si votre sol convient : sol, relief et pratiques ne sont pas évalués.</li>
            <li>Ce qui tombe sur votre parcelle : les données couvrent des mailles de plusieurs dizaines de kilomètres.</li>
            <li>Une garantie de récolte : c'est une aide à la décision, pas une promesse.</li>
          </ul>
        </div>
      </section>

      <section className="wrap section final">
        <h2>Prêt à vérifier&nbsp;?</h2>
        <p>Une minute, sans compte ni inscription.</p>
        <p><a className="button deep" href="#/analyse">Vérifier pour mon champ</a></p>
      </section>
    </>
  );
}
