'use client'

import { useMemo, memo } from 'react';
import type { TraceEvent, ComputedMessage } from '@/lib/schema';
import styles from './Visualizer.module.css';

interface MessageArrowsProps {
  messages: ComputedMessage[];
  currentClock: number;
  onSelectEvent: (events: TraceEvent[]) => void;
}

/** Renders Bézier curve arrows between nodes with De Casteljau animation for pending messages. */
function MessageArrowsInner({ messages, currentClock, onSelectEvent }: MessageArrowsProps) {
  // Collect unique colors for SVG marker definitions
  const uniqueColors = useMemo(() => Array.from(new Set(messages.map(m => m.color))), [messages]);

  return (
    <>
      <defs>
        {/* Message arrow markers (Unique colors only) */}
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

      {/* Message Arrows (Drawn with Bezier Curves to avoid overlapping) */}
      {messages.map(msg => {
        const isFuture = msg.clock > currentClock;
        const isPending = msg.clock <= currentClock && msg.eventTime > currentClock;
        const isPast = msg.eventTime <= currentClock;

        if (isFuture) return null;

        let pathD = '';
        let endX = msg.endX;
        let endY = msg.endY;

        if (isPending) {
          // Curve animation using De Casteljau's algorithm
          const duration = msg.eventTime - msg.clock;
          const t = duration > 0 ? (currentClock - msg.clock) / duration : 1;
          const safeT = Math.max(0, Math.min(1, t));
          const invT = 1 - safeT;

          endX = invT * invT * msg.startX + 2 * invT * safeT * msg.cx + safeT * safeT * msg.endX;
          endY = invT * invT * msg.startY + 2 * invT * safeT * msg.cy + safeT * safeT * msg.endY;

          const newCx = msg.startX + safeT * (msg.cx - msg.startX);
          const newCy = msg.startY + safeT * (msg.cy - msg.startY);

          pathD = `M ${msg.startX},${msg.startY} Q ${newCx},${newCy} ${endX},${endY}`;
        } else {
          pathD = msg.staticPathD;
        }

        return (
          <g
            key={msg.id}
            className={`${styles.messageGroup} ${isPast ? styles.pastMessage : ''}`}
            onClick={() => onSelectEvent([msg.originalEvent])}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectEvent([msg.originalEvent]); } }}
            role="button"
            tabIndex={0}
            aria-label={`Mensaje ${msg.name} de nodo ${msg.originalEvent.source} a nodo ${msg.originalEvent.target}`}
          >
            <title>{`${msg.name}: nodo ${msg.originalEvent.source} → nodo ${msg.originalEvent.target}`}</title>
            {/* Thick invisible hitbox for easier hover/click */}
            <path
              d={pathD}
              stroke="transparent"
              strokeWidth={15}
              fill="none"
            />
            {/* Visible arrow line */}
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
                x={msg.cx}
                y={msg.cy - 5}
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

const MessageArrows = memo(MessageArrowsInner);
MessageArrows.displayName = 'MessageArrows';
export default MessageArrows;
