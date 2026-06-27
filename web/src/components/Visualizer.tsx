'use client'

import { useMemo, useState } from 'react';
import { useSimulation } from '@/lib/SimulationContext';
import styles from './Visualizer.module.css';

const NODE_HEIGHT = 100;
const TIME_SCALE = 80; // píxeles por cada unidad de tiempo (segundo)
const PADDING_X = 60;
const PADDING_Y = 60;

export default function Visualizer() {
  const { traceData, currentClock, maxTime } = useSimulation();
  const [selectedEvent, setSelectedEvent] = useState<any | null>(null);

  const nodes = useMemo(() => {
    if (!traceData) return [];
    const nodeSet = new Set<number>();
    traceData.trace.forEach(event => {
      nodeSet.add(event.source);
      if ('target' in event) nodeSet.add(event.target);
    });
    
    return Array.from(nodeSet)
      .sort((a, b) => a - b)
      .map((id, index) => ({
        id,
        y: PADDING_Y + index * NODE_HEIGHT
      }));
  }, [traceData]);

  const messages = useMemo(() => {
    if (!traceData) return [];
    
    // Asignar colores fijos a tipos de mensajes comunes para distinguirlos
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#ec4899'];
    const typeColorMap = new Map<string, string>();
    let colorIndex = 0;

    return traceData.trace
      .filter(e => e.action === 'TRANSMIT')
      .map((t, index) => {
        const srcNode = nodes.find(n => n.id === t.source);
        const dstNode = nodes.find(n => n.id === (t as any).target);
        if (!srcNode || !dstNode) return null;

        if (!typeColorMap.has(t.name)) {
          typeColorMap.set(t.name, colors[colorIndex % colors.length]);
          colorIndex++;
        }

        const startX = PADDING_X + t.clock * TIME_SCALE;
        const endX = PADDING_X + (t as any).event_time * TIME_SCALE;

        return {
          originalEvent: t,
          id: `${index}-${t.source}-${(t as any).target}-${t.clock}-${t.name}`,
          name: t.name,
          color: typeColorMap.get(t.name),
          startX,
          startY: srcNode.y,
          endX,
          endY: dstNode.y,
          clock: t.clock,
          eventTime: (t as any).event_time,
          payload: t.payload
        };
      }).filter(Boolean);
  }, [traceData, nodes]);

  if (!traceData) return null;

  const totalHeight = nodes.length > 0 ? PADDING_Y * 2 + (nodes.length - 1) * NODE_HEIGHT : 400;
  // Añadimos un poco de margen al final del X para que se vea cómodo
  const totalWidth = Math.max(800, PADDING_X * 2 + maxTime * TIME_SCALE + 200);

  const currentPlayheadX = PADDING_X + currentClock * TIME_SCALE;

  return (
    <div className={styles.scrollContainer}>
      <svg width={totalWidth} height={totalHeight} className={styles.svgLayer}>
        <defs>
          {/* Marcadores para las flechas de los mensajes (Solo colores únicos) */}
          {Array.from(new Set(messages.map((m: any) => m.color))).map(color => (
            <marker
              key={`arrow-${color}`}
              id={`arrow-${(color as string).replace('#', '')}`}
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <path d="M0,0 L0,6 L9,3 z" fill={color as string} />
            </marker>
          ))}
        </defs>

        {/* Líneas horizontales de vida de cada Nodo */}
        {nodes.map(node => (
          <g key={`lifeline-${node.id}`}>
            <text x={10} y={node.y + 5} className={styles.nodeLabel}>N{node.id}</text>
            <line 
              x1={PADDING_X} y1={node.y} 
              x2={totalWidth - 50} y2={node.y} 
              className={styles.lifeline} 
              strokeDasharray="4,4"
            />
          </g>
        ))}

        {/* Eje de Tiempo (Ticks abajo) */}
        <line 
          x1={PADDING_X} y1={totalHeight - 20} 
          x2={totalWidth - 50} y2={totalHeight - 20} 
          className={styles.timeAxis} 
        />
        {Array.from({ length: Math.ceil(maxTime) + 1 }).map((_, i) => (
          <g key={`tick-${i}`}>
            <line 
              x1={PADDING_X + i * TIME_SCALE} y1={totalHeight - 25} 
              x2={PADDING_X + i * TIME_SCALE} y2={totalHeight - 15} 
              stroke="var(--text-secondary)" 
            />
            <text 
              x={PADDING_X + i * TIME_SCALE} y={totalHeight - 5} 
              className={styles.timeTick}
            >
              {i}s
            </text>
          </g>
        ))}

        {/* Puntos Discretos de Eventos (Event Dots para inspeccionar el Payload genéricamente) */}
        {traceData.trace.map((evt, index) => {
          // El nodo que ejecuta la acción (en RECEIVE suele ser el source en nuestro esquema, o target, depende, 
          // usaremos 'source' como el dueño del evento por defecto)
          const ownerId = evt.action === 'RECEIVE' ? evt.target : evt.source;
          const node = nodes.find(n => n.id === ownerId);
          
          if (!node) return null;
          if (evt.clock > currentClock) return null; // Solo renderizar hasta el reloj actual

          const x = PADDING_X + evt.clock * TIME_SCALE;
          const y = node.y;

          let DotShape;
          let dotColor = '#94a3b8'; // default
          
          if (evt.action === 'TRANSMIT') {
            dotColor = '#3b82f6'; // Azul
            DotShape = <circle cx={x} cy={y} r="5" fill={dotColor} />;
          } else if (evt.action === 'RECEIVE') {
            dotColor = '#10b981'; // Verde
            DotShape = <rect x={x - 5} y={y - 5} width="10" height="10" fill={dotColor} rx="2" />;
          } else {
            dotColor = '#f59e0b'; // Amarillo (APP_LOG)
            DotShape = <polygon points={`${x},${y-6} ${x+6},${y} ${x},${y+6} ${x-6},${y}`} fill={dotColor} />;
          }

          return (
            <g 
              key={`dot-${index}-${evt.clock}`} 
              className={styles.eventDot}
              onClick={() => setSelectedEvent(evt)}
            >
              {DotShape}
            </g>
          );
        })}

        {/* Flechas de Mensajes */}
        {messages.map((msg: any) => {
          const isFuture = msg.clock > currentClock;
          const isPending = msg.clock <= currentClock && msg.eventTime > currentClock;
          const isPast = msg.eventTime <= currentClock;

          if (isFuture) return null;

          return (
            <g 
              key={msg.id} 
              className={styles.messageGroup}
              onClick={() => setSelectedEvent(msg.originalEvent)}
              style={{ cursor: 'pointer', opacity: isPast ? 1 : 0.8 }}
            >
              <line
                x1={msg.startX} y1={msg.startY}
                x2={isPending ? currentPlayheadX : msg.endX} 
                y2={isPending ? msg.startY + (msg.endY - msg.startY) * ((currentClock - msg.clock) / (msg.eventTime - msg.clock)) : msg.endY}
                stroke={msg.color}
                strokeWidth={isPending ? 3 : 2}
                markerEnd={isPending ? '' : `url(#arrow-${msg.color.replace('#', '')})`}
                className={isPending ? styles.animatedLine : ''}
              />
              {!isPending && (
                <text 
                  x={(msg.startX + msg.endX) / 2} 
                  y={(msg.startY + msg.endY) / 2 - 5} 
                  className={styles.messageLabel}
                  fill={msg.color}
                >
                  {msg.name}
                </text>
              )}
            </g>
          );
        })}

        {/* Playhead (Línea de tiempo actual vertical) */}
        <line 
          x1={currentPlayheadX} y1={20} 
          x2={currentPlayheadX} y2={totalHeight - 20} 
          className={styles.playhead} 
        />
        <polygon 
          points={`${currentPlayheadX - 6},20 ${currentPlayheadX + 6},20 ${currentPlayheadX},28`} 
          fill="#ef4444" 
        />
      </svg>

      {/* Panel de Detalles */}
      {selectedEvent && (
        <div className={`glass-panel ${styles.detailsPanel}`}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h4 style={{ margin: 0, color: 'var(--accent-color)' }}>Detalles del Evento</h4>
            <button onClick={() => setSelectedEvent(null)} className={styles.closeBtn}>×</button>
          </div>
          <pre className={styles.jsonDump}>
            {JSON.stringify(selectedEvent, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
