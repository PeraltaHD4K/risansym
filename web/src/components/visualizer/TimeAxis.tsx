import { memo } from 'react';
import styles from './Visualizer.module.css';
import { PADDING_X } from './constants';

interface TimeAxisProps {
  maxTime: number;
  timeScale: number;
  totalHeight: number;
  totalWidth: number;
}

const TimeAxis = memo(function TimeAxis({ maxTime, timeScale, totalHeight, totalWidth }: TimeAxisProps) {
  const TARGET_TICKS = 10;
  const step = Math.max(1, maxTime / TARGET_TICKS);
  const power = Math.pow(10, Math.floor(Math.log10(step)));
  const normalizedStep = step / power;
  let tickInterval = power;
  if (normalizedStep > 5) tickInterval *= 10;
  else if (normalizedStep > 2) tickInterval *= 5;
  else if (normalizedStep > 1) tickInterval *= 2;
  tickInterval = Math.max(1, Math.round(tickInterval));

  const ticks = [];
  for (let t = 0; t <= maxTime; t += tickInterval) {
    ticks.push(t);
  }

  return (
    <>
      {/* Eje de Tiempo (Ticks abajo) */}
      <line
        x1={PADDING_X} y1={totalHeight - 20}
        x2={totalWidth - 50} y2={totalHeight - 20}
        className={styles.timeAxis}
      />
      {ticks.map((t) => (
        <g key={`tick-${t}`}>
          <line
            x1={PADDING_X + t * timeScale} y1={totalHeight - 25}
            x2={PADDING_X + t * timeScale} y2={totalHeight - 15}
            stroke="var(--text-secondary)"
          />
          <text
            x={PADDING_X + t * timeScale} y={totalHeight - 5}
            className={styles.timeTick}
          >
            {t}s
          </text>
        </g>
      ))}
    </>
  );
});

export default TimeAxis;
