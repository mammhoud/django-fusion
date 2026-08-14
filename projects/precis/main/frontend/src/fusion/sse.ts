/**
 * SSE binding — precis.
 *
 * Re-exports the shared SSE client for app code (live progress, event
 * streams from fusion `SSEMixin` endpoints). No stream is opened unless
 * a component calls `createSSEClient`.
 */
export { createSSEClient } from '@fusion/modules/sse';
export type { SSEClient, SSEClientOptions, SSEHandlers } from '@fusion/modules/sse';
