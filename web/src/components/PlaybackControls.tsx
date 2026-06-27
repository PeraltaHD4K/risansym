'use client'

import { Play, Pause, SkipBack, SkipForward, ZoomIn, ZoomOut } from 'lucide-react';
import { useSimulation } from '@/lib/SimulationContext';
import styles from './PlaybackControls.module.css';
import { useEffect, useRef } from 'react';

export default function PlaybackControls() {
  const { 
    traceData, 
    currentClock, 
    setCurrentClock, 
    isPlaying, 
    setIsPlaying, 
    playbackSpeed,
    maxTime,
    zoomScale,
    setZoomScale
  } = useSimulation();
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isPlaying && currentClock < maxTime) {
      timerRef.current = setInterval(() => {
        setCurrentClock((prev: number) => {
          const next = prev + (0.5 * playbackSpeed);
          if (next >= maxTime) {
            setIsPlaying(false);
            return maxTime;
          }
          return next;
        });
      }, 100);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, currentClock, maxTime, playbackSpeed, setCurrentClock, setIsPlaying]);

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
          {isPlaying ? <Pause size={24} /> : <Play size={24} style={{ marginLeft: '4px' }} />}
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
