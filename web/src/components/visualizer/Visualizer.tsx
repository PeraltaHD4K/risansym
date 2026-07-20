'use client'

import { useState } from 'react';
import type { TraceEvent } from '@/lib/schema';
import { useTrace } from '@/lib/TraceContext';
import { useClock, usePlaybackApi } from '@/lib/PlaybackContext';

import { useNodePositions } from './hooks/useNodePositions';
import { useMessageArrows } from './hooks/useMessageArrows';
import { useEventGroups } from './hooks/useEventGroups';
import { BASE_TIME_SCALE, PADDING_X, PADDING_Y, NODE_HEIGHT, MIN_SVG_HEIGHT, MIN_SVG_WIDTH, SVG_PADDING_RIGHT } from './constants';

import LifelineLayer from './LifelineLayer';
import TimeAxis from './TimeAxis';
import EventDots from './EventDots';
import MessageArrows from './MessageArrows';
import Playhead from './Playhead';
import EventDetailsPanel from './EventDetailsPanel';

import styles from './Visualizer.module.css';

export default function Visualizer() {
  const { traceData } = useTrace();
  const { currentClock } = useClock();
  const { maxTime, zoomScale } = usePlaybackApi();
  const [selectedEvents, setSelectedEvents] = useState<TraceEvent[] | null>(null);

  const nodes = useNodePositions(traceData);
  const messages = useMessageArrows(traceData, nodes, zoomScale);
  const eventGroups = useEventGroups(traceData, currentClock, nodes, zoomScale);

  if (!traceData || nodes.length === 0) return null;

  const timeScale = BASE_TIME_SCALE * zoomScale;
  
  const totalHeight = nodes.length > 0 ? PADDING_Y * 2 + (nodes.length - 1) * NODE_HEIGHT : MIN_SVG_HEIGHT;
  const totalWidth = Math.max(MIN_SVG_WIDTH, PADDING_X * 2 + maxTime * timeScale + SVG_PADDING_RIGHT);
  
  const currentX = PADDING_X + currentClock * timeScale;

  return (
    <div className={styles.visualizerWrapper}>
      <div className={styles.scrollContainer}>
        <svg
          id="visualizer-svg"
          className={styles.svgLayer}
          width={totalWidth}
          height={totalHeight}
          xmlns="http://www.w3.org/2000/svg"
          role="img"
          aria-label="Diagrama de secuencia de la simulación distribuida"
        >
          <LifelineLayer nodes={nodes} totalWidth={totalWidth} />
          
          <TimeAxis 
            maxTime={maxTime} 
            timeScale={timeScale} 
            totalHeight={totalHeight} 
            totalWidth={totalWidth} 
          />

          <MessageArrows 
            messages={messages} 
            currentClock={currentClock} 
            onSelectEvent={setSelectedEvents} 
          />

          <EventDots 
            groups={eventGroups} 
            onSelectEvent={setSelectedEvents} 
          />

          <Playhead x={currentX} totalHeight={totalHeight} />
        </svg>
      </div>

      <EventDetailsPanel 
        selectedEvents={selectedEvents} 
        onClose={() => setSelectedEvents(null)} 
      />
    </div>
  );
}
