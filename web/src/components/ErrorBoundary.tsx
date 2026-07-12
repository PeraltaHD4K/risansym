'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import styles from './ErrorBoundary.module.css';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in visualizer:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorContainer}>
          <AlertTriangle size={48} className={styles.icon} />
          <h2>Algo salió mal en el visualizador</h2>
          <p>
            El archivo de traza podría tener un formato inesperado o valores inválidos.
          </p>
          <pre className={styles.errorDetails}>
            {this.state.error?.message}
          </pre>
          <button 
            className="premium-button"
            onClick={() => window.location.reload()}
          >
            Reiniciar Aplicación
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
