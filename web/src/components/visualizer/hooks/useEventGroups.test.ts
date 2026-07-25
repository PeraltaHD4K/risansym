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
      execution_date: '2023-01-01T00:00:00Z',
      parameters: { total_nodes: 2 },
      metrics: {},
      capture: { max_events: 100, recorded_events: 3, dropped_events: 0, truncated: false }
    },
    trace: [
      { action: 'TRANSMIT', source: 1, target: 2, clock: 1.0, event_time: 2.0, name: 'MSG_1', payload: {} },
      { action: 'RECEIVE', source: 1, target: 2, clock: 2.0, name: 'MSG_1', payload: {} },
      { action: 'APP_LOG', source: 2, clock: 2.0, message: 'COMP_1' }
    ] as TraceEvent[]
  };

  const mockNodes: NodePosition[] = [
    { id: 1, y: 100 },
    { id: 2, y: 200 }
  ];

  it('groups events by node and clock correctly', () => {
    // With currentClock = 1.0, only the first event should be included
    const { result, rerender } = renderHook(
      ({ clock }) => useEventGroups(mockTraceData, clock, mockNodes, 1),
      { initialProps: { clock: 1.0 } }
    );

    expect(result.current).toHaveLength(1);
    expect(result.current[0].ownerId).toBe(1); // source of TRANSMIT
    expect(result.current[0].clock).toBe(1.0);
    expect(result.current[0].events).toHaveLength(1);

    // With currentClock = 2.0, all groups should be included
    rerender({ clock: 2.0 });

    expect(result.current).toHaveLength(2); // (node 1, clock 1) and (node 2, clock 2)
    
    const node2Group = result.current.find(g => g.ownerId === 2 && g.clock === 2.0);
    expect(node2Group).toBeDefined();
    // RECEIVE (target: 2) and APP_LOG (source: 2) both map to ownerId = 2
    expect(node2Group?.events).toHaveLength(2);
  });

  it('returns empty array when traceData is null', () => {
    const { result } = renderHook(() => useEventGroups(null, 10, mockNodes, 1));
    expect(result.current).toEqual([]);
  });
});
