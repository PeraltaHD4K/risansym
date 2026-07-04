interface PlayheadProps {
  x: number;
  totalHeight: number;
}

/** Renders the vertical playhead line + triangle indicator. */
export default function Playhead({ x, totalHeight }: PlayheadProps) {
  return (
    <>
      {/* Playhead (Línea de tiempo actual vertical) */}
      <line
        x1={x} y1={20}
        x2={x} y2={totalHeight - 20}
        stroke="var(--danger-color)"
        strokeWidth={2}
        strokeDasharray="6,4"
      />
      <polygon
        points={`${x - 6},20 ${x + 6},20 ${x},28`}
        fill="#ef4444"
      />
    </>
  );
}
