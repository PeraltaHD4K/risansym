import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useMessageArrows } from './useMessageArrows';
import type { TraceOutput, NodePosition, TraceEvent } from '@/lib/schema';

describe('useMessageArrows', () => {
  const mockTraceData: TraceOutput = {
    metadata: {
      schema_version: '1.0',
      algorithm: 'test',
      topology: 'test',
      execution_date: '2023-01-01T00:00:00Z',
      parameters: { total_nodes: 2 },
      metrics: {},
      capture: { max_events: 100, recorded_events: 3, dropped_events: 0, truncated: false }
    },
    trace: [
      { action: 'TRANSMIT', source: 1, target: 2, clock: 1.0, event_time: 2.0, name: 'MSG_A', payload: {} },
      { action: 'TRANSMIT', source: 2, target: 1, clock: 1.5, event_time: 3.0, name: 'MSG_B', payload: {} },
      { action: 'RECEIVE', source: 1, target: 2, clock: 2.0, name: 'MSG_A', payload: {} }
    ] as TraceEvent[]
  };

  const mockNodes: NodePosition[] = [
    { id: 1, y: 100 },
    { id: 2, y: 200 }
  ];

  it('computes arrow geometries for TRANSMIT events', () => {
    const { result } = renderHook(() => useMessageArrows(mockTraceData, mockNodes, 1));

    // Only TRANSMIT events should generate arrows
    expect(result.current).toHaveLength(2);
    
    // First message (node 1 -> 2)
    expect(result.current[0].name).toBe('MSG_A');
    expect(result.current[0].startY).toBe(100);
    expect(result.current[0].endY).toBe(200);
    
    // Second message (node 2 -> 1)
    expect(result.current[1].name).toBe('MSG_B');
    expect(result.current[1].startY).toBe(200);
    expect(result.current[1].endY).toBe(100);

    // Should assign different colors if available
    expect(result.current[0].color).not.toBe(result.current[1].color);
  });

  it('returns empty array when traceData is null', () => {
    const { result } = renderHook(() => useMessageArrows(null, mockNodes, 1));
    expect(result.current).toEqual([]);
  });
});
