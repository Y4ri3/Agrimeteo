/**
 * Rideau de pluie : un trait par jour qui descend du haut, d'autant plus long qu'il a plu.
 * Un jour sans pluie est un trait pâle et court ; un jour sans donnée (null) reste un point gris, jamais 0.
 */
export function RainCurtain({
  values, height, title, markIndex, markLabel,
}: {
  values: (number | null)[]; height: number; title: string; markIndex?: number; markLabel?: string;
}) {
  const max = Math.max(1, ...values.filter((v): v is number => v !== null));
  return (
    <div className="curtain" role="img" aria-label={title} style={{ height: height + (markLabel ? 56 : 0) }}>
      <div className="curtain-bars" style={{ height }}>
        {values.map((v, i) => (
          <span
            key={i}
            className={`drop${v === null ? " gap" : v === 0 ? " dry" : ""}${i === markIndex ? " mark" : ""}`}
            style={{ height: v === null || v === 0 ? 3 : Math.max(5, Math.round((v / max) * (height - 30))) }}
          />
        ))}
      </div>
      {markIndex !== undefined && markLabel && (
        <div className="flag" style={{ left: `${((markIndex + 0.5) / values.length) * 100}%`, top: height + 10 }}>
          <span className="flag-tip" aria-hidden="true" />
          <span className="flag-text">{markLabel}</span>
        </div>
      )}
    </div>
  );
}
