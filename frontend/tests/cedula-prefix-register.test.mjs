// Test: F2-09 — Prefijo de Cédula Implícito en Registro de Atletas
// Run: node frontend/tests/cedula-prefix-register.test.mjs

const STRICT = /^[VJEGP]-?\d{1,10}$/;

function buildCedula(prefijo, digits) {
  return `${prefijo}-${digits}`;
}

function filterNumeric(raw) {
  return raw.replace(/\D/g, "");
}

let passed = 0;
let failed = 0;

function assert(label, ok) {
  if (ok) { passed++; console.log(`  ✅ ${label}`); }
  else { failed++; console.error(`  ❌ ${label}`); }
}

console.log("\n=== Test 1: input '12345678' con prefijo V se guarda como 'V-12345678' ===\n");

const t1 = buildCedula("V", "12345678");
assert("V + 12345678 = V-12345678", t1 === "V-12345678");
assert("V-12345678 pasa regex strict", STRICT.test(t1));

console.log("\n=== Test 2: input con caracteres no numéricos es rechazado ===\n");

const dirty = "12a34b-5c6d";
const clean = filterNumeric(dirty);
assert("filterNumeric('12a34b-5c6d') = '123456'", clean === "123456");
assert("clean value '123456' contiene solo dígitos", /^\d+$/.test(clean));

const t2 = buildCedula("V", clean);
assert("V + 123456 = V-123456", t2 === "V-123456");
assert("V-123456 pasa regex strict", STRICT.test(t2));

// Non-numeric only input should produce empty string
const allAlpha = filterNumeric("abcXYZ-.;");
assert("filterNumeric('abcXYZ-.;') = ''", allAlpha === "");

// Build with empty digits should fail strict when digits are empty
const tEmpty = buildCedula("V", "");
assert("V + '' = 'V-' NO pasa regex strict (sin dígitos)", !STRICT.test(tEmpty));

console.log("\n=== Test 3: cambio de prefijo a 'J' produce 'J-12345678' ===\n");

const t3 = buildCedula("J", "12345678");
assert("J + 12345678 = J-12345678", t3 === "J-12345678");
assert("J-12345678 pasa regex strict", STRICT.test(t3));

// Verify other prefixes also work
for (const p of ["E", "G", "P"]) {
  const v = buildCedula(p, "87654321");
  assert(`${p} + 87654321 = ${p}-87654321 pasa regex strict`, STRICT.test(v));
}

console.log("\n=== Edge: maxLength 10 y dígitos ===\n");

const eleven = "12345678901";
const truncated = filterNumeric(eleven).slice(0, 10);
assert("filterNumeric('12345678901') cortado a 10 dígitos", truncated === "1234567890" && truncated.length === 10);

const t4 = buildCedula("V", truncated);
assert("V-1234567890 (10 dígitos) pasa regex strict", STRICT.test(t4));
assert("V-12345678901 (11 dígitos) NO pasa regex strict", !STRICT.test("V-12345678901"));

console.log(`\n=== Resultados: ${passed} passed, ${failed} failed ===\n`);
process.exit(failed ? 1 : 0);
