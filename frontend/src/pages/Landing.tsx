import { RainStrip } from "../components/RainStrip";
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
