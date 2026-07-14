import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useMessageArrows } from './useMessageArrows';
import type { TraceOutput, NodePosition, TraceEvent } from '@/lib/schema';

describe('useMessageArrows', () => {
  const mockTraceData: TraceOutput = {
    metadata: {
      algorithm: 'test',
      topology: 'test',
      version: '1.0',
      parameters: { total_nodes: 2 }
    },
    trace: [
      { action: 'TRANSMIT', source: 0, target: 1, clock: 1.0, event_time: 2.0, name: 'MSG_A', payload: {} },
      { action: 'TRANSMIT', source: 1, target: 0, clock: 1.5, event_time: 3.0, name: 'MSG_B', payload: {} },
      { action: 'RECEIVE', source: 0, target: 1, clock: 2.0, event_time: 2.0, name: 'MSG_A', payload: {} }
    ] as TraceEvent[]
  };

  const mockNodes: NodePosition[] = [
    { id: 0, y: 100 },
    { id: 1, y: 200 }
  ];

  it('computes arrow geometries for TRANSMIT events', () => {
    const { result } = renderHook(() => useMessageArrows(mockTraceData, mockNodes, 1));

    // Only TRANSMIT events should generate arrows
    expect(result.current).toHaveLength(2);
    
    // First message (node 0 -> 1)
    expect(result.current[0].name).toBe('MSG_A');
    expect(result.current[0].startY).toBe(100);
    expect(result.current[0].endY).toBe(200);
    
    // Second message (node 1 -> 0)
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
