'use client'

import { createContext, useContext, useState, ReactNode, Dispatch, SetStateAction } from 'react';
import { TraceOutput } from './schema';

interface SimulationContextType {
  traceData: TraceOutput | null;
  setTraceData: Dispatch<SetStateAction<TraceOutput | null>>;
  currentClock: number;
  setCurrentClock: Dispatch<SetStateAction<number>>;
  isPlaying: boolean;
  setIsPlaying: Dispatch<SetStateAction<boolean>>;
  playbackSpeed: number;
  setPlaybackSpeed: Dispatch<SetStateAction<number>>;
  maxTime: number;
  zoomScale: number;
  setZoomScale: Dispatch<SetStateAction<number>>;
}

const SimulationContext = createContext<SimulationContextType | null>(null);

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [traceData, setTraceData] = useState<TraceOutput | null>(null);
  const [currentClock, setCurrentClock] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [zoomScale, setZoomScale] = useState<number>(1);

  // Derivamos el tiempo máximo del archivo si existe (Forzando casteo numérico)
  const maxTime = Number(traceData?.metadata?.parameters?.max_time ?? 0);

  return (
    <SimulationContext.Provider
      value={{
        traceData,
        setTraceData,
        currentClock,
        setCurrentClock,
        isPlaying,
        setIsPlaying,
        playbackSpeed,
        setPlaybackSpeed,
        maxTime,
        zoomScale,
        setZoomScale,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulation() {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
}
