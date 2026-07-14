'use client'

import { createContext, useContext, useState, useMemo, type ReactNode, type Dispatch, type SetStateAction } from 'react';
import type { TraceOutput } from './schema';

interface TraceContextType {
  traceData: TraceOutput | null;
  setTraceData: Dispatch<SetStateAction<TraceOutput | null>>;
}

const TraceContext = createContext<TraceContextType | null>(null);

export function TraceProvider({ children }: { children: ReactNode }) {
  const [traceData, setTraceData] = useState<TraceOutput | null>(null);

  const value = useMemo(() => ({ traceData, setTraceData }), [traceData]);

  return (
    <TraceContext.Provider value={value}>
      {children}
    </TraceContext.Provider>
  );
}

export function useTrace(): TraceContextType {
  const context = useContext(TraceContext);
  if (!context) {
    throw new Error('useTrace must be used within a TraceProvider');
  }
  return context;
}
