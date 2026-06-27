import { z } from 'zod';

const TransmitEventSchema = z.object({
  action: z.literal('TRANSMIT'),
  clock: z.number(),
  event_time: z.number(),
  source: z.number(),
  target: z.number(),
  name: z.string(),
  payload: z.any()
});

const ReceiveEventSchema = z.object({
  action: z.literal('RECEIVE'),
  clock: z.number(),
  source: z.number(),
  target: z.number(),
  name: z.string(),
  payload: z.any()
});

const AppLogEventSchema = z.object({
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
  tag: z.string().nullable(),
  execution_date: z.string(),
  parameters: z.record(z.any()),
  metrics: z.record(z.any())
});

export const TraceOutputSchema = z.object({
  metadata: TraceMetadataSchema,
  trace: z.array(TraceEventSchema)
});

// Inferir tipos de TypeScript a partir de Zod
export type TraceEvent = z.infer<typeof TraceEventSchema>;
export type TraceMetadata = z.infer<typeof TraceMetadataSchema>;
export type TraceOutput = z.infer<typeof TraceOutputSchema>;
