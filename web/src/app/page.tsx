'use client'

import { Activity } from 'lucide-react';
import styles from './page.module.css';
import Uploader from '@/components/Uploader';
import PlaybackControls from '@/components/PlaybackControls';
import Visualizer from '@/components/Visualizer';
import { useTrace } from '@/lib/TraceContext';

export default function Home() {
  const { traceData } = useTrace();

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
        <aside className={`glass-panel ${styles.sidebar}`} aria-label="Panel de detalles de traza">
          <h3>Inspector de Traza</h3>
          {traceData ? (
            <div className={styles.inspectorContent}>
              <p>Algoritmo: <strong className={styles.accentValue}>{traceData.metadata.algorithm}</strong></p>
              <p>Topología: <strong className={styles.primaryValue}>{traceData.metadata.topology}</strong></p>
              <br/>
              <p>Métricas de Simulación:</p>
              <ul className={styles.metricsList}>
                <li>Eventos: {traceData.trace.length}</li>
                <li>Nodos Totales: {String(traceData.metadata.parameters.total_nodes ?? 'N/A')}</li>
              </ul>
            </div>
          ) : (
            <p className={styles.inspectorContent}>
              Carga un archivo de simulación para habilitar los controles de tiempo y métricas.
            </p>
          )}
          
          <a 
            href="https://github.com/PeraltaHD4K/risansym" 
            target="_blank" 
            rel="noopener noreferrer" 
            className={`premium-button ${styles.docButton}`}
          >
            <Activity size={18} />
            Documentación
          </a>
        </aside>

        {/* Área Principal (Lienzo / Drag & Drop) */}
        <section className={`glass-panel ${styles.mainArea}`} aria-label="Visualizador principal">
          {!traceData ? (
            <Uploader />
          ) : (
            <div className={styles.visualizerLayout}>
              <Visualizer />
              <PlaybackControls />
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
