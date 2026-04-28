/* Dice notation parser. Parses strings like "3d6", "2d6+6", "5d6", "4d4-2". */
(function(TRPG) {

var DICE_PATTERN = /^(\d+)d(\d+)([+-]\d+)?$/i;

TRPG.DiceExpression = function(count, sides, modifier) {
    this.count = count;
    this.sides = sides;
    this.modifier = modifier || 0;
};

TRPG.DiceExpression.prototype.notation = function() {
    var base = this.count + "d" + this.sides;
    if (this.modifier > 0) return base + "+" + this.modifier;
    if (this.modifier < 0) return base + this.modifier;
    return base;
};

TRPG.DiceExpression.prototype.rawExpected = function() {
    return this.count * (this.sides + 1) / 2 + this.modifier;
};

TRPG.DiceExpression.prototype.percentileExpected = function() {
    return this.rawExpected() * 5;
};

TRPG.parse = function(notation) {
    var s = notation.trim().toLowerCase();
    var match = DICE_PATTERN.exec(s);
    if (!match) {
        throw new Error(
            "Invalid dice notation: '" + notation + "'. " +
            "Expected format like '3d6', '2d6+6', or '5d6'."
        );
    }
    var count = parseInt(match[1], 10);
    var sides = parseInt(match[2], 10);
    var modifier = match[3] ? parseInt(match[3], 10) : 0;

    if (count < 1) {
        throw new Error("Number of dice must be at least 1, got " + count + ".");
    }
    if (sides < 2) {
        throw new Error("Number of sides must be at least 2, got " + sides + ".");
    }

    return new TRPG.DiceExpression(count, sides, modifier);
};

})(window.TRPG = window.TRPG || {});
