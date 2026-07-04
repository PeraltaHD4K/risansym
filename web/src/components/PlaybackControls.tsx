'use client'

import { Play, Pause, SkipBack, SkipForward, ZoomIn, ZoomOut } from 'lucide-react';
import { useTrace } from '@/lib/TraceContext';
import { usePlayback } from '@/lib/PlaybackContext';
import styles from './PlaybackControls.module.css';
import { useEffect, useRef, useCallback } from 'react';

export default function PlaybackControls() {
  const { traceData } = useTrace();
  const { 
    currentClock, 
    setCurrentClock, 
    isPlaying, 
    setIsPlaying, 
    playbackSpeed,
    maxTime,
    zoomScale,
    setZoomScale
  } = usePlayback();
  
  const rafRef = useRef<number | null>(null);
  const lastTimestampRef = useRef<number | null>(null);

  const animate = useCallback((timestamp: number) => {
    if (lastTimestampRef.current === null) {
      lastTimestampRef.current = timestamp;
      rafRef.current = requestAnimationFrame(animate);
      return;
    }

    const deltaSeconds = (timestamp - lastTimestampRef.current) / 1000;
    lastTimestampRef.current = timestamp;

    setCurrentClock((prev: number) => {
      const next = prev + deltaSeconds * playbackSpeed;
      if (next >= maxTime) {
        setIsPlaying(false);
        return maxTime;
      }
      return next;
    });

    rafRef.current = requestAnimationFrame(animate);
  }, [playbackSpeed, maxTime, setCurrentClock, setIsPlaying]);

  useEffect(() => {
    if (isPlaying) {
      lastTimestampRef.current = null;
      rafRef.current = requestAnimationFrame(animate);
    } else {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      lastTimestampRef.current = null;
    }

    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, [isPlaying, animate]);

  if (!traceData) return null;

  return (
    <div className={`glass-panel ${styles.controlsContainer}`}>
      <div className={styles.buttonsGroup}>
        <button className={styles.controlBtn} onClick={() => setCurrentClock(0)}>
          <SkipBack size={20} />
        </button>
        
        <button 
          className={styles.playBtn} 
          onClick={() => setIsPlaying(!isPlaying)}
        >
          {isPlaying ? <Pause size={24} /> : <Play size={24} className={styles.playIcon} />}
        </button>
        
        <button className={styles.controlBtn} onClick={() => setCurrentClock(maxTime)}>
          <SkipForward size={20} />
        </button>
      </div>

      <div className={styles.timelineWrapper}>
        <span className={styles.timeLabel}>{currentClock.toFixed(1)}s</span>
        <input 
          type="range" 
          min="0" 
          max={maxTime} 
          step="0.1"
          value={currentClock}
          onChange={(e) => {
            setIsPlaying(false);
            setCurrentClock(parseFloat(e.target.value));
          }}
          className={styles.slider}
        />
        <span className={styles.timeLabel}>{maxTime.toFixed(1)}s</span>
      </div>

      <div className={styles.zoomGroup}>
        <button className={styles.zoomBtn} onClick={() => setZoomScale(Math.max(0.5, zoomScale - 0.5))}>
          <ZoomOut size={18} />
        </button>
        <span className={styles.zoomLabel}>{Math.round(zoomScale * 100)}%</span>
        <button className={styles.zoomBtn} onClick={() => setZoomScale(Math.min(10, zoomScale + 0.5))}>
          <ZoomIn size={18} />
        </button>
      </div>
    </div>
  );
}
