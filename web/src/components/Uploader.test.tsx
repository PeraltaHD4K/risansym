import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Uploader from './Uploader';
import { useTrace } from '@/lib/TraceContext';
import { usePlayback } from '@/lib/PlaybackContext';

vi.mock('@/lib/TraceContext', () => ({
  useTrace: vi.fn(),
}));

vi.mock('@/lib/PlaybackContext', () => ({
  usePlayback: vi.fn(),
}));

describe('Uploader', () => {
  const mockSetTraceData = vi.fn();
  const mockSetCurrentClock = vi.fn();
  const mockSetIsPlaying = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useTrace as any).mockReturnValue({ setTraceData: mockSetTraceData });
    (usePlayback as any).mockReturnValue({
      setCurrentClock: mockSetCurrentClock,
      setIsPlaying: mockSetIsPlaying,
    });
  });

  it('renders default state correctly', () => {
    render(<Uploader />);
    expect(screen.getByText('Sube tu archivo traza.json')).toBeDefined();
  });

  it('processes file using FileReader', async () => {
    const mockFileReader = {
      readAsText: vi.fn(),
      onload: null as any,
      onerror: null as any,
    };
    class MockFileReader {
      readAsText = mockFileReader.readAsText;
      set onload(val: any) { mockFileReader.onload = val; }
      set onerror(val: any) { mockFileReader.onerror = val; }
    }
    window.FileReader = MockFileReader as any;

    render(<Uploader />);
    
    // Simulate drop
    const dropzone = screen.getByRole('button');
    const file = new File(['{"valid":"json"}'], 'trace.json', { type: 'application/json' });
    
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] },
    });

    expect(mockFileReader.readAsText).toHaveBeenCalledWith(file);
    
    // Simulate successful read
    mockFileReader.onload({ target: { result: 'invalid json content' } });
    
    // It should handle JSON parse error silently inside catch and call setError
    expect(await screen.findByText(/Error de Validación/i)).toBeDefined();
    expect(mockSetTraceData).toHaveBeenCalledWith(null);
  });
});
