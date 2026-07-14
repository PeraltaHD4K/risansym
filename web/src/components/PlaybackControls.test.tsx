import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import PlaybackControls from './PlaybackControls';
import { useTrace } from '@/lib/TraceContext';
import { usePlayback } from '@/lib/PlaybackContext';

vi.mock('@/lib/TraceContext', () => ({
  useTrace: vi.fn(),
}));

vi.mock('@/lib/PlaybackContext', () => ({
  usePlayback: vi.fn(),
}));

vi.mock('@/lib/exportUtils', () => ({
  downloadSVG: vi.fn(),
}));

describe('PlaybackControls', () => {
  const mockSetCurrentClock = vi.fn();
  const mockSetIsPlaying = vi.fn();
  const mockSetZoomScale = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useTrace).mockReturnValue({
      traceData: { metadata: { topology: 'test-topo' } },
    });
    vi.mocked(usePlayback).mockReturnValue({
      currentClock: 1.5,
      setCurrentClock: mockSetCurrentClock,
      isPlaying: false,
      setIsPlaying: mockSetIsPlaying,
      playbackSpeed: 1,
      maxTime: 10,
      zoomScale: 1,
      setZoomScale: mockSetZoomScale,
    });
  });

  it('renders controls when traceData exists', () => {
    render(<PlaybackControls />);
    expect(screen.getByLabelText('Start playback')).toBeDefined();
    expect(screen.getByLabelText('Playback timeline')).toBeDefined();
  });

  it('returns null if traceData is missing', () => {
    vi.mocked(useTrace).mockReturnValue({ traceData: null });
    const { container } = render(<PlaybackControls />);
    expect(container.firstChild).toBeNull();
  });

  it('toggles play/pause state', () => {
    render(<PlaybackControls />);
    const playBtn = screen.getByLabelText('Start playback');
    fireEvent.click(playBtn);
    expect(mockSetIsPlaying).toHaveBeenCalledWith(true);
  });

  it('handles zoom controls', () => {
    render(<PlaybackControls />);
    const zoomIn = screen.getByLabelText('Zoom In');
    fireEvent.click(zoomIn);
    expect(mockSetZoomScale).toHaveBeenCalledWith(1.5);
  });
});
