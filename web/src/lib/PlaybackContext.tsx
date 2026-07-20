'use client'

import { createContext, use, useState, useMemo, type ReactNode, type Dispatch, type SetStateAction } from 'react';
import { useTrace } from './TraceContext';

// --- High-frequency context: only currentClock ---
interface ClockContextType {
  currentClock: number;
  setCurrentClock: Dispatch<SetStateAction<number>>;
}

const ClockContext = createContext<ClockContextType | null>(null);

// --- Low-frequency context: everything else ---
interface PlaybackApiContextType {
  isPlaying: boolean;
  setIsPlaying: Dispatch<SetStateAction<boolean>>;
  playbackSpeed: number;
  setPlaybackSpeed: Dispatch<SetStateAction<number>>;
  maxTime: number;
  zoomScale: number;
  setZoomScale: Dispatch<SetStateAction<number>>;
}

const PlaybackApiContext = createContext<PlaybackApiContextType | null>(null);

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
    return traceData.trace.reduce((max, e) => {
      const val = 'event_time' in e ? Number(e.event_time ?? e.clock) : e.clock;
      return val > max ? val : max;
    }, 0);
  }, [traceData]);

  const clockValue = useMemo(() => ({ currentClock, setCurrentClock }), [currentClock]);

  const apiValue = useMemo(() => ({
    isPlaying,
    setIsPlaying,
    playbackSpeed,
    setPlaybackSpeed,
    maxTime,
    zoomScale,
    setZoomScale,
  }), [isPlaying, playbackSpeed, maxTime, zoomScale]);

  return (
    <PlaybackApiContext value={apiValue}>
      <ClockContext value={clockValue}>
        {children}
      </ClockContext>
    </PlaybackApiContext>
  );
}

/** High-frequency hook: only subscribe to currentClock changes. */
export function useClock(): ClockContextType {
  const context = use(ClockContext);
  if (!context) {
    throw new Error('useClock must be used within a PlaybackProvider');
  }
  return context;
}

/** Low-frequency hook: subscribe to playback API (isPlaying, speed, zoom, maxTime). */
export function usePlaybackApi(): PlaybackApiContextType {
  const context = use(PlaybackApiContext);
  if (!context) {
    throw new Error('usePlaybackApi must be used within a PlaybackProvider');
  }
  return context;
}

/** Combined hook for backwards compatibility. Components using this will re-render on clock changes. */
export function usePlayback(): ClockContextType & PlaybackApiContextType {
  return { ...useClock(), ...usePlaybackApi() };
}
