'use client'

import { memo } from 'react';
import type { TraceEvent } from '@/lib/schema';
import { isTransmitEvent, isReceiveEvent } from '@/lib/schema';
import type { EventGroup } from './hooks/useEventGroups';
import styles from './Visualizer.module.css';

interface EventDotsProps {
  groups: EventGroup[];
  onSelectEvent: (events: TraceEvent[]) => void;
}

/** Renders grouped event dots: circles for TRANSMIT, squares for RECEIVE, diamonds for APP_LOG. */
function EventDotsInner({ groups, onSelectEvent }: EventDotsProps) {
  return (
    <>
      {/* Puntos Discretos de Eventos Agrupados (Event Dots) */}
      {groups.map(group => {
        const { x, y, events } = group;

        let DotShape: React.JSX.Element;

        if (events.length > 1) {
          DotShape = (
            <g>
              <circle cx={x} cy={y} r="8" fill="#ffffff" stroke="var(--accent-color)" strokeWidth="2" />
              <text x={x} y={y + 3} fontSize="9" fontWeight="bold" fill="#000" textAnchor="middle">
                {events.length}
              </text>
            </g>
          );
        } else {
          const evt = events[0];
          if (isTransmitEvent(evt)) {
            DotShape = <circle cx={x} cy={y} r="5" fill="#3b82f6" />;
          } else if (isReceiveEvent(evt)) {
            DotShape = <rect x={x - 5} y={y - 5} width="10" height="10" fill="#10b981" rx="2" />;
          } else {
            // APP_LOG — diamond shape
            DotShape = <polygon points={`${x},${y - 6} ${x + 6},${y} ${x},${y + 6} ${x - 6},${y}`} fill="#f59e0b" />;
          }
        }

        return (
          <g
            key={group.key}
            className={styles.eventDot}
            onClick={() => onSelectEvent(events)}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectEvent(events); } }}
            role="button"
            tabIndex={0}
            aria-label={`${events.length} evento(s) en t=${group.clock}`}
          >
            <title>{`${events.length} evento(s) en t=${group.clock}`}</title>
            {DotShape}
          </g>
        );
      })}
    </>
  );
}

const EventDots = memo(EventDotsInner);
EventDots.displayName = 'EventDots';
export default EventDots;
