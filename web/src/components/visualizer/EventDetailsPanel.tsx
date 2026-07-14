'use client'

import { useEffect, useRef } from 'react';
import type { TraceEvent } from '@/lib/schema';
import styles from './EventDetailsPanel.module.css';

interface EventDetailsPanelProps {
  selectedEvents: TraceEvent[] | null;
  onClose: () => void;
}

/** Floating panel showing event JSON details. Renders outside the scroll container. */
export default function EventDetailsPanel({ selectedEvents, onClose }: EventDetailsPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!selectedEvents) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    
    // Focus the panel to move focus into the dialog
    if (panelRef.current) {
      panelRef.current.focus();
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedEvents, onClose]);

  if (!selectedEvents) return null;

  const title = selectedEvents.length > 1
    ? `Múltiples Eventos (${selectedEvents.length})`
    : 'Detalles del Evento';

  return (
    <div 
      ref={panelRef}
      className={`glass-panel ${styles.detailsPanel}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="event-details-title"
      tabIndex={-1}
    >
      <div className={styles.header}>
        <h4 id="event-details-title" className={styles.title}>{title}</h4>
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
