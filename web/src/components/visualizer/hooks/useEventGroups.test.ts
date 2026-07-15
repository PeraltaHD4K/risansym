import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useEventGroups } from './useEventGroups';
import type { TraceOutput, NodePosition, TraceEvent } from '@/lib/schema';

describe('useEventGroups', () => {
  const mockTraceData: TraceOutput = {
    metadata: {
      schema_version: '1.0',
      algorithm: 'test',
      topology: 'test',
      execution_date: '2023-01-01',
      parameters: { total_nodes: 2 },
      metrics: {}
    },
    trace: [
      { action: 'TRANSMIT', source: 0, target: 1, clock: 1.0, event_time: 2.0, name: 'MSG_1', payload: {} },
      { action: 'RECEIVE', source: 0, target: 1, clock: 2.0, event_time: 2.0, name: 'MSG_1', payload: {} },
      { action: 'APP_LOG', source: 1, clock: 2.0, message: 'COMP_1' }
    ] as TraceEvent[]
  };

  const mockNodes: NodePosition[] = [
    { id: 0, y: 100 },
    { id: 1, y: 200 }
  ];

  it('groups events by node and clock correctly', () => {
    // With currentClock = 1.0, only the first event should be included
    const { result, rerender } = renderHook(
      ({ clock }) => useEventGroups(mockTraceData, clock, mockNodes, 1),
      { initialProps: { clock: 1.0 } }
    );

    expect(result.current).toHaveLength(1);
    expect(result.current[0].ownerId).toBe(0); // source of TRANSMIT
    expect(result.current[0].clock).toBe(1.0);
    expect(result.current[0].events).toHaveLength(1);

    // With currentClock = 2.0, all groups should be included
    rerender({ clock: 2.0 });

    expect(result.current).toHaveLength(2); // (node 0, clock 1) and (node 1, clock 2)
    
    const node1Group = result.current.find(g => g.ownerId === 1 && g.clock === 2.0);
    expect(node1Group).toBeDefined();
    // RECEIVE (target: 1) and COMPUTE (source: 1) both map to ownerId = 1
    expect(node1Group?.events).toHaveLength(2);
  });

  it('returns empty array when traceData is null', () => {
    const { result } = renderHook(() => useEventGroups(null, 10, mockNodes, 1));
    expect(result.current).toEqual([]);
  });
});
