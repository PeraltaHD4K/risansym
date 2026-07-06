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
  return (
    <>
      {/* Eje de Tiempo (Ticks abajo) */}
      <line
        x1={PADDING_X} y1={totalHeight - 20}
        x2={totalWidth - 50} y2={totalHeight - 20}
        className={styles.timeAxis}
      />
      {Array.from({ length: Math.ceil(maxTime) + 1 }).map((_, i) => (
        <g key={`tick-${i}`}>
          <line
            x1={PADDING_X + i * timeScale} y1={totalHeight - 25}
            x2={PADDING_X + i * timeScale} y2={totalHeight - 15}
            stroke="var(--text-secondary)"
          />
          <text
            x={PADDING_X + i * timeScale} y={totalHeight - 5}
            className={styles.timeTick}
          >
            {i}s
          </text>
        </g>
      ))}
    </>
  );
});

export default TimeAxis;
