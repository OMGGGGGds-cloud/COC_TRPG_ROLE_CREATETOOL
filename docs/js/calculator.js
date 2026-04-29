/* Expected value calculator for dice expressions. */
(function(TRPG) {
"use strict";

var COC_PERCENTILE_MULTIPLIER = 5;

TRPG.expectedValue = function(expr) {
    return expr.percentileExpected();
};

TRPG.expectedValueStr = function(notation) {
    var expr = TRPG.parse(notation);
    var total = TRPG.expectedValue(expr);
    var perDie = (expr.sides + 1) / 2;
    var percentilePerDie = perDie * COC_PERCENTILE_MULTIPLIER;
    var multLabel = "(×" + COC_PERCENTILE_MULTIPLIER + ")";

    var parts = [];
    parts.push("Formula: " + expr.notation());
    parts.push("Expected percentile value: " + formatFloat(total));

    var detail = [];
    if (Number.isInteger(percentilePerDie)) {
        detail.push(percentilePerDie + " per die " + multLabel);
    } else {
        detail.push(formatFloat(percentilePerDie) + " per die " + multLabel);
    }
    var label = expr.count === 1 ? "die" : "dice";
    detail.push("× " + expr.count + " " + label);
    if (expr.modifier) {
        var scaled = expr.modifier * COC_PERCENTILE_MULTIPLIER;
        var sign = scaled > 0 ? "+" : "";
        detail.push(sign + scaled + " flat " + multLabel);
    }
    parts.push("  (" + detail.join(", ") + ")");

    return parts.join("\n");
};

function formatFloat(n) {
    if (Number.isInteger(n)) return n.toString();
    // Strip trailing zeros
    return parseFloat(n.toFixed(10)).toString();
}

})(window.TRPG = window.TRPG || {});
