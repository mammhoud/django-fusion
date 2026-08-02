/**
 * Round-trip test for the codec format shared between
 * django-fusion's ``FusionCodec`` and the TypeScript ``FusionDecoder``.
 *
 * This test:
 * 1. Builds a known payload using the same algorithm as Python's
 *    ``FusionCodec.encode()`` (``fusion_v<version>:<urlsafe_base64(json)>``).
 * 2. Decodes it with a standalone decoder function that mirrors
 *    ``FusionDecoder.decode()``.
 * 3. Validates the decoded result matches the original data.
 *
 * Run with:
 *   node projects/lms/lms/tests/fusion-decoder-roundtrip.test.mjs
 *
 * Expected output: "All codec round-trip tests passed!"
 */

import assert from 'node:assert/strict';

// ─── Constants ─────────────────────────────────────────────────────

/** Regex matching the codec prefix format. */
const CODEC_PREFIX_RE = /^fusion_v(\d+):(.+)$/;

// ─── Standalone decoder (mirrors FusionDecoder.decode()) ───────────

/**
 * Parse and decode a ``fusion_v<version>:<base64>`` string.
 * This mirrors ``django_fusion.routes.rendering.session.FusionCodec.decode()``.
 *
 * @param {string} encoded - The codec-encoded string.
 * @returns {unknown} The decoded JSON data.
 */
function decode(encoded) {
  if (!encoded || typeof encoded !== 'string') {
    throw new Error(`Invalid encoded value: ${encoded}`);
  }

  const match = CODEC_PREFIX_RE.exec(encoded);
  if (!match) {
    throw new Error(
      `Invalid codec prefix — expected "fusion_v<version>:<base64>", got ${encoded.slice(0, 30)}`,
    );
  }

  const b64 = match[2];

  let jsonStr;
  try {
    jsonStr = Buffer.from(b64, 'base64').toString('utf-8');
  } catch {
    try {
      jsonStr = atob(b64);
    } catch {
      throw new Error(`Failed to base64-decode payload: ${b64}`);
    }
  }

  try {
    return JSON.parse(jsonStr);
  } catch (cause) {
    throw new Error(`Failed to JSON-parse decoded payload: ${jsonStr}`, { cause });
  }
}

/**
 * Encode a value into ``fusion_v<version>:<base64>`` format.
 * This mirrors ``django_fusion.routes.rendering.session.FusionCodec.encode()``.
 *
 * @param {unknown} data - The data to encode.
 * @param {string} [version='1'] - Codec version number.
 * @returns {string} The codec-encoded string.
 */
function encode(data, version = '1') {
  const raw = JSON.stringify(data, null, 0); // compact JSON
  const b64 = Buffer.from(raw, 'utf-8').toString('base64url');

  // Base64url-encode (same as Python's urlsafe_b64encode)
  const urlSafeB64 = b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

  return `fusion_v${version}:${urlSafeB64}`;
}

// ─── Test payloads ────────────────────────────────────────────────

/** Simple key-value payload. */
const SIMPLE_PAYLOAD = { key: 'value', number: 42 };

/** Fragment-pointer payload matching the Python test. */
const FRAGMENT_POINTER_PAYLOAD = {
  component: 'pages.home',
  fragment_name: 'pages.home',
  fusion_render_first: false,
  fragment_url: 'http://localhost:8000/fragments/pages.home/',
  page_slug: 'home',
  title: 'Learn Without Limits',
  tags: ['a', 'b', 'c'],
};

/** Nested payload. */
const NESTED_PAYLOAD = {
  metadata: {
    version: 2,
    flags: [true, false, null],
    nested: { deep: { value: 3.14 } },
  },
  items: [
    { id: 1, name: 'first' },
    { id: 2, name: 'second' },
  ],
};

// ─── Tests ────────────────────────────────────────────────────────

function testRoundTrip(label, data) {
  const encoded = encode(data);
  assert(
    typeof encoded === 'string' && encoded.startsWith('fusion_v1:'),
    `[${label}] Expected "fusion_v1:" prefix, got ${encoded.slice(0, 20)}`,
  );

  const decoded = decode(encoded);
  assert.deepStrictEqual(
    decoded,
    data,
    `[${label}] Round-trip mismatch:\n  Encoded: ${encoded}\n  Decoded: ${JSON.stringify(decoded)}\n  Expected: ${JSON.stringify(data)}`,
  );

  console.log(`  ✅ ${label}`);
}

function testInvalidInputs() {
  // Invalid prefix
  assert.throws(
    () => decode('bad_prefix:AAAA'),
    /Invalid codec prefix/,
    'Should reject invalid prefix',
  );
  console.log('  ✅ Invalid prefix rejected');

  // Empty string
  assert.throws(() => decode(''), /Invalid encoded value/, 'Should reject empty string');
  console.log('  ✅ Empty string rejected');

  // Garbage base64 (Node.js Buffer.from is lenient — may silently decode,
  // so the error may come from JSON parsing instead of base64 decoding).
  assert.throws(
    () => decode('fusion_v1:!!!not-base64!!!'),
    /Failed to (base64-decode|JSON-parse)/,
    'Should reject garbage base64',
  );
  console.log('  ✅ Garbage base64 rejected');
}

// ─── Cross-language compatibility test ────────────────────────────

/**
 * This test validates that a Python-produced encoded string can be
 * decoded on the TypeScript side. The encoded string is produced by
 * ``FusionCodec.encode({"component": "pages.privacy"})`` in Python.
 *
 * To regenerate this value from Python:
 *
 *   from django_fusion.routes.rendering.session import FusionCodec
 *   print(repr(FusionCodec.encode({"component": "pages.privacy"})))
 */
function testCrossLanguageCompatibility() {
  // This is a known-good encoded string produced by Python's FusionCodec.
  // It encodes: {"component": "pages.privacy"}
  // Regenerate by running the Python test ``test_produces_known_string``.
  const pythonEncoded = 'fusion_v1:eyJjb21wb25lbnQiOiJwYWdlcy5wcml2YWN5In0';

  const decoded = decode(pythonEncoded);
  assert.deepStrictEqual(
    decoded,
    { component: 'pages.privacy' },
    `Cross-language compatibility failure:\n  Python output: ${pythonEncoded}\n  JS decoded: ${JSON.stringify(decoded)}`,
  );
  console.log('  ✅ Cross-language compatibility (Python → TypeScript)');
}

// ─── Main ─────────────────────────────────────────────────────────

function main() {
  console.log('\n🔁 Fusion Codec Round-Trip Tests\n');

  // Round-trip tests
  console.log('Round-trips:');
  testRoundTrip('Simple dict', SIMPLE_PAYLOAD);
  testRoundTrip('Fragment pointer', FRAGMENT_POINTER_PAYLOAD);
  testRoundTrip('Nested structure', NESTED_PAYLOAD);

  // Error handling
  console.log('\nError handling:');
  testInvalidInputs();

  // Cross-language
  console.log('\nCross-language:');
  testCrossLanguageCompatibility();

  console.log('\n✅ All codec round-trip tests passed!');
}

main();
