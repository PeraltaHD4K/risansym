'use client'

import { createContext, useContext, useState, type ReactNode, type Dispatch, type SetStateAction } from 'react';
import type { TraceOutput } from './schema';

interface TraceContextType {
  traceData: TraceOutput | null;
  setTraceData: Dispatch<SetStateAction<TraceOutput | null>>;
}

const TraceContext = createContext<TraceContextType | null>(null);

export function TraceProvider({ children }: { children: ReactNode }) {
  const [traceData, setTraceData] = useState<TraceOutput | null>(null);

  return (
    <TraceContext.Provider value={{ traceData, setTraceData }}>
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
