import type { NoteStep } from '../types';

/** Parse a notes `steps` JSON string into a list of steps (title + details). */
export function parseNoteSteps(stepsJson?: string | null): NoteStep[] {
  if (!stepsJson) return [];
  try {
    const parsed = JSON.parse(stepsJson);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .map(s => (typeof s === 'string' ? { title: s } : s))
      .filter((s: Partial<NoteStep>) => s && typeof s.title === 'string')
      .map((s: Partial<NoteStep>) => ({ title: s.title!, details: typeof s.details === 'string' ? s.details : undefined }));
  } catch {
    return [];
  }
}

/** Serialize a list of steps into the `steps` JSON string (or null when empty). */
export function serializeNoteSteps(steps: NoteStep[]): string | null {
  if (!steps || steps.length === 0) return null;
  return JSON.stringify(
    steps.map(s => ({ title: s.title.trim(), details: s.details?.trim() || undefined })).filter(s => s.title),
  );
}
