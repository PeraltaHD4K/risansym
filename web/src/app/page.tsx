'use client'

import { Activity } from 'lucide-react';
import styles from './page.module.css';
import Uploader from '@/components/Uploader';
import PlaybackControls from '@/components/PlaybackControls';
import Visualizer from '@/components/Visualizer';
import { useSimulation } from '@/lib/SimulationContext';

export default function Home() {
  const { traceData, currentClock } = useSimulation();

  return (
    <main className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>
          Risan<span className="text-gradient">sym</span>
        </h1>
        <p className={styles.subtitle}>
          Simulador de Eventos Discretos de Alta Precisión. Arrastra una traza JSON para visualizar la coreografía del algoritmo.
        </p>
      </header>

      <div className={styles.dashboard}>
        {/* Panel Lateral (Controles) */}
        <aside className={`glass-panel ${styles.sidebar}`}>
          <h3>Inspector de Traza</h3>
          {traceData ? (
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              <p>Algoritmo: <strong style={{ color: 'var(--accent-color)' }}>{traceData.metadata.algorithm}</strong></p>
              <p>Topología: <strong style={{ color: 'var(--text-primary)' }}>{traceData.metadata.topology}</strong></p>
              <br/>
              <p>Métricas de Simulación:</p>
              <ul style={{ paddingLeft: '16px', marginTop: '8px' }}>
                <li>Eventos: {traceData.trace.length}</li>
                <li>Nodos Totales: {traceData.metadata.parameters.total_nodes}</li>
              </ul>
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Carga un archivo de simulación para habilitar los controles de tiempo y métricas.
            </p>
          )}
          
          <button className="premium-button" style={{ marginTop: 'auto', justifyContent: 'center' }}>
            <Activity size={18} />
            Documentación
          </button>
        </aside>

        {/* Área Principal (Lienzo / Drag & Drop) */}
        <section className={`glass-panel ${styles.mainArea}`}>
          {!traceData ? (
            <Uploader />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%', minWidth: 0, minHeight: 0 }}>
              <Visualizer />
              <PlaybackControls />
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
