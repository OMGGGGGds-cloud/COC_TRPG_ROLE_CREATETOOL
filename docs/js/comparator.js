/* Roll vs. Point-Buy comparison for CoC 7e character creation.
 * Mode A (full_set): Best of K complete sets.
 * Mode B (per_group): Best per formula group. */
(function(TRPG) {
"use strict";

var COC_PERCENTILE_MULTIPLIER = 5;

var ALL_CHARS = TRPG.COC_CHARACTERISTICS;
var CHARS_3D6 = ALL_CHARS.filter(function(c) { return c.formula === "3d6"; });
var CHARS_2D6 = ALL_CHARS.filter(function(c) { return c.formula === "2d6+6"; });
var COUNT_3D6 = CHARS_3D6.length;  // 5
var COUNT_2D6 = CHARS_2D6.length;  // 3

// ---- Helpers ----

function buildAttrDist(char) {
    var expr = TRPG.parse(char.formula);
    return TRPG.diceSumDistributionWithModifier(expr.count, expr.sides, expr.modifier);
}

function rawExpectedFromFormula(formula) {
    var expr = TRPG.parse(formula);
    return expr.rawExpected();
}

// ---- ComparisonResult ----

TRPG.ComparisonResult = function(opts) {
    this.pointBuyBudget = opts.budget;
    this.attempts = opts.attempts;
    this.mode = opts.mode;
    this.expectedBestTotal = opts.expectedBestTotal;
    this.pointBuyTotal = opts.budget;
    this.singleSetExpected = opts.singleSetExpected || null;
    this.group3d6ExpectedBest = opts.group3d6ExpectedBest || null;
    this.group2d6ExpectedBest = opts.group2d6ExpectedBest || null;
    this.group3d6PoolSize = opts.group3d6PoolSize || null;
    this.group2d6PoolSize = opts.group2d6PoolSize || null;
};

TRPG.ComparisonResult.prototype.difference = function() {
    return this.expectedBestTotal - this.pointBuyTotal;
};

TRPG.ComparisonResult.prototype.recommendation = function() {
    var diff = this.difference();
    if (diff > 0) {
        return "Rolling beats buying by " + diff.toFixed(1) + " points. " +
               "With " + this.attempts + " attempt(s), rolling yields a better expected outcome.";
    } else if (diff < 0) {
        return "Buying beats rolling by " + Math.abs(diff).toFixed(1) + " points. " +
               "The point-buy budget gives a better guaranteed outcome.";
    } else {
        return "Both approaches yield the same expected outcome.";
    }
};

// ---- Mode A: Best of K full sets ----

function compareModeFullSet(budget, attempts) {
    var attrDists = ALL_CHARS.map(buildAttrDist);
    var setDist = TRPG.convolveDistributions(attrDists);

    var singleExpected = 0;
    for (var i = 0; i < ALL_CHARS.length; i++) {
        singleExpected += rawExpectedFromFormula(ALL_CHARS[i].formula);
    }

    var expectedBest = TRPG.expectedMaxOfK(setDist, attempts) * COC_PERCENTILE_MULTIPLIER;

    return new TRPG.ComparisonResult({
        budget: budget,
        attempts: attempts,
        mode: "full_set",
        expectedBestTotal: expectedBest,
        singleSetExpected: singleExpected
    });
}

// ---- Mode B: Best per formula group ----

function compareModePerGroup(budget, attempts) {
    var dist3d6 = buildAttrDist(CHARS_3D6[0]);
    var dist2d6 = buildAttrDist(CHARS_2D6[0]);

    var pool3d6 = COUNT_3D6 * attempts;
    var pool2d6 = COUNT_2D6 * attempts;

    var expectedBest3d6 = TRPG.expectedSumOfTopK(dist3d6, pool3d6, COUNT_3D6) * COC_PERCENTILE_MULTIPLIER;
    var expectedBest2d6 = TRPG.expectedSumOfTopK(dist2d6, pool2d6, COUNT_2D6) * COC_PERCENTILE_MULTIPLIER;

    var expectedBestTotal = expectedBest3d6 + expectedBest2d6;

    var singleExpected = 0;
    for (var i = 0; i < ALL_CHARS.length; i++) {
        singleExpected += rawExpectedFromFormula(ALL_CHARS[i].formula);
    }

    return new TRPG.ComparisonResult({
        budget: budget,
        attempts: attempts,
        mode: "per_group",
        expectedBestTotal: expectedBestTotal,
        singleSetExpected: singleExpected,
        group3d6ExpectedBest: expectedBest3d6,
        group2d6ExpectedBest: expectedBest2d6,
        group3d6PoolSize: pool3d6,
        group2d6PoolSize: pool2d6
    });
}

// ---- Public API ----

TRPG.compareRollVsBuy = function(budget, attempts, mode) {
    if (budget < 0) throw new Error("Budget must be >= 0, got " + budget + ".");
    if (attempts < 1) throw new Error("Attempts must be >= 1, got " + attempts + ".");
    if (mode !== "full_set" && mode !== "per_group") {
        throw new Error("Mode must be 'full_set' or 'per_group', got '" + mode + "'.");
    }

    if (mode === "full_set") {
        return compareModeFullSet(budget, attempts);
    } else {
        return compareModePerGroup(budget, attempts);
    }
};

})(window.TRPG = window.TRPG || {});
