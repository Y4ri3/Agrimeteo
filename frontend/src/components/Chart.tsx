export type Series = { name: string; values: (number | null)[]; kind: "bar" | "line" };

const W = 640, H = 250, L = 58, R = 14, T = 14, B = 34;
const dayLabel = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });

/** Graduations « rondes » (1, 2, 5, 10, 20…) : au plus 5 repères entre le bas et le haut. */
function ticks(lo: number, hi: number): number[] {
  const raw = (hi - lo) / 4 || 1;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((m) => m * pow).find((s) => s >= raw) ?? raw;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v * 100) / 100);
  return out;
}

/**
 * Graphique à barres ou lignes avec axes nommés, repères de dates et survol des valeurs.
 * Une valeur manquante (null) laisse un trou : jamais 0.
 */
export function Chart({
  title, unit, yLabel, dates, series, howToRead,
}: {
  title: string; unit: string; yLabel: string; dates: string[]; series: Series[]; howToRead: string;
}) {
  const all = series.flatMap((s) => s.values).filter((v): v is number => v !== null);
  if (all.length === 0) return <p className="muted">{title} : aucune donnée sur la période.</p>;
  // Les barres partent de zéro ; pour des courbes, l'axe s'ajuste aux valeurs (sinon elles s'écrasent en haut).
  const hasBars = series.some((s) => s.kind === "bar");
  const spread = Math.max(...all) - Math.min(...all) || 1;
  const lo = hasBars ? Math.min(0, ...all) : Math.floor(Math.min(...all) - spread * 0.15);
  const hi = hasBars ? Math.max(...all, lo + 1) : Math.ceil(Math.max(...all) + spread * 0.15);
  const grid = ticks(lo, hi);
  const top = Math.max(hi, grid[grid.length - 1] ?? hi);
  const x = (i: number) => L + ((i + 0.5) * (W - L - R)) / dates.length;
  const y = (v: number) => T + ((top - v) * (H - T - B)) / (top - lo);
  const bw = Math.max(1.5, ((W - L - R) / dates.length) * 0.7);
  const mid = Math.floor((dates.length - 1) / 2);
  const xLabels = [0, mid, dates.length - 1].filter((v, i, a) => a.indexOf(v) === i);
  return (
    <figure className="chartbox">
      <figcaption>{title}</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${title}, du ${dayLabel(dates[0])} au ${dayLabel(dates[dates.length - 1])}. ${howToRead}`} className="chart">
        {grid.map((g) => (
          <g key={g}>
            <line x1={L} x2={W - R} y1={y(g)} y2={y(g)} className={g === 0 ? "axis" : "gridline"} />
            <text x={L - 8} y={y(g) + 4} textAnchor="end" className="tick">{String(g).replace(".", ",")}</text>
          </g>
        ))}
        <text transform={`translate(14 ${(T + H - B) / 2}) rotate(-90)`} textAnchor="middle" className="axis-title">{yLabel}</text>
        {xLabels.map((i) => (
          <text key={i} x={x(i)} y={H - 10} textAnchor={i === 0 ? "start" : i === dates.length - 1 ? "end" : "middle"} className="tick">{dayLabel(dates[i])}</text>
        ))}
        {series.map((s, k) =>
          s.kind === "bar" ? (
            s.values.map((v, i) => v === null ? null : (
              <rect key={i} x={x(i) - bw / 2} y={Math.min(y(v), y(0))} width={bw} height={Math.max(0.5, Math.abs(y(0) - y(v)))} className={`s${k}`}>
                <title>{`${dayLabel(dates[i])} : ${String(v).replace(".", ",")} ${unit}`}</title>
              </rect>
            ))
          ) : (
            <g key={s.name}>
              <polyline fill="none" className={`line s${k}`} points={s.values.map((v, i) => (v === null ? null : `${x(i)},${y(v)}`)).filter(Boolean).join(" ")} />
              {s.values.map((v, i) => v === null ? null : (
                <circle key={i} cx={x(i)} cy={y(v)} r={3} className={`dot s${k}`}>
                  <title>{`${s.name}, ${dayLabel(dates[i])} : ${String(v).replace(".", ",")} ${unit}`}</title>
                </circle>
              ))}
            </g>
          ),
        )}
      </svg>
      <p className="legend">{series.map((s, k) => <span key={s.name} className={`key s${k}`}>{s.name}</span>)}</p>
      <p className="howto"><strong>Comment lire.</strong> {howToRead}</p>
    </figure>
  );
}
