'use client'

import { Play, Pause, SkipBack, SkipForward, ZoomIn, ZoomOut, Download } from 'lucide-react';
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

  const handleDownloadSVG = () => {
    const svgElement = document.getElementById('visualizer-svg');
    if (!svgElement) {
      alert("No se encontró el lienzo del visualizador.");
      return;
    }

    const clonedSvg = svgElement.cloneNode(true) as SVGSVGElement;
    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(clonedSvg);

    if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    
    // Inject styles directly so the downloaded SVG looks identical
    const styleString = `
      <style>
        :root {
          --bg-color: #0f111a;
          --panel-border: rgba(255, 255, 255, 0.2);
          --text-primary: #e2e8f0;
          --text-secondary: #94a3b8;
          --danger-color: #ef4444;
          --font-outfit: system-ui, sans-serif;
          --font-inter: system-ui, sans-serif;
        }
        svg { background-color: var(--bg-color); }
        [class*="nodeLabel"] { font-family: var(--font-outfit); font-weight: 600; fill: var(--text-primary); font-size: 14px; }
        [class*="lifeline"] { stroke: var(--panel-border); stroke-width: 1; }
        [class*="timeAxis"] { stroke: var(--text-secondary); stroke-width: 2; }
        [class*="timeTick"] { fill: var(--text-secondary); font-size: 10px; font-family: var(--font-inter); text-anchor: middle; }
        [class*="messageLabel"] { font-family: var(--font-inter); font-size: 10px; font-weight: 600; text-anchor: middle; }
        [class*="playhead"] { stroke: var(--danger-color); stroke-width: 2; stroke-dasharray: 6,4; }
      </style>
    `;
    
    source = source.replace('>', `>${styleString}`);

    const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `traza_${traceData?.metadata?.topology || 'export'}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

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
        <button className={styles.zoomBtn} onClick={() => setZoomScale(Math.max(0.5, zoomScale - 0.5))} title="Zoom Out">
          <ZoomOut size={18} />
        </button>
        <span className={styles.zoomLabel}>{Math.round(zoomScale * 100)}%</span>
        <button className={styles.zoomBtn} onClick={() => setZoomScale(Math.min(10, zoomScale + 0.5))} title="Zoom In">
          <ZoomIn size={18} />
        </button>
        <div style={{ width: '1px', height: '20px', background: 'var(--panel-border)', margin: '0 8px' }} />
        <button className={styles.zoomBtn} onClick={handleDownloadSVG} title="Descargar Diagrama (SVG)">
          <Download size={18} />
        </button>
      </div>
    </div>
  );
}
