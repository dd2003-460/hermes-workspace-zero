#!/usr/bin/env node
import { execSync } from "node:child_process";
import { existsSync, chmodSync, readFileSync, writeFileSync, readdirSync, symlinkSync, mkdirSync, lstatSync, unlinkSync } from "node:fs";
import { dirname, resolve, join, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const originalCwd = process.cwd();
process.chdir(__dirname);

// Plugin-install-path guard
const isPluginInstallPath = (p) =>
  /[/\\]\\.claude[/\\]plugins[/\\](cache|marketplaces)[/\\]/.test(p);
const safeOriginalCwd = isPluginInstallPath(originalCwd) ? null : originalCwd;

if (!process.env.CLAUDE_PROJECT_DIR && safeOriginalCwd) {
  process.env.CLAUDE_PROJECT_DIR = safeOriginalCwd;
}

if (!process.env.CONTEXT_MODE_PROJECT_DIR && safeOriginalCwd) {
  process.env.CONTEXT_MODE_PROJECT_DIR = safeOriginalCwd;
}

// ── Self-heal Layer 1: Fix registry → symlink mismatches ──
const cacheMatch = __dirname.match(
  /^(.*[\\/\\]plugins[\\/\\]cache[\\/\\][^\\/\\]+[\\/\\][^\\/\\]+[\\/\\])([^\\/\\]+)$/,
);
if (cacheMatch) {
  try {
    const cacheParent = cacheMatch[1];
    const myVersion = cacheMatch[2];
    const ipPath = resolve(homedir(), ".claude", "plugins", "installed_plugins.json");

    const dirs = readdirSync(cacheParent).filter((d) =>
      /^\d+\.\d+\.\d+/.test(d),
    );
    if (dirs.length > 1) {
      dirs.sort((a, b) => {
        const pa = a.split(".").map(Number);
        const pb = b.split(".").map(Number);
        for (let i = 0; i < 3; i++) {
          if ((pa[i] ?? 0) !== (pb[i] ?? 0))
            return (pa[i] ?? 0) - (pb[i] ?? 0);
        }
        return 0;
      });
      const newest = dirs[dirs.length - 1];
      if (newest && newest !== myVersion) {
        const ip = JSON.parse(readFileSync(ipPath, "utf-8"));
        for (const [key, entries] of Object.entries(ip.plugins || {})) {
          if (key !== "context-mode@context-mode") continue;
          for (const entry of entries) {
            entry.installPath = resolve(cacheParent, newest);
            entry.version = newest;
            entry.lastUpdated = new Date().toISOString();
          }
        }
        writeFileSync(ipPath, JSON.stringify(ip, null, 2) + "\n", "utf-8");
      }
    }

    const cacheRoot = resolve(homedir(), ".claude", "plugins", "cache");
    if (existsSync(ipPath)) {
      const ip = JSON.parse(readFileSync(ipPath, "utf-8"));
      for (const [key, entries] of Object.entries(ip.plugins || {})) {
        if (key !== "context-mode@context-mode") continue;
        for (const entry of entries) {
          const rp = entry.installPath;
          if (!rp || existsSync(rp) || rp === __dirname) continue;
          if (!resolve(rp).startsWith(cacheRoot + sep)) continue;
          try {
            try { if (lstatSync(rp).isSymbolicLink()) unlinkSync(rp); } catch {}
            const rpParent = dirname(rp);
            if (!existsSync(rpParent)) mkdirSync(rpParent, { recursive: true });
            symlinkSync(__dirname, rp, process.platform === "win32" ? "junction" : undefined);
          } catch { /* best effort */ }
        }
      }
    }
  } catch {
    /* best effort */
  }
}

// Self-heal layers for installed_plugins.json
try {
  const { healInstalledPlugins, healSettingsEnabledPlugins, healPluginJsonMcpServers, healMcpJsonArgs } =
    await import("./scripts/heal-installed-plugins.mjs");
  const pluginKey = "context-mode@context-mode";
  const registryPath = resolve(homedir(), ".claude", "plugins", "installed_plugins.json");
  const settingsPath = resolve(homedir(), ".claude", "settings.json");
  try { healInstalledPlugins({ registryPath, pluginCacheRoot: resolve(homedir(), ".claude", "plugins", "cache"), pluginKey }); }
  catch { /* best effort */ }
  try { healSettingsEnabledPlugins({ settingsPath, pluginKey }); }
  catch { /* best effort */ }
  try {
    if (existsSync(registryPath)) {
      const ip = JSON.parse(readFileSync(registryPath, "utf-8"));
      const entries = (ip && ip.plugins && ip.plugins[pluginKey]) || [];
      if (Array.isArray(entries)) {
        for (const entry of entries) {
          const installPath = entry && entry.installPath;
          if (typeof installPath !== "string" || !installPath) continue;
          try { healPluginJsonMcpServers({ pluginRoot: installPath, pluginCacheRoot: resolve(homedir(), ".claude", "plugins", "cache"), pluginKey }); } catch {}
          try { healMcpJsonArgs({ pluginRoot: installPath, pluginCacheRoot: resolve(homedir(), ".claude", "plugins", "cache"), pluginKey }); } catch {}
        }
      }
    }
  } catch { /* best effort */ }
} catch { /* best effort */ }

// Hooks and normalize hooks
try {
  const { buildHookCommand, selfHealCacheHealHook, ensureShebangAndExecBit } =
    await import("./hooks/cache-heal-utils.mjs");
  const globalHooksDir = resolve(homedir(), ".claude", "hooks");
  const healHookPath = resolve(globalHooksDir, "context-mode-cache-heal.mjs");
  const oldBashHook = resolve(globalHooksDir, "context-mode-cache-heal.sh");
  if (existsSync(oldBashHook)) {
    try { unlinkSync(oldBashHook); } catch {}
  }
  if (!existsSync(healHookPath)) {
    if (!existsSync(globalHooksDir)) mkdirSync(globalHooksDir, { recursive: true });
    const healScript = `#!/usr/bin/env node
import{existsSync,readdirSync,statSync,symlinkSync,lstatSync,unlinkSync,readFileSync}from"node:fs";
import{dirname,join,resolve,sep}from"node:path";
import{homedir}from"node:os";
try{
  const f=resolve(homedir(),".claude","plugins","installed_plugins.json");
  if(!existsSync(f))process.exit(0);
  const cacheRoot=resolve(homedir(),".claude","plugins","cache");
  const ip=JSON.parse(readFileSync(f,"utf-8"));
  for(const[k,es]of Object.entries(ip.plugins||{})){
    if(k!=="context-mode@context-mode")continue;
    for(const e of es){
      const p=e.installPath;
      if(!p||existsSync(p))continue;
      if(!resolve(p).startsWith(cacheRoot+sep))continue;
      const parent=dirname(p);
      if(!existsSync(parent))continue;
      try{if(lstatSync(p).isSymbolicLink())unlinkSync(p)}catch{}
      const dirs=readdirSync(parent).filter(d=>/^\\d+\\d/.test(d)&&statSync(join(parent,d)).isDirectory());
      if(!dirs.length)continue;
      dirs.sort((a,b)=>{const pa=a.split(".").map(Number),pb=b.split(".").map(Number);for(let i=0;i<3;i++){if((pa[i]||0)!==(pb[i]||0))return(pa[i]||0)-(pb[i]||0)}return 0});
      try{symlinkSync(join(parent,dirs[dirs.length-1]),p,process.platform==="win32"?"junction":undefined)}catch{}
    }
  }
}catch{}
`;
    writeFileSync(healHookPath, healScript, { mode: 0o755 });
  }
  if (process.platform !== "win32") {
    try { ensureShebangAndExecBit(healHookPath); } catch {}
  }
} catch { /* best effort */ }

try {
  if (!process.env.VITEST) {
    const { normalizeHooksOnStartup } = await import("./hooks/normalize-hooks.mjs");
    normalizeHooksOnStartup({
      pluginRoot: __dirname,
      nodePath: process.execPath,
      platform: process.platform,
    });
  }
} catch { /* best effort */ }

import "./hooks/ensure-deps.mjs";
for (const pkg of ["turndown", "turndown-plugin-gfm", "@mixmark-io/domino"]) {
  if (!existsSync(resolve(__dirname, "node_modules", pkg))) {
    try {
      execSync(`npm install ${pkg} --no-package-lock --no-save --silent`, {
        cwd: __dirname,
        stdio: "pipe",
        timeout: 120000,
      });
    } catch { /* best effort */ }
  }
}

if (!existsSync(resolve(__dirname, "cli.bundle.mjs")) && existsSync(resolve(__dirname, "build", "cli.js"))) {
  const shimPath = resolve(__dirname, "cli.bundle.mjs");
  writeFileSync(shimPath, '#!/usr/bin/env node\nawait import("./build/cli.js");\n');
  if (process.platform !== "win32") chmodSync(shimPath, 0o755);
}

if (existsSync(resolve(__dirname, "server.bundle.mjs"))) {
  await import("./server.bundle.mjs");
} else {
  if (!existsSync(resolve(__dirname, "node_modules"))) {
    try {
      execSync("npm install --silent", { cwd: __dirname, stdio: "pipe", timeout: 60000 });
    } catch { /* best effort */ }
  }
  if (!existsSync(resolve(__dirname, "build", "server.js"))) {
    try {
      execSync("npx tsc --silent", { cwd: __dirname, stdio: "pipe", timeout: 30000 });
    } catch { /* best effort */ }
  }
  await import("./build/server.js");
}
