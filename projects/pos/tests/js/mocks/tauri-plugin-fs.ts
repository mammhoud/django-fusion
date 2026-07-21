/**
 * Mock for @tauri-apps/plugin-fs — used in vitest tests running in jsdom.
 * Provides stub functions for native file system operations.
 */

export async function readFile(_path: string): Promise<Uint8Array> {
  console.warn('[tauri-mock] fs.readFile() called — returning empty buffer in test environment');
  return new Uint8Array(0);
}

export async function readTextFile(_path: string): Promise<string> {
  console.warn('[tauri-mock] fs.readTextFile() called — returning empty string in test environment');
  return '';
}

export async function readBinaryFile(_path: string): Promise<Uint8Array> {
  return readFile(_path);
}

export async function writeFile(_path: string, _contents: string | Uint8Array): Promise<void> {
  // No-op in test environment
}

export async function writeTextFile(_path: string, _contents: string): Promise<void> {
  // No-op in test environment
}

export async function writeBinaryFile(_path: string, _contents: Uint8Array): Promise<void> {
  // No-op in test environment
}

export async function remove(_path: string): Promise<void> {
  // No-op in test environment
}

export async function exists(_path: string): Promise<boolean> {
  return false;
}

export async function mkdir(_path: string): Promise<void> {
  // No-op in test environment
}

export async function readDir(_path: string): Promise<Array<{ name: string; path: string }>> {
  return [];
}

export const BaseDirectory = {
  AppConfig: 1,
  AppData: 2,
  AppLocalData: 3,
  AppCache: 4,
  AppLog: 5,
  Audio: 6,
  Cache: 7,
  Config: 8,
  Data: 9,
  Desktop: 10,
  Document: 11,
  Download: 12,
  Executable: 13,
  Font: 14,
  Home: 15,
  LocalData: 16,
  Picture: 17,
  Public: 18,
  Resource: 19,
  Runtime: 20,
  Temp: 21,
  Template: 22,
  Video: 23,
} as const;
