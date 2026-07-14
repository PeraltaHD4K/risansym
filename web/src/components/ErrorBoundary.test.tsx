import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary';

// Silence console.error for expected test errors
const originalError = console.error;
vi.spyOn(console, 'error').mockImplementation((...args) => {
  if (typeof args[0] === 'string' && args[0].includes('React will try to recreate this component tree from scratch')) {
    return;
  }
  originalError(...args);
});

const ErrorThrowingComponent = () => {
  throw new Error('Test component error');
};

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>All good</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('All good')).toBeDefined();
  });

  it('catches error and displays fallback UI', () => {
    render(
      <ErrorBoundary>
        <ErrorThrowingComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText(/Algo salió mal/i)).toBeDefined();
    expect(screen.getByText('Test component error')).toBeDefined();
  });
});
