/**
 * Simplified ensure-deps for Hermes MCP (no better-sqlite3 - uses fallback)
 */

import { existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "..");

export async function ensureDeps() {
  // No better-sqlite3 available - skip native deps
  // The server will gracefully handle missing DB by using fallbacks
  return;
}

export function ensureNativeCompat(pluginRoot) {
  return;
}

export function codesignBinary(binaryPath) {
  return;
}

// Auto-run
await ensureDeps();
ensureNativeCompat(root);
