import { renderHook } from '@testing-library/react';
import { expect, test, describe } from 'vitest';
import { useNodePositions } from './useNodePositions';
import type { TraceOutput } from '@/lib/schema';
import { PADDING_Y, NODE_HEIGHT } from '../constants';

describe('useNodePositions', () => {
  test('returns empty array when traceData is null', () => {
    const { result } = renderHook(() => useNodePositions(null));
    expect(result.current).toEqual([]);
  });

  test('extracts, deduplicates, and sorts nodes correctly', () => {
    const mockTrace: TraceOutput = {
      metadata: {
        schema_version: '1.0',
        algorithm: 'Test',
        topology: 'Test',
        execution_date: '2023-01-01T00:00:00Z',
        parameters: {},
        metrics: {},
        capture: { max_events: 100, recorded_events: 3, dropped_events: 0, truncated: false }
      },
      trace: [
        { action: 'TRANSMIT', source: 3, target: 1, clock: 0, event_time: 1, name: 'M1', payload: {} },
        { action: 'RECEIVE', source: 3, target: 1, clock: 1, name: 'M1', payload: {} },
        { action: 'APP_LOG', source: 2, clock: 2, message: 'test' }
      ]
    };

    const { result } = renderHook(() => useNodePositions(mockTrace));
    
    // Expect nodes 1, 2, 3 sorted
    expect(result.current).toHaveLength(3);
    
    expect(result.current[0].id).toBe(1);
    expect(result.current[0].y).toBe(PADDING_Y + 0 * NODE_HEIGHT);
    
    expect(result.current[1].id).toBe(2);
    expect(result.current[1].y).toBe(PADDING_Y + 1 * NODE_HEIGHT);
    
    expect(result.current[2].id).toBe(3);
    expect(result.current[2].y).toBe(PADDING_Y + 2 * NODE_HEIGHT);
  });
});
