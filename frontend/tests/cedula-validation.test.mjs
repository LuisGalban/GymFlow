// Test: F2-07 — Sanitización y Validación de Cédula en Recepción
// Run: node frontend/tests/cedula-validation.test.mjs

const STRICT = /^[VJEGP]-?\d{1,10}$/;
const PARTIAL = /^[VJEGP]-?\d{0,10}$/;

function sanitize(raw) {
  const s = raw.toUpperCase().replace(/[^VJEGP\d-]/g, "");
  if (s === "") return "";
  if (!PARTIAL.test(s)) return null;
  return s;
}

let passed = 0;
let failed = 0;

function assert(label, ok) {
  if (ok) { passed++; console.log(`  ✅ ${label}`); }
  else { failed++; console.error(`  ❌ ${label}`); }
}

console.log("\n=== Sanitization ===\n");

const t1 = sanitize("V-25111222");
assert("V-25111222 -> V-25111222", t1 === "V-25111222");

const t2 = sanitize("v-25111222");
assert("lowercase v -> uppercase V-25111222", t2 === "V-25111222");

const t3 = sanitize("'; DROP TABLE miembros; --");
assert("SQL injection -> null (no match)", t3 === null);

const t4 = sanitize("<script>alert(1)</script>");
assert("XSS -> null (no match)", t4 === null);

const t5 = sanitize("../../../etc/passwd");
assert("Path traversal -> null (no match)", t5 === null);

const t6 = sanitize("V-99999999999");
assert("11 digits -> null (max 10)", t6 === null);

const t7 = sanitize("   V-123   ");
assert("spaces stripped -> V-123", t7 === "V-123");

const t8 = sanitize("J-1234567890");
assert("J-1234567890 -> J-1234567890 (10 digits OK)", t8 === "J-1234567890");

const t9 = sanitize("E-0");
assert("E-0 -> E-0 (1 digit OK)", t9 === "E-0");

const t10 = sanitize("P-");
assert("P- (no digits) -> P- (partial match)", t10 === "P-");

const t11 = sanitize("G");
assert("G solo -> G (partial match)", t11 === "G");

const t12 = sanitize("");
assert("empty string -> empty string", t12 === "");

const t13 = sanitize("a1b2c3");
assert("random chars 'a1b2c3' -> 'A123' not in VJEGP -> null", t13 === null);

console.log("\n=== Strict Pattern (API guard) ===\n");

assert("V-25111222 matches strict", STRICT.test("V-25111222"));
assert("J-1234567890 matches strict", STRICT.test("J-1234567890"));
assert("E-0 matches strict", STRICT.test("E-0"));
assert("P-1 matches strict", STRICT.test("P-1"));
assert("G-9999999999 matches strict (10 digits)", STRICT.test("G-9999999999"));
assert("'' does NOT match strict", !STRICT.test(""));
assert("'V' does NOT match strict (no digits)", !STRICT.test("V"));
assert("'V-' does NOT match strict (no digits)", !STRICT.test("V-"));
assert("'ABC' does NOT match strict", !STRICT.test("ABC"));
assert("'V-99999999999' does NOT match strict (11 digits)", !STRICT.test("V-99999999999"));
assert("'; DROP' does NOT match strict", !STRICT.test("'; DROP"));
assert("'<script>' does NOT match strict", !STRICT.test("<script>"));
assert("'V-123\x00null' does NOT match strict (null byte)", !STRICT.test("V-123\x00null"));

console.log(`\n=== Resultados: ${passed} passed, ${failed} failed ===\n`);
process.exit(failed ? 1 : 0);
