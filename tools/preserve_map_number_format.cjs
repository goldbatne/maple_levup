// Formatting only: preserve existing numeric lexemes and file-ending whitespace.
// Map content must first be authored through MapBuilder.
const assert = require('node:assert/strict');

function numericTokens(text) {
  const audioRanges = [...text.matchAll(/\{[^{}]*"@type"\s*:\s*"MOD\.Core\.SoundComponent"[^{}]*\}/g)]
    .map(m => [m.index, m.index + m[0].length]);
  return [...text.matchAll(/"(?:\\.|[^"\\])*"|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g)]
    .filter(m => m[1] !== undefined && !audioRanges.some(([a, b]) => m.index >= a && m.index < b));
}

function preserveFormat(original, written) {
  const oldTokens = numericTokens(original);
  const newTokens = numericTokens(written);
  assert.equal(oldTokens.length, newTokens.length, 'Non-audio numeric token count changed');
  let result = written;
  for (let i = newTokens.length - 1; i >= 0; i--) {
    assert.equal(Number(oldTokens[i][1]), Number(newTokens[i][1]), 'Non-audio numeric value changed');
    const token = newTokens[i];
    result = result.slice(0, token.index) + oldTokens[i][1] + result.slice(token.index + token[1].length);
  }
  result = result.replace(/\s*$/, original.match(/\s*$/)[0]);
  const parse = s => JSON.parse(s.replace(/^\uFEFF/, ''));
  assert.deepEqual(parse(result), parse(written), 'Formatting changed semantic content');
  return result;
}

module.exports = { preserveFormat };

if (require.main === module) {
  const fs = require('node:fs');
  const { execFileSync } = require('node:child_process');
  const files = execFileSync('git', ['diff', '--name-only', '--', 'map'], { encoding: 'utf8' }).trim().split(/\r?\n/);
  for (const file of files.filter(f => f.endsWith('.map'))) {
    const original = execFileSync('git', ['show', `HEAD:${file}`], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
    const current = fs.readFileSync(file, 'utf8');
    fs.writeFileSync(file, preserveFormat(original, current), 'utf8');
  }
  console.log(`Formatting preserved: ${files.length} maps; semantic changes: 0`);
}
