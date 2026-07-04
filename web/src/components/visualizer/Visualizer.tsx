'use client'

import { useState } from 'react';
import type { TraceEvent } from '@/lib/schema';
import { useTrace } from '@/lib/TraceContext';
import { usePlayback } from '@/lib/PlaybackContext';

import { useNodePositions } from './hooks/useNodePositions';
import { useMessageArrows } from './hooks/useMessageArrows';
import { useEventGroups } from './hooks/useEventGroups';
import { BASE_TIME_SCALE, PADDING_X, PADDING_Y, NODE_HEIGHT } from './constants';

import LifelineLayer from './LifelineLayer';
import TimeAxis from './TimeAxis';
import EventDots from './EventDots';
import MessageArrows from './MessageArrows';
import Playhead from './Playhead';
import EventDetailsPanel from './EventDetailsPanel';

import styles from './Visualizer.module.css';

export default function Visualizer() {
  const { traceData } = useTrace();
  const { currentClock, maxTime, zoomScale } = usePlayback();
  const [selectedEvents, setSelectedEvents] = useState<TraceEvent[] | null>(null);

  const nodes = useNodePositions(traceData);
  const messages = useMessageArrows(traceData, nodes, zoomScale);
  const eventGroups = useEventGroups(traceData, currentClock, nodes, zoomScale);

  if (!traceData || nodes.length === 0) return null;

  const timeScale = BASE_TIME_SCALE * zoomScale;
  
  const totalHeight = nodes.length > 0 ? PADDING_Y * 2 + (nodes.length - 1) * NODE_HEIGHT : 400;
  const totalWidth = Math.max(800, PADDING_X * 2 + maxTime * timeScale + 200);
  
  const currentX = PADDING_X + currentClock * timeScale;

  return (
    <div className={styles.visualizerWrapper}>
      <div className={styles.scrollContainer}>
        <svg
          className={styles.svgLayer}
          width={totalWidth}
          height={totalHeight}
          xmlns="http://www.w3.org/2000/svg"
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
