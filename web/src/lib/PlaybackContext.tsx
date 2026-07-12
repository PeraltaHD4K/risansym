'use client'

import { createContext, useContext, useState, useMemo, type ReactNode, type Dispatch, type SetStateAction } from 'react';
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

  const maxTime = useMemo(() => {
    const fromParams = Number(traceData?.metadata?.parameters?.max_time ?? 0);
    if (fromParams > 0) return fromParams;
    // Fallback: derive from trace events when metadata doesn't include max_time
    if (!traceData?.trace?.length) return 0;
    return Math.max(...traceData.trace.map(e =>
      'event_time' in e ? Number(e.event_time ?? e.clock) : e.clock
    ));
  }, [traceData]);

  const value = useMemo(() => ({
    currentClock,
    setCurrentClock,
    isPlaying,
    setIsPlaying,
    playbackSpeed,
    setPlaybackSpeed,
    maxTime,
    zoomScale,
    setZoomScale,
  }), [currentClock, isPlaying, playbackSpeed, maxTime, zoomScale]);

  return (
    <PlaybackContext.Provider value={value}>
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
