'use client'

import { createContext, useContext, useState, ReactNode } from 'react';
import { TraceOutput } from './schema';

interface SimulationContextType {
  traceData: TraceOutput | null;
  setTraceData: (data: TraceOutput | null) => void;
  currentClock: number;
  setCurrentClock: (time: number) => void;
  isPlaying: boolean;
  setIsPlaying: (playing: boolean) => void;
  playbackSpeed: number;
  setPlaybackSpeed: (speed: number) => void;
  maxTime: number;
  zoomScale: number;
  setZoomScale: (scale: number) => void;
}

const SimulationContext = createContext<SimulationContextType | null>(null);

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [traceData, setTraceData] = useState<TraceOutput | null>(null);
  const [currentClock, setCurrentClock] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [zoomScale, setZoomScale] = useState<number>(1);

  // Derivamos el tiempo máximo del archivo si existe
  const maxTime = traceData?.metadata?.parameters?.max_time ?? 0;

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
