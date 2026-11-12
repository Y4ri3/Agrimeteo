/** Frise de pluie : une barre par jour. Un jour sans donnée (null) reste un trou hachuré, jamais 0. */
export function RainStrip({
  values,
  startLabel,
  endLabel,
  markIndex,
  markLabel,
  title,
  unitLabel,
}: {
  values: (number | null)[];
  startLabel: string;
  endLabel: string;
  markIndex?: number;
  markLabel?: string;
  title: string;
  unitLabel?: string;
}) {
  const W = 720, H = 150, T = 26, B = 22;
  const max = Math.max(1, ...values.filter((v): v is number => v !== null));
  const slot = W / values.length;
  const bar = Math.max(1.5, slot * 0.72);
  const x = (i: number) => i * slot + slot / 2;
  return (
    <figure className="strip">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title} preserveAspectRatio="none">
        <defs>
          <pattern id="trou" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="4" className="hatch" />
          </pattern>
        </defs>
        <line x1="0" x2={W} y1={H - B} y2={H - B} className="strip-base" />
        {values.map((v, i) =>
          v === null ? (
            <rect key={i} x={x(i) - bar / 2} y={T} width={bar} height={H - B - T} fill="url(#trou)" />
          ) : (
            <rect key={i} x={x(i) - bar / 2} y={H - B - (v / max) * (H - B - T)} width={bar} height={Math.max(0.5, (v / max) * (H - B - T))} className="strip-bar" />
          ),
        )}
        {markIndex !== undefined && (
          <>
            <line x1={x(markIndex)} x2={x(markIndex)} y1={6} y2={H - B} className="strip-mark" />
            <text x={Math.min(x(markIndex) + 6, W - 4)} y={14} textAnchor={x(markIndex) > W * 0.72 ? "end" : "start"} className="strip-label">
              {markLabel}
            </text>
          </>
        )}
        {unitLabel && (
          <text x={W} y={T - 8} textAnchor="end" className="strip-axis">{`jour le plus pluvieux : ${String(max).replace(".", ",")} ${unitLabel}`}</text>
        )}
        <text x={0} y={H - 6} className="strip-axis">{startLabel}</text>
        <text x={W} y={H - 6} textAnchor="end" className="strip-axis">{endLabel}</text>
      </svg>
    </figure>
  );
}
