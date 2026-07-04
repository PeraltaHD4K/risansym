'use client'

import { createContext, useContext, useState, type ReactNode, type Dispatch, type SetStateAction } from 'react';
import { useTrace } from './TraceContext';

interface PlaybackContextType {
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

const PlaybackContext = createContext<PlaybackContextType | null>(null);

export function PlaybackProvider({ children }: { children: ReactNode }) {
  const { traceData } = useTrace();
  const [currentClock, setCurrentClock] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [zoomScale, setZoomScale] = useState<number>(1);

  // Derivamos el tiempo máximo del archivo si existe (Forzando casteo numérico)
  const maxTime = Number(traceData?.metadata?.parameters?.max_time ?? 0);

  return (
    <PlaybackContext.Provider
      value={{
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
    </PlaybackContext.Provider>
  );
}

export function usePlayback(): PlaybackContextType {
  const context = useContext(PlaybackContext);
  if (!context) {
    throw new Error('usePlayback must be used within a PlaybackProvider');
  }
  return context;
}
