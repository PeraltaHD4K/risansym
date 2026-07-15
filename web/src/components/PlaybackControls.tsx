'use client'

import { Play, Pause, SkipBack, SkipForward, ZoomIn, ZoomOut, Download } from 'lucide-react';
import { useTrace } from '@/lib/TraceContext';
import { usePlayback } from '@/lib/PlaybackContext';
import styles from './PlaybackControls.module.css';
import { useEffect, useRef, useCallback } from 'react';
import { downloadSVG } from '@/lib/exportUtils';

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

  const animate = useCallback(function animate(timestamp: number) {
    if (lastTimestampRef.current === null) {
      lastTimestampRef.current = timestamp;
      rafRef.current = requestAnimationFrame(animate);
      return;
    }

    const deltaSeconds = (timestamp - lastTimestampRef.current) / 1000;
    lastTimestampRef.current = timestamp;

    setCurrentClock((prev: number) => {
      const next = prev + deltaSeconds * playbackSpeed;
      return next >= maxTime ? maxTime : next;
    });

    rafRef.current = requestAnimationFrame(animate);
  }, [playbackSpeed, maxTime, setCurrentClock]);

  useEffect(() => {
    if (isPlaying && currentClock >= maxTime) {
      setIsPlaying(false);
    }
  }, [currentClock, maxTime, isPlaying, setIsPlaying]);

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

  const handleDownloadSVG = () => {
    downloadSVG(traceData?.metadata?.topology);
  };

  if (!traceData) return null;

  return (
    <div className={`glass-panel ${styles.controlsContainer}`}>
      <div className={styles.buttonsGroup}>
        <button className={styles.controlBtn} onClick={() => setCurrentClock(0)} aria-label="Rewind to start">
          <SkipBack size={20} aria-hidden="true" />
        </button>
        
        <button 
          className={styles.playBtn} 
          onClick={() => setIsPlaying(!isPlaying)}
          aria-label={isPlaying ? "Pause playback" : "Start playback"}
        >
          {isPlaying ? <Pause size={24} aria-hidden="true" /> : <Play size={24} className={styles.playIcon} aria-hidden="true" />}
        </button>
        
        <button className={styles.controlBtn} onClick={() => setCurrentClock(maxTime)} aria-label="Skip to end">
          <SkipForward size={20} aria-hidden="true" />
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
          aria-label="Playback timeline"
        />
        <span className={styles.timeLabel}>{maxTime.toFixed(1)}s</span>
      </div>

      <div className={styles.zoomGroup}>
        <button className={styles.zoomBtn} onClick={() => setZoomScale(Math.max(0.5, zoomScale - 0.5))} title="Zoom Out" aria-label="Zoom Out">
          <ZoomOut size={18} aria-hidden="true" />
        </button>
        <span className={styles.zoomLabel} aria-hidden="true">{Math.round(zoomScale * 100)}%</span>
        <button className={styles.zoomBtn} onClick={() => setZoomScale(Math.min(10, zoomScale + 0.5))} title="Zoom In" aria-label="Zoom In">
          <ZoomIn size={18} aria-hidden="true" />
        </button>
        <div style={{ width: '1px', height: '20px', background: 'var(--panel-border)', margin: '0 8px' }} aria-hidden="true" />
        <button className={styles.zoomBtn} onClick={handleDownloadSVG} title="Descargar Diagrama (SVG)" aria-label="Descargar Diagrama SVG">
          <Download size={18} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
