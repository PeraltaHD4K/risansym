'use client'

import type { TraceEvent, ComputedMessage } from '@/lib/schema';
import styles from './Visualizer.module.css';

interface MessageArrowsProps {
  messages: ComputedMessage[];
  currentClock: number;
  onSelectEvent: (events: TraceEvent[]) => void;
}

/** Renders Bézier curve arrows between nodes with De Casteljau animation for pending messages. */
export default function MessageArrows({ messages, currentClock, onSelectEvent }: MessageArrowsProps) {
  // Collect unique colors for SVG marker definitions
  const uniqueColors = Array.from(new Set(messages.map(m => m.color)));

  return (
    <>
      <defs>
        {/* Marcadores para las flechas de los mensajes (Solo colores únicos) */}
        {uniqueColors.map(color => (
          <marker
            key={`arrow-${color}`}
            id={`arrow-${color.replace('#', '')}`}
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L0,6 L9,3 z" fill={color} />
          </marker>
        ))}
      </defs>

      {/* Flechas de Mensajes (Trazadas con Curvas Bezier para evitar solapamiento) */}
      {messages.map(msg => {
        const isFuture = msg.clock > currentClock;
        const isPending = msg.clock <= currentClock && msg.eventTime > currentClock;
        const isPast = msg.eventTime <= currentClock;

        if (isFuture) return null;

        // Punto de control para la curva. Hacemos que se abombe ligeramente hacia arriba
        // o abajo en función de la distancia vertical, evitando que flechas colineales se solapen.
        const dy = msg.endY - msg.startY;
        const cx = (msg.startX + msg.endX) / 2;
        const cy = (msg.startY + msg.endY) / 2 - (dy * 0.15);

        let pathD = '';
        let endX = msg.endX;
        let endY = msg.endY;

        if (isPending) {
          // Animación de la curva usando el algoritmo de De Casteljau
          const t = (currentClock - msg.clock) / (msg.eventTime - msg.clock);
          const safeT = Math.max(0, Math.min(1, t));
          const invT = 1 - safeT;

          endX = invT * invT * msg.startX + 2 * invT * safeT * cx + safeT * safeT * msg.endX;
          endY = invT * invT * msg.startY + 2 * invT * safeT * cy + safeT * safeT * msg.endY;

          const newCx = msg.startX + safeT * (cx - msg.startX);
          const newCy = msg.startY + safeT * (cy - msg.startY);

          pathD = `M ${msg.startX},${msg.startY} Q ${newCx},${newCy} ${endX},${endY}`;
        } else {
          pathD = `M ${msg.startX},${msg.startY} Q ${cx},${cy} ${msg.endX},${msg.endY}`;
        }

        return (
          <g
            key={msg.id}
            className={styles.messageGroup}
            onClick={() => onSelectEvent([msg.originalEvent])}
            style={{ cursor: 'pointer', opacity: isPast ? 1 : 0.8 }}
          >
            {/* Hitbox invisible y gruesa para que sea fácil hacer hover/click */}
            <path
              d={pathD}
              stroke="transparent"
              strokeWidth={15}
              fill="none"
            />
            {/* Línea visible de la flecha */}
            <path
              d={pathD}
              stroke={msg.color}
              strokeWidth={isPending ? 3 : 2}
              fill="none"
              markerEnd={isPending ? '' : `url(#arrow-${msg.color.replace('#', '')})`}
              className={isPending ? styles.animatedLine : ''}
            />
            {!isPending && (
              <text
                x={cx}
                y={cy - 5}
                className={styles.messageLabel}
                fill={msg.color}
              >
                {msg.name}
              </text>
            )}
          </g>
        );
      })}
    </>
  );
}
