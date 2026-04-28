/* Node.js test runner for TRPG JS modules. Run with: node docs/js/test.js */

var fs = require('fs');
var vm = require('vm');

// Create a minimal browser-like environment
global.window = {};
global.document = {
    querySelectorAll: function() { return []; },
    addEventListener: function() {},
    getElementById: function() { return null; }
};

// Load modules in order
function loadScript(path) {
    var code = fs.readFileSync(path, 'utf-8');
    var script = new vm.Script(code);
    script.runInThisContext();
}

loadScript('docs/js/parser.js');
loadScript('docs/js/calculator.js');
loadScript('docs/js/coc_data.js');
loadScript('docs/js/distribution.js');
loadScript('docs/js/comparator.js');

var TRPG = window.TRPG;
var passed = 0;
var failed = 0;

function assert(cond, msg) {
    if (cond) {
        passed++;
    } else {
        failed++;
        console.error('FAIL: ' + msg);
    }
}

function assertFloatEqual(actual, expected, tolerance, msg) {
    if (Math.abs(actual - expected) < tolerance) {
        passed++;
    } else {
        failed++;
        console.error('FAIL: ' + msg + ' (got ' + actual + ', expected ' + expected + ')');
    }
}

// ---- Parser tests ----
console.log('\n--- Parser ---');

var e = TRPG.parse('3d6');
assert(e.count === 3, '3d6 count');
assert(e.sides === 6, '3d6 sides');
assert(e.modifier === 0, '3d6 modifier');
assert(e.notation() === '3d6', '3d6 notation');
assertFloatEqual(e.rawExpected(), 10.5, 0.01, '3d6 raw expected');
assertFloatEqual(e.percentileExpected(), 52.5, 0.01, '3d6 percentile expected');

var e2 = TRPG.parse('2d6+6');
assert(e2.count === 2, '2d6+6 count');
assert(e2.sides === 6, '2d6+6 sides');
assert(e2.modifier === 6, '2d6+6 modifier');
assertFloatEqual(e2.rawExpected(), 13, 0.01, '2d6+6 raw expected');
assertFloatEqual(e2.percentileExpected(), 65, 0.01, '2d6+6 percentile expected');

var e3 = TRPG.parse('4d4-2');
assert(e3.modifier === -2, '4d4-2 modifier');
assert(e3.notation() === '4d4-2', '4d4-2 notation');
assertFloatEqual(e3.rawExpected(), 8, 0.01, '4d4-2 raw expected');
assertFloatEqual(e3.percentileExpected(), 40, 0.01, '4d4-2 percentile expected');

// Error cases
var parseErrors = 0;
['', 'd6', '3d', 'abc', '0d6', '3d1'].forEach(function(s) {
    try { TRPG.parse(s); } catch(ex) { parseErrors++; }
});
assert(parseErrors === 6, 'Parser rejects invalid input (6 cases)');

// ---- Expected value tests ----
console.log('--- Expected Value ---');
assertFloatEqual(TRPG.expectedValue(TRPG.parse('5d6')), 87.5, 0.01, '5d6 expected');
assertFloatEqual(TRPG.expectedValue(TRPG.parse('1d20')), 52.5, 0.01, '1d20 expected');
assertFloatEqual(TRPG.expectedValue(TRPG.parse('3d8')), 67.5, 0.01, '3d8 expected');

var strResult = TRPG.expectedValueStr('3d6');
assert(strResult.indexOf('52.5') !== -1, 'expectedValueStr contains 52.5');

// ---- CoC data tests ----
console.log('--- CoC Data ---');
assert(TRPG.COC_CHARACTERISTICS.length === 8, '8 characteristics');
assert(TRPG.COC_CHARACTERISTICS[0].name === 'STR', 'first is STR');
assert(TRPG.COC_CHARACTERISTICS[7].name === 'EDU', 'last is EDU');

// ---- Distribution tests ----
console.log('--- Distribution ---');

var d1 = TRPG.diceSumDistribution(1, 6);
var keys1 = Object.keys(d1);
assert(keys1.length === 6, '1d6 has 6 outcomes');
assertFloatEqual(d1[1], 1/6, 0.001, '1d6 P(1)');
assertFloatEqual(d1[6], 1/6, 0.001, '1d6 P(6)');

var sum = 0;
for (var k in d1) { if (d1.hasOwnProperty(k)) sum += d1[k]; }
assertFloatEqual(sum, 1.0, 0.001, '1d6 sums to 1');

var d2 = TRPG.diceSumDistribution(2, 6);
assert(Object.keys(d2).length === 11, '2d6 has 11 outcomes (2-12)');
assertFloatEqual(d2[7], 6/36, 0.001, '2d6 P(7) = 6/36');
assertFloatEqual(d2[2], 1/36, 0.001, '2d6 P(2) = 1/36');

// CDF
var cdf = TRPG.cumulativeDistribution(d2);
assertFloatEqual(cdf[2], 1/36, 0.001, 'CDF[2] = 1/36');
assertFloatEqual(cdf[12], 1.0, 0.001, 'CDF[12] = 1');

// Expected max of K
var dist3d6 = TRPG.diceSumDistribution(3, 6);
var max1 = TRPG.expectedMaxOfK(dist3d6, 1);
assertFloatEqual(max1, 10.5, 0.01, 'Max of 1 draw = expected value');

var max2 = TRPG.expectedMaxOfK(dist3d6, 2);
assert(max2 > max1, 'Max of 2 draws > max of 1');

var max5 = TRPG.expectedMaxOfK(dist3d6, 5);
assert(max5 > max2, 'Max of 5 draws > max of 2');

// Expected sum of top K
var top1of2 = TRPG.expectedSumOfTopK(dist3d6, 2, 1);
assertFloatEqual(top1of2, max2, 0.001, 'Top 1 of 2 = max of 2');

var top2of2 = TRPG.expectedSumOfTopK(dist3d6, 2, 2);
assertFloatEqual(top2of2, 21, 0.01, 'Top 2 of 2 = 2 * mean = 21');

// Convolution
var d6_1 = TRPG.diceSumDistribution(1, 6);
var d6_2 = TRPG.convolveDistributions([d6_1, d6_1]);
assertFloatEqual(d6_2[7], 6/36, 0.001, 'Convolution: 6+1=7 prob');
assert(Object.keys(d6_2).length === 11, 'Convolution: right outcome count');

// ---- Comparator tests ----
console.log('--- Comparator ---');

// Mode A: single attempt
var r1 = TRPG.compareRollVsBuy(450, 1, 'full_set');
assertFloatEqual(r1.expectedBestTotal, 457.5, 0.5, 'Mode A K=1 ~ 457.5');
assert(r1.mode === 'full_set', 'Mode A mode field');

// Mode A: more attempts increases expected
var r2 = TRPG.compareRollVsBuy(450, 3, 'full_set');
assert(r2.expectedBestTotal > r1.expectedBestTotal, 'Mode A: K=3 > K=1');

// Mode B: single attempt
var r3 = TRPG.compareRollVsBuy(450, 1, 'per_group');
assertFloatEqual(r3.expectedBestTotal, 457.5, 0.5, 'Mode B K=1 ~ 457.5');

// Mode B: more attempts
var r4 = TRPG.compareRollVsBuy(450, 3, 'per_group');
assert(r4.expectedBestTotal > r3.expectedBestTotal, 'Mode B: K=3 > K=1');

// Mode B > Mode A for same K (more freedom)
assert(r4.expectedBestTotal > r2.expectedBestTotal, 'Mode B > Mode A for K=3');

// Recommendations
assert(r1.recommendation().indexOf('Rolling beats') === 0, 'Recommendation: rolling wins with K=1');
var rLow = TRPG.compareRollVsBuy(1000, 1, 'full_set');
assert(rLow.recommendation().indexOf('Buying beats') === 0, 'Recommendation: buying wins with big budget');

// ---- Results ----
console.log('\n========================');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
if (failed > 0) process.exit(1);
