import { useMemo } from 'react';
import type { TraceOutput, TraceEvent, NodePosition } from '@/lib/schema';
import { isReceiveEvent } from '@/lib/schema';
import { PADDING_X, BASE_TIME_SCALE } from '../constants';

/** A group of events occurring at the same node and clock tick. */
export interface EventGroup {
  key: string;
  ownerId: number;
  clock: number;
  x: number;
  y: number;
  events: TraceEvent[];
}

/**
 * Groups trace events by (node, clock) for dot rendering.
 * Uses a nested Map<number, Map<number, TraceEvent[]>> instead of string key parsing (W6 fix).
 * Only includes events at or before currentClock.
 */
export function useEventGroups(
  traceData: TraceOutput | null,
  currentClock: number,
  nodes: NodePosition[],
  zoomScale: number
): EventGroup[] {
  return useMemo(() => {
    if (!traceData) return [];

    const timeScale = BASE_TIME_SCALE * zoomScale;

    // Group using a nested Map: nodeId -> clock -> events (W6 fix: no string key parsing)
    const groupMap = new Map<number, Map<number, TraceEvent[]>>();

    traceData.trace.forEach(evt => {
      if (evt.clock > currentClock) return;

      const ownerId = isReceiveEvent(evt) ? evt.target : evt.source;
      const clock = evt.clock;

      let clockMap = groupMap.get(ownerId);
      if (!clockMap) {
        clockMap = new Map<number, TraceEvent[]>();
        groupMap.set(ownerId, clockMap);
      }

      let events = clockMap.get(clock);
      if (!events) {
        events = [];
        clockMap.set(clock, events);
      }

      events.push(evt);
    });

    // Flatten into EventGroup[]
    const result: EventGroup[] = [];

    groupMap.forEach((clockMap, ownerId) => {
      const node = nodes.find(n => n.id === ownerId);
      if (!node) return;

      clockMap.forEach((events, clock) => {
        result.push({
          key: `${ownerId}-${clock}`,
          ownerId,
          clock,
          x: PADDING_X + clock * timeScale,
          y: node.y,
          events,
        });
      });
    });

    return result;
  }, [traceData, currentClock, nodes, zoomScale]);
}
