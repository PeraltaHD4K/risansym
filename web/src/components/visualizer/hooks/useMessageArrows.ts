import { useMemo } from 'react';
import type { TraceOutput, NodePosition, ComputedMessage } from '@/lib/schema';
import { isTransmitEvent } from '@/lib/schema';
import { PADDING_X, MESSAGE_COLORS, BASE_TIME_SCALE } from '../constants';

/**
 * Computes arrow geometries from trace data for message visualization.
 * Filters TRANSMIT events, assigns colors by message name, and computes SVG coordinates.
 */
export function useMessageArrows(
  traceData: TraceOutput | null,
  nodes: NodePosition[],
  zoomScale: number
): ComputedMessage[] {
  return useMemo(() => {
    if (!traceData) return [];

    const timeScale = BASE_TIME_SCALE * zoomScale;

    // Assign fixed colors to common message types to distinguish them
    const typeColorMap = new Map<string, string>();
    let colorIndex = 0;

    const results: ComputedMessage[] = [];
    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    traceData.trace.forEach((event, index) => {
      if (!isTransmitEvent(event)) return;

      const srcNode = nodeMap.get(event.source);
      const dstNode = nodeMap.get(event.target);
      if (!srcNode || !dstNode) return;

      if (!typeColorMap.has(event.name)) {
        typeColorMap.set(event.name, MESSAGE_COLORS[colorIndex % MESSAGE_COLORS.length]);
        colorIndex++;
      }

      const startX = PADDING_X + event.clock * timeScale;
      const endX = PADDING_X + event.event_time * timeScale;

      results.push({
        originalEvent: event,
        id: `${index}-${event.source}-${event.target}-${event.clock}-${event.name}`,
        name: event.name,
        color: typeColorMap.get(event.name) ?? MESSAGE_COLORS[0],
        startX,
        startY: srcNode.y,
        endX,
        endY: dstNode.y,
        clock: event.clock,
        eventTime: event.event_time,
        payload: event.payload,
      });
    });

    return results;
  }, [traceData, nodes, zoomScale]);
}
