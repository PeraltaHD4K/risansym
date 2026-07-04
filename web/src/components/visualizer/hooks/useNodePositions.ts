import { useMemo } from 'react';
import type { TraceOutput, NodePosition } from '@/lib/schema';
import { PADDING_Y, NODE_HEIGHT } from '../constants';

/**
 * Computes Y-positions for each unique node found in the trace data.
 * Extracts nodes from all trace events (source + target), deduplicates, and sorts by id.
 */
export function useNodePositions(traceData: TraceOutput | null): NodePosition[] {
  return useMemo(() => {
    if (!traceData) return [];

    const nodeSet = new Set<number>();
    traceData.trace.forEach(event => {
      nodeSet.add(event.source);
      if ('target' in event) {
        nodeSet.add(event.target as number);
      }
    });

    return Array.from(nodeSet)
      .sort((a, b) => a - b)
      .map((id, index) => ({
        id,
        y: PADDING_Y + index * NODE_HEIGHT,
      }));
  }, [traceData]);
}
