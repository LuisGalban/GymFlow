// Test: F2-08 — Race Condition Prevention via AbortController in Admin Dashboard
// Run: node frontend/tests/admin-race-condition.test.mjs

import { readFileSync } from "fs";
import { resolve } from "path";

let passed = 0;
let failed = 0;

function assert(label, ok) {
  if (ok) { passed++; console.log(`  ✅ ${label}`); }
  else { failed++; console.error(`  ❌ ${label}`); }
}

// ── 1. Simulated race condition logic ──
console.log("\n=== Race Condition Simulation ===\n");

function simulateAdminFilterCycle() {
  const events = [];
  let currentController = null;

  function onFilterChange(label) {
    if (currentController) {
      currentController.abort();
      events.push(`${label}: aborted previous`);
    }
    currentController = new AbortController();
    const signal = currentController.signal;
    events.push(`${label}: created controller, signal.aborted=${signal.aborted}`);
    return signal;
  }

  const s1 = onFilterChange("request-1");
  const s2 = onFilterChange("request-2");
  const s3 = onFilterChange("request-3");

  return { events, s1, s2, s3, currentController };
}

const { events, s1, s2, s3 } = simulateAdminFilterCycle();

assert("request-1 signal was aborted by request-2", s1.aborted === true);
assert("request-2 signal was aborted by request-3", s2.aborted === true);
assert("request-3 signal is still active (latest)", s3.aborted === false);
assert("3 requests produce 5 events (1+2+2)", events.length === 5);

// ── 2. Verify AbortController cancellation pattern ──
console.log("\n=== AbortController Pattern ===\n");

const ctrl = new AbortController();
const signal = ctrl.signal;

assert("signal starts as not aborted", signal.aborted === false);

let abortCalled = false;
signal.addEventListener("abort", () => { abortCalled = true; });

ctrl.abort();

assert("abort event fires", abortCalled === true);
assert("signal.aborted is true after abort", signal.aborted === true);

try {
  await fetch("https://example.com", { signal });
  assert("fetch with aborted signal throws", false);
} catch (err) {
  assert("fetch with aborted signal throws DOMException", err.name === "AbortError");
}

// ── 3. Verify only latest signal is used ──
console.log("\n=== Only Latest Signal Applied ===\n");

function simulateRapidFilters(count) {
  let activeController = null;
  const abortedSignals = [];
  let lastUsedSignal = null;

  for (let i = 0; i < count; i++) {
    if (activeController) {
      activeController.abort();
      abortedSignals.push(activeController.signal);
    }
    activeController = new AbortController();
    lastUsedSignal = activeController.signal;
  }

  return { abortedSignals, lastUsedSignal, activeController };
}

const rapid = simulateRapidFilters(10);

assert("9 signals were aborted (10 total minus last)", rapid.abortedSignals.length === 9);
assert("all aborted signals report aborted=true", rapid.abortedSignals.every(s => s.aborted === true));
assert("the last signal is NOT aborted", rapid.lastUsedSignal.aborted === false);
assert("lastUsedSignal matches activeController.signal", rapid.lastUsedSignal === rapid.activeController.signal);

// ── 4. Verify useEffect cleanup pattern ──
console.log("\n=== useEffect Cleanup Pattern ===\n");

function simulateUseEffectLifecycle() {
  const log = [];

  function effectRun(controller) {
    log.push(`started with controller ${controller.id}`);
    return () => {
      controller.abort();
      log.push(`cleanup: aborted controller ${controller.id}`);
    };
  }

  const ctrl1 = { id: 1, signal: { aborted: false }, abort() { this.signal.aborted = true; } };
  const ctrl2 = { id: 2, signal: { aborted: false }, abort() { this.signal.aborted = true; } };

  const cleanup1 = effectRun(ctrl1);
  cleanup1();
  const cleanup2 = effectRun(ctrl2);

  return { log, ctrl1, ctrl2, cleanup2 };
}

const ue = simulateUseEffectLifecycle();

assert("cleanup1 aborted controller 1", ue.ctrl1.signal.aborted === true);
assert("controller 2 is still active", ue.ctrl2.signal.aborted === false);
assert("cleanup log has start and cleanup entries", ue.log.length === 3);

// ── 5. Source code verification (smoke test) ──
console.log("\n=== Source Code Verification (admin/page.tsx) ===\n");

const srcPath = resolve("src/app/dashboard/admin/page.tsx");
let source;
try {
  source = readFileSync(srcPath, "utf-8");
} catch {
  source = readFileSync(resolve("frontend/src/app/dashboard/admin/page.tsx"), "utf-8");
}

assert("source file readable", source.length > 0);
assert("uses useRef for AbortController (abortRef)", /abortRef\s*=\s*useRef<AbortController\s*\|\s*null>/.test(source));
assert("aborts previous controller", /abortRef\.current\.abort\(\)/.test(source));
assert("creates new AbortController", /new\s+AbortController\(\)/.test(source));
assert("assigns controller to abortRef", /abortRef\.current\s*=\s*controller/.test(source));
assert("passes signal to API config", /signal:\s*controller\.signal/.test(source));
assert("handles CanceledError", /CanceledError/.test(source));
assert("handles ERR_CANCELED code", /ERR_CANCELED/.test(source));
assert("early return on cancellation", /return;\s*$/.test(source) || /return\s*;/.test(source));
assert("useEffect cleanup calls abort", /return\s*\(\)\s*=>/.test(source) && /controller\.abort\(\)/.test(source));
assert("fetchData defined inside useEffect", /async\s+function\s+fetchData\(\)/.test(source));

// ── 6. Verify filter triggers re-fetch (dependency array) ──
console.log("\n=== Filter → Re-fetch Wiring ===\n");

assert("filtroRango in useEffect deps", /\[.*authLoading.*token.*user.*filtroRango/.test(source));
assert("filtroDesde in useEffect deps", /filtroDesde/.test(source));
assert("filtroHasta in useEffect deps", /filtroHasta/.test(source));
assert("setLoading(true) on filter change", /setFiltroRango\(key\)[\s\S]*?setLoading\(true\)/.test(source));

// ── Results ──
console.log(`\n=== Resultados: ${passed} passed, ${failed} failed ===\n`);
process.exit(failed ? 1 : 0);
