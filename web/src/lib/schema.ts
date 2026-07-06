import { z } from 'zod';

export const TransmitEventSchema = z.object({
  action: z.literal('TRANSMIT'),
  clock: z.number(),
  event_time: z.number(),
  source: z.number(),
  target: z.number(),
  name: z.string(),
  payload: z.unknown(),
  node_state: z.unknown().nullable().optional()
});

export const ReceiveEventSchema = z.object({
  action: z.literal('RECEIVE'),
  clock: z.number(),
  source: z.number(),
  target: z.number(),
  name: z.string(),
  payload: z.unknown(),
  node_state: z.unknown().nullable().optional()
});

export const AppLogEventSchema = z.object({
  action: z.literal('APP_LOG'),
  clock: z.number(),
  source: z.number(),
  message: z.string()
});

export const TraceEventSchema = z.discriminatedUnion('action', [
  TransmitEventSchema,
  ReceiveEventSchema,
  AppLogEventSchema
]);

export const TraceMetadataSchema = z.object({
  schema_version: z.literal('1.0'),
  algorithm: z.string(),
  topology: z.string(),
  tag: z.string().nullable().optional(),
  execution_date: z.string(),
  parameters: z.record(z.string(), z.unknown()),
  metrics: z.record(z.string(), z.unknown())
});

export const TraceOutputSchema = z.object({
  metadata: TraceMetadataSchema,
  trace: z.array(TraceEventSchema)
});

// Inferir tipos de TypeScript a partir de Zod
export type TransmitEvent = z.infer<typeof TransmitEventSchema>;
export type ReceiveEvent = z.infer<typeof ReceiveEventSchema>;
export type AppLogEvent = z.infer<typeof AppLogEventSchema>;
export type TraceEvent = z.infer<typeof TraceEventSchema>;
export type TraceMetadata = z.infer<typeof TraceMetadataSchema>;
export type TraceOutput = z.infer<typeof TraceOutputSchema>;

// Type guards for discriminated union members
export function isTransmitEvent(event: TraceEvent): event is TransmitEvent {
  return event.action === 'TRANSMIT';
}

export function isReceiveEvent(event: TraceEvent): event is ReceiveEvent {
  return event.action === 'RECEIVE';
}

export function isAppLogEvent(event: TraceEvent): event is AppLogEvent {
  return event.action === 'APP_LOG';
}

// Utility types for the Visualizer
export interface ComputedMessage {
  originalEvent: TransmitEvent;
  id: string;
  name: string;
  color: string;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  clock: number;
  eventTime: number;
  payload: unknown;
}

export interface NodePosition {
  id: number;
  y: number;
}
