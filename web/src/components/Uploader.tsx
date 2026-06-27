'use client'

import { useState } from 'react';
import { UploadCloud, CheckCircle, AlertTriangle } from 'lucide-react';
import { useSimulation } from '@/lib/SimulationContext';
import { TraceOutputSchema } from '@/lib/schema';
import styles from './Uploader.module.css';

export default function Uploader() {
  const { setTraceData, setCurrentClock, setIsPlaying } = useSimulation();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [isDragging, setIsDragging] = useState(false);

  const processFile = (file: File) => {
    setError(null);
    setSuccess(false);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const rawJson = JSON.parse(text);
        
        // Zod validation (Contrato de Datos)
        const parsedData = TraceOutputSchema.parse(rawJson);
        
        setTraceData(parsedData);
        setCurrentClock(0);
        setIsPlaying(false);
        setSuccess(true);
      } catch (err: any) {
        console.error("Zod Validation Error:", err);
        setError("El archivo no cumple con el esquema V1.0 (Zod Validation Failed).");
        setTraceData(null);
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div 
      className={`${styles.uploadBox} ${isDragging ? styles.dragging : ''} ${error ? styles.errorBox : ''} ${success ? styles.successBox : ''}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => document.getElementById('fileUpload')?.click()}
    >
      <input 
        id="fileUpload" 
        type="file" 
        accept=".json" 
        style={{ display: 'none' }} 
        onChange={(e) => e.target.files && processFile(e.target.files[0])} 
      />
      
      {error ? (
        <AlertTriangle className={styles.iconError} />
      ) : success ? (
        <CheckCircle className={styles.iconSuccess} />
      ) : (
        <UploadCloud className={styles.icon} />
      )}
      
      <h3 style={{ marginBottom: '8px' }}>
        {error ? "Error de Validación" : success ? "Traza Cargada" : "Sube tu archivo traza.json"}
      </h3>
      
      <p className={styles.description}>
        {error ? error : success ? "El simulador está listo para reproducir." : "Arrastra y suelta aquí el archivo JSON generado por tu simulación en Python."}
      </p>
    </div>
  );
}
