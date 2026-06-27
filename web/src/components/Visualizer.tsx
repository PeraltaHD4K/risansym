'use client'

import { useMemo } from 'react';
import { useSimulation } from '@/lib/SimulationContext';
import styles from './Visualizer.module.css';

export default function Visualizer() {
  const { traceData, currentClock } = useSimulation();

  const CANVAS_SIZE = 600;
  const RADIUS = 220;
  const CENTER = CANVAS_SIZE / 2;

  // 1. Extraer nodos únicos
  const nodes = useMemo(() => {
    if (!traceData) return [];
    const nodeSet = new Set<number>();
    traceData.trace.forEach(event => {
      nodeSet.add(event.source);
      if ('target' in event) nodeSet.add(event.target);
    });
    
    // Ordenar nodos y asignar coordenadas circulares
    const sorted = Array.from(nodeSet).sort((a, b) => a - b);
    return sorted.map((id, index) => {
      const angle = (index / sorted.length) * 2 * Math.PI - Math.PI / 2; // Empezar arriba
      return {
        id,
        x: CENTER + RADIUS * Math.cos(angle),
        y: CENTER + RADIUS * Math.sin(angle),
      };
    });
  }, [traceData]);

  // 2. Extraer mensajes en tránsito
  const activeMessages = useMemo(() => {
    if (!traceData) return [];
    
    // Un mensaje está activo si fue transmitido antes o igual al reloj actual,
    // y su tiempo de llegada (event_time) es estrictamente mayor al reloj actual.
    // (O si acaba de llegar, para mostrar el impacto).
    const transmits = traceData.trace.filter(e => e.action === 'TRANSMIT' && e.clock <= currentClock && e.event_time >= currentClock);
    
    return transmits.map((t, index) => {
      const srcNode = nodes.find(n => n.id === t.source);
      const dstNode = nodes.find(n => n.id === (t as any).target);
      
      if (!srcNode || !dstNode) return null;
      
      const totalDuration = (t as any).event_time - t.clock;
      const progress = totalDuration > 0 ? (currentClock - t.clock) / totalDuration : 1;
      
      const x = srcNode.x + (dstNode.x - srcNode.x) * progress;
      const y = srcNode.y + (dstNode.y - srcNode.y) * progress;
      
      return {
        id: `${index}-${t.source}-${(t as any).target}-${t.clock}-${t.name}`,
        name: t.name,
        x,
        y,
        progress
      };
    }).filter(Boolean);
  }, [traceData, currentClock, nodes]);

  if (!traceData) return null;

  return (
    <div className={styles.canvasContainer}>
      <svg width={CANVAS_SIZE} height={CANVAS_SIZE} className={styles.svgLayer}>
        {/* Enlaces base tenues (Topología completa supuesta) */}
        {nodes.map(n1 => 
          nodes.map(n2 => {
            if (n1.id >= n2.id) return null;
            return (
              <line 
                key={`link-${n1.id}-${n2.id}`}
                x1={n1.x} y1={n1.y} 
                x2={n2.x} y2={n2.y} 
                stroke="rgba(255, 255, 255, 0.03)" 
                strokeWidth="1"
              />
            );
          })
        )}

        {/* Mensajes en tránsito (Partículas) */}
        {activeMessages.map((msg: any) => (
          <g key={msg.id} transform={`translate(${msg.x}, ${msg.y})`}>
            <circle r="6" fill="var(--accent-color)" className={styles.particleGlow} />
            <circle r="4" fill="#fff" />
            <text y="-12" textAnchor="middle" fill="var(--accent-color)" fontSize="12" fontWeight="bold">
              {msg.name}
            </text>
          </g>
        ))}
      </svg>

      {/* Nodos HTML para mejor renderizado CSS */}
      {nodes.map(node => (
        <div 
          key={node.id} 
          className={styles.node}
          style={{ left: node.x, top: node.y }}
        >
          <span className={styles.nodeId}>N{node.id}</span>
        </div>
      ))}
    </div>
  );
}
