'use client'

import type { TraceEvent } from '@/lib/schema';
import styles from './EventDetailsPanel.module.css';

interface EventDetailsPanelProps {
  selectedEvents: TraceEvent[] | null;
  onClose: () => void;
}

/** Floating panel showing event JSON details. Renders outside the scroll container. */
export default function EventDetailsPanel({ selectedEvents, onClose }: EventDetailsPanelProps) {
  if (!selectedEvents) return null;

  const title = selectedEvents.length > 1
    ? `Múltiples Eventos (${selectedEvents.length})`
    : 'Detalles del Evento';

  return (
    <div className={`glass-panel ${styles.detailsPanel}`}>
      <div className={styles.header}>
        <h4 className={styles.title}>{title}</h4>
        <button onClick={onClose} className={styles.closeBtn} aria-label="Cerrar detalles">
          <span aria-hidden="true">×</span>
        </button>
      </div>
      <div className={styles.scrollBody}>
        {selectedEvents.map((ev, i) => (
          <div key={i} className={styles.eventEntry}>
            <span className={styles.eventLabel}>
              #{i + 1} - {ev.action} {'name' in ev ? `(${ev.name})` : ''}
            </span>
            <pre className={styles.jsonDump}>
              {JSON.stringify(ev, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
