import { STATUS } from "../labels";
import { Gauge, limitsSentence, type Criterion } from "./Gauge";

/** Un repère du profil : ce qu'on mesure, où est la limite, où on se situe, et pourquoi. */
export function CriterionCard({ c }: { c: Criterion }) {
  const s = STATUS[c.status] ?? { word: c.status, icon: "" };
  return (
    <li className={`crit st-${c.status}`} data-testid={`critere-${c.id}`}>
      <div className="crit-head">
        <h3>{c.label ?? c.id}{c.window_days ? <small> sur {c.window_days} jours</small> : null}</h3>
        <span className={`tag s-${c.status}`}><span aria-hidden="true">{s.icon}</span> {s.word}</span>
      </div>
      <Gauge c={c} />
      <p className="crit-limits">Limites : {limitsSentence(c)}.{c.blocking ? " Un résultat défavorable ici suffit pour répondre non." : ""}</p>
      <p className="crit-why">{c.explanation}</p>
    </li>
  );
}
