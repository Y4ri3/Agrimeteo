import type { Prediction } from "../api";

export type Criterion = Prediction["meteorological_favorability"]["criteria"][number];
type Tone = "ok" | "vigilance" | "defavorable";

const W = 600, H = 78, BAR_Y = 30, BAR_H = 18;
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

/** Place la valeur sur une échelle colorée : bon, à surveiller, défavorable. Pur affichage, aucun calcul de verdict. */
export function Gauge({ c }: { c: Criterion }) {
  if (!num(c.value) || (!num(c.vigilance) && !num(c.unfavorable))) return null;
  const { value, vigilance: vig, unfavorable: unf } = c;
  const points = [value, vig, unf].filter(num);
  const min = Math.min(...points), max = Math.max(...points);
  const span = Math.max(max - min, Math.abs(max) * 0.2, 1);
  const lo = min - span * 0.35, hi = max + span * 0.35;
  const x = (v: number) => ((v - lo) / (hi - lo)) * W;
  const up = c.direction === "higher_is_worse";

  // Zones de l'échelle, du plus bas au plus haut.
  const edges = [lo, ...[vig, unf].filter(num).sort((a, b) => a - b), hi];
  const tones: Tone[] = [];
  for (let i = 0; i < edges.length - 1; i++) {
    const mid = (edges[i] + edges[i + 1]) / 2;
    const crossedUnf = num(unf) && (up ? mid >= unf : mid <= unf);
    const crossedVig = num(vig) && (up ? mid >= vig : mid <= vig);
    tones.push(crossedUnf ? "defavorable" : crossedVig ? "vigilance" : "ok");
  }
  const unit = c.unit ? ` ${c.unit}` : "";
  return (
    <svg className="gauge" viewBox={`0 0 ${W} ${H}`} role="img"
      aria-label={`${c.label} : ${fr(value)}${unit}. Limites : ${limitsSentence(c)}.`}>
      {tones.map((t, i) => (
        <rect key={i} x={x(edges[i])} y={BAR_Y} width={x(edges[i + 1]) - x(edges[i])} height={BAR_H} className={`zone z-${t}`} />
      ))}
      {[vig, unf].filter(num).map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={BAR_Y - 2} y2={BAR_Y + BAR_H + 6} className="gauge-tick" />
          <text x={x(t)} y={H - 6} textAnchor="middle" className="gauge-label">{fr(t)}</text>
        </g>
      ))}
      <g transform={`translate(${x(value)} 0)`}>
        <path d={`M0 ${BAR_Y - 1} l-7 -11 h14 z`} className="gauge-marker" />
        <text y={12} textAnchor={x(value) > W - 70 ? "end" : x(value) < 70 ? "start" : "middle"} className="gauge-value">
          {fr(value)}{unit}
        </text>
      </g>
    </svg>
  );
}
