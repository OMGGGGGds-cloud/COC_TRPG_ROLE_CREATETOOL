/* Call of Cthulhu 7th Edition character creation data. */
(function(TRPG) {
"use strict";

TRPG.CoCCharacteristic = function(name, formula, fullName, displayOrder) {
    this.name = name;
    this.formula = formula;
    this.fullName = fullName;
    this.displayOrder = displayOrder;
};

TRPG.COC_CHARACTERISTICS = [
    new TRPG.CoCCharacteristic("STR", "3d6",   "Strength",      1),
    new TRPG.CoCCharacteristic("CON", "3d6",   "Constitution",  2),
    new TRPG.CoCCharacteristic("DEX", "3d6",   "Dexterity",     3),
    new TRPG.CoCCharacteristic("POW", "3d6",   "Power",         4),
    new TRPG.CoCCharacteristic("APP", "3d6",   "Appearance",    5),
    new TRPG.CoCCharacteristic("SIZ", "2d6+6", "Size",          6),
    new TRPG.CoCCharacteristic("INT", "2d6+6", "Intelligence",  7),
    new TRPG.CoCCharacteristic("EDU", "2d6+6", "Education",     8)
];

})(window.TRPG = window.TRPG || {});
