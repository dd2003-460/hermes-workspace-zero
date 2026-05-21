// cache-heal-utils.mjs stub - Hooks are Claude Code specific, not needed for Hermes MCP

export function extractNodePath(cmd) { return null; }
export function isStaleNodePath(cmd) { return false; }
export function buildHookCommand({ scriptPath, platform, nodePath }) { return `"${scriptPath}"`; }
export function selfHealCacheHealHook({ settingsPath, scriptPath, platform, nodePath }) { return "noop"; }
export function ensureShebangAndExecBit(scriptPath) { return; }
