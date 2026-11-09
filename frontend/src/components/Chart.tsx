export type Series = { name: string; values: (number | null)[]; kind: "bar" | "line" };

const W = 640, H = 220, L = 44, R = 12, T = 12, B = 28;

/** Graphique SVG minimal (barres ou lignes). Une valeur manquante (null) laisse un trou : jamais 0. */
export function Chart({ title, unit, dates, series }: { title: string; unit: string; dates: string[]; series: Series[] }) {
  const all = series.flatMap((s) => s.values).filter((v): v is number => v !== null);
  if (all.length === 0) return <p className="muted">{title} : aucune donnée.</p>;
  const lo = Math.min(0, ...all), hi = Math.max(...all, lo + 1);
  const x = (i: number) => L + ((i + 0.5) * (W - L - R)) / dates.length;
  const y = (v: number) => T + ((hi - v) * (H - T - B)) / (hi - lo);
  const bw = Math.max(1, ((W - L - R) / dates.length) * 0.7);
  return (
    <figure>
      <figcaption>{title} ({unit})</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${title}, du ${dates[0]} au ${dates[dates.length - 1]}`} className="chart">
        <line x1={L} x2={W - R} y1={y(0)} y2={y(0)} className="axis" />
        {[lo, (lo + hi) / 2, hi].map((t) => (
          <text key={t} x={L - 6} y={y(t) + 4} textAnchor="end" className="tick">{Math.round(t * 10) / 10}</text>
        ))}
        <text x={L} y={H - 8} className="tick">{dates[0]}</text>
        <text x={W - R} y={H - 8} textAnchor="end" className="tick">{dates[dates.length - 1]}</text>
        {series.map((s, k) =>
          s.kind === "bar" ? (
            s.values.map((v, i) => v === null ? null : (
              <rect key={i} x={x(i) - bw / 2} y={Math.min(y(v), y(0))} width={bw} height={Math.abs(y(0) - y(v))} className={`s${k}`} />
            ))
          ) : (
            <polyline key={s.name} fill="none" className={`line s${k}`}
              points={s.values.map((v, i) => (v === null ? null : `${x(i)},${y(v)}`)).filter(Boolean).join(" ")} />
          ),
        )}
      </svg>
      <p className="legend">{series.map((s, k) => <span key={s.name} className={`key s${k}`}>{s.name}</span>)}</p>
    </figure>
  );
}
