import type { Prediction } from "../api";

export type Criterion = Prediction["meteorological_favorability"]["criteria"][number];
type Tone = "ok" | "vigilance" | "defavorable";

const fr = (n: number) => String(Math.round(n * 10) / 10).replace(".", ",");
const num = (n: number | null | undefined): n is number => n !== null && n !== undefined;

/** Phrase qui dit où sont les limites, dans le sens du critère. */
export function limitsSentence(c: Criterion): string {
  const u = c.unit ? ` ${c.unit}` : "";
  const up = c.direction === "higher_is_worse";
  const parts: string[] = [];
  if (num(c.vigilance)) parts.push(`à surveiller ${up ? "dès" : "à"} ${fr(c.vigilance)}${u}${up ? "" : " ou moins"}`);
  if (num(c.unfavorable)) parts.push(`défavorable ${up ? "dès" : "à"} ${fr(c.unfavorable)}${u}${up ? "" : " ou moins"}`);
  return parts.length ? parts.join(", ") : "aucun seuil défini";
}

/** Place la valeur sur une échelle colorée : bon, à surveiller, défavorable. Pur affichage, aucun verdict calculé ici. */
export function Gauge({ c }: { c: Criterion }) {
  if (!num(c.value) || (!num(c.vigilance) && !num(c.unfavorable))) return null;
  const { value, vigilance: vig, unfavorable: unf } = c;
  const points = [value, vig, unf].filter(num);
  const min = Math.min(...points), max = Math.max(...points);
  const span = Math.max(max - min, Math.abs(max) * 0.2, 1);
  const lo = min - span * 0.35, hi = max + span * 0.35;
  const pct = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const up = c.direction === "higher_is_worse";

  // Zones de l'échelle, du plus bas au plus haut.
  const edges = [lo, ...[vig, unf].filter(num).sort((a, b) => a - b), hi];
  const zones = edges.slice(0, -1).map((from, i) => {
    const mid = (from + edges[i + 1]) / 2;
    const bad = num(unf) && (up ? mid >= unf : mid <= unf);
    const warn = num(vig) && (up ? mid >= vig : mid <= vig);
    return { width: pct(edges[i + 1]) - pct(from), tone: (bad ? "defavorable" : warn ? "vigilance" : "ok") as Tone };
  });
  const unit = c.unit ? ` ${c.unit}` : "";
  return (
    <div className="gauge" role="img" aria-label={`${c.label} : ${fr(value)}${unit}. Limites : ${limitsSentence(c)}.`}>
      <span className="gauge-value" style={{ left: `${pct(value)}%` }}>{fr(value)}{unit}</span>
      <span className="gauge-pin" style={{ left: `${pct(value)}%` }} />
      <div className="gauge-bar">
        {zones.map((z, i) => <span key={i} className={`z z-${z.tone}`} style={{ flex: z.width }} />)}
      </div>
      {[vig, unf].filter(num).map((t) => (
        <span key={t}>
          <span className="gauge-tick" style={{ left: `${pct(t)}%` }} />
          <span className="gauge-label" style={{ left: `${pct(t)}%` }}>{fr(t)}{unit}</span>
        </span>
      ))}
    </div>
  );
}
