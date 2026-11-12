import { CriterionCard } from "../components/CriterionCard";
import { RainStrip } from "../components/RainStrip";
import { EXAMPLE_CRITERIA } from "../landing-example";
import { KAOLACK_RAIN, KAOLACK_START, TRIGGER_INDEX } from "../landing-data";

function dayLabel(index: number): string {
  const d = new Date(`${KAOLACK_START}T00:00:00`);
  d.setDate(d.getDate() + index);
  return d.toLocaleDateString("fr-FR", { day: "numeric", month: "long" });
}

export function Landing() {
  return (
    <>
      <section className="hero">
        <div className="wrap hero-grid">
          <div>
            <h1>Puis-je semer&nbsp;?</h1>
            <p className="lead">
              AgriMétéo lit la pluie et la chaleur des derniers jours à l'endroit de votre choix, puis vous dit si
              les conditions sont bonnes pour semer de l'arachide ou du mil, et pourquoi.
            </p>
            <p className="hero-actions">
              <a className="button" href="#/analyse">Vérifier pour mon champ</a>
              <a className="link on-dark" href="#fonctionnement">Comment ça marche</a>
            </p>
          </div>
          <div className="hero-strip">
            <RainStrip
              values={KAOLACK_RAIN}
              startLabel="1er juin 2025"
              endLabel="30 septembre 2025"
              markIndex={TRIGGER_INDEX}
              markLabel={`${dayLabel(TRIGGER_INDEX)} : 20 mm en 3 jours`}
              title="Pluie quotidienne à Kaolack, de juin à septembre 2025"
            />
            <p className="caption">
              Pluie de chaque jour à Kaolack, de juin à septembre 2025. Le trait marque le premier épisode de 20 mm en
              3 jours, le signal que beaucoup d'agriculteurs du Sahel attendent pour semer. Les jours sans pluie ne
              dessinent rien.
            </p>
          </div>
        </div>
      </section>
      <svg className="furrows" viewBox="0 0 1200 60" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 30 C150 0 300 60 450 30 S750 0 900 30 S1100 55 1200 30 V60 H0Z" className="furrow f1" />
        <path d="M0 42 C160 18 320 66 480 42 S780 18 940 42 S1120 62 1200 44 V60 H0Z" className="furrow f2" />
        <path d="M0 52 C200 36 360 66 560 52 S900 38 1200 54 V60 H0Z" className="furrow f3" />
      </svg>

      <section className="wrap section" aria-labelledby="exemple">
        <h2 id="exemple">À quoi ressemble une réponse</h2>
        <p className="muted">
          Exemple réel : arachide à Kaolack, pendant les 30 jours jusqu'au 20 août 2025. Chaque repère est une mesure
          placée sur une échelle : vert, c'est bon ; rouge, c'est défavorable.
        </p>
        <div className="verdict tone-reserve example-verdict">
          <h3>Oui, sous réserve</h3>
          <p>Les trois repères sont dans le vert. La réponse reste prudente : les repères de la culture sont encore à valider.</p>
        </div>
        <ul className="criteria">{EXAMPLE_CRITERIA.map((c) => <CriterionCard key={c.id} c={c} />)}</ul>
      </section>

      <section className="wrap section" id="fonctionnement">
        <h2>Comment ça marche</h2>
        <ol className="steps">
          <li>
            <strong>Vous choisissez</strong> la culture et le lieu. Un nom de village ou de ville suffit.
          </li>
          <li>
            <strong>L'application récupère</strong> la pluie et les températures des 30 derniers jours, depuis la base
            ouverte Open-Meteo.
          </li>
          <li>
            <strong>Elle compare</strong> ces valeurs à des repères tirés d'études agricoles du Sahel, puis répond en
            clair, avec les raisons chiffrées.
          </li>
        </ol>
      </section>

      <section className="wrap section" aria-labelledby="cultures">
        <h2 id="cultures">Quatre cultures</h2>
        <ul className="crops">
          <li><strong>Arachide</strong><span>Bassin arachidier</span></li>
          <li><strong>Mil</strong><span>Bassin arachidier, Ferlo, Sénégal oriental</span></li>
          <li><strong>Riz</strong><span>Vallée du fleuve, Casamance</span></li>
          <li><strong>Tomate</strong><span>Niayes, vallée du fleuve</span></li>
        </ul>
        <p className="muted">Les données couvrent le monde entier : vous pouvez analyser n'importe quel lieu, même hors du Sénégal.</p>
      </section>

      <section className="wrap section two-col" aria-labelledby="limites">
        <div>
          <h2 id="limites">Ce que vous obtenez</h2>
          <ul className="plain">
            <li>Une réponse en quatre niveaux&nbsp;: oui, oui sous réserve, non, ou «&nbsp;on ne peut pas conclure&nbsp;».</li>
            <li>Les raisons, avec les valeurs mesurées et le repère auquel elles sont comparées.</li>
            <li>La qualité des données et un niveau de fiabilité.</li>
            <li>Les courbes de pluie et de température de la période.</li>
          </ul>
        </div>
        <div>
          <h2>Ce que l'outil ne dit pas</h2>
          <ul className="plain">
            <li>Si votre sol convient&nbsp;: sol, relief et pratiques ne sont pas évalués.</li>
            <li>Ce qui tombe sur votre parcelle&nbsp;: les données couvrent des mailles de plusieurs dizaines de kilomètres.</li>
            <li>Une garantie de récolte&nbsp;: c'est une aide à la décision, pas une promesse.</li>
            <li>Les repères sont encore à valider avec des conseillers agricoles.</li>
          </ul>
        </div>
      </section>

      <section className="wrap section cta">
        <h2>Prêt à vérifier ?</h2>
        <p>Cela prend une minute, sans compte ni inscription.</p>
        <p><a className="button" href="#/analyse">Vérifier pour mon champ</a></p>
      </section>
    </>
  );
}
