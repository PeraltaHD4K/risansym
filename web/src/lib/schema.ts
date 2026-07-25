import { z } from 'zod';

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

const JsonValueSchema: z.ZodType<JsonValue> = z.lazy(() =>
  z.union([
    z.string(),
    z.number().finite(),
    z.boolean(),
    z.null(),
    z.array(JsonValueSchema),
    z.record(z.string(), JsonValueSchema)
  ])
);

const JsonObjectSchema = z.record(z.string(), JsonValueSchema);
const NodeIdSchema = z.number().int().positive();

export const TransmitEventSchema = z.strictObject({
  action: z.literal('TRANSMIT'),
  clock: z.number().finite().nonnegative(),
  event_time: z.number().finite().nonnegative(),
  source: NodeIdSchema,
  target: NodeIdSchema,
  name: z.string().min(1),
  payload: JsonObjectSchema,
  node_state: JsonObjectSchema.nullable().optional()
}).refine(event => event.event_time >= event.clock, {
  message: 'event_time cannot be earlier than clock',
  path: ['event_time']
});

export const ReceiveEventSchema = z.strictObject({
  action: z.literal('RECEIVE'),
  clock: z.number().finite().nonnegative(),
  source: NodeIdSchema,
  target: NodeIdSchema,
  name: z.string().min(1),
  payload: JsonObjectSchema,
  node_state: JsonObjectSchema.nullable().optional()
});

export const AppLogEventSchema = z.strictObject({
  action: z.literal('APP_LOG'),
  clock: z.number().finite().nonnegative(),
  source: NodeIdSchema,
  message: z.string().min(1)
});

export const TraceEventSchema = z.discriminatedUnion('action', [
  TransmitEventSchema,
  ReceiveEventSchema,
  AppLogEventSchema
]);

export const TraceCaptureSchema = z.strictObject({
  max_events: z.number().int().positive().max(1000000),
  recorded_events: z.number().int().nonnegative(),
  dropped_events: z.number().int().nonnegative(),
  truncated: z.boolean()
}).refine(capture => capture.truncated === (capture.dropped_events > 0), {
  message: 'truncated must match dropped_events',
  path: ['truncated']
});

export const TraceMetadataSchema = z.strictObject({
  schema_version: z.literal('1.0'),
  algorithm: z.string().min(1),
  topology: z.string().min(1),
  tag: z.string().nullable().optional(),
  execution_date: z.iso.datetime({ offset: true }),
  parameters: JsonObjectSchema,
  metrics: JsonObjectSchema,
  capture: TraceCaptureSchema
});

export const TraceOutputSchema = z.strictObject({
  metadata: TraceMetadataSchema,
  trace: z.array(TraceEventSchema).max(1000000)
}).refine(output => output.trace.length === output.metadata.capture.recorded_events, {
  message: 'recorded_events must equal trace length',
  path: ['metadata', 'capture', 'recorded_events']
});

// Inferir tipos de TypeScript a partir de Zod
export type TransmitEvent = z.infer<typeof TransmitEventSchema>;
export type ReceiveEvent = z.infer<typeof ReceiveEventSchema>;
export type AppLogEvent = z.infer<typeof AppLogEventSchema>;
export type TraceEvent = z.infer<typeof TraceEventSchema>;
export type TraceMetadata = z.infer<typeof TraceMetadataSchema>;
export type TraceCapture = z.infer<typeof TraceCaptureSchema>;
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
  cx: number;
  cy: number;
  staticPathD: string;
  clock: number;
  eventTime: number;
  payload: Record<string, unknown>;
}

export interface NodePosition {
  id: number;
  y: number;
}
