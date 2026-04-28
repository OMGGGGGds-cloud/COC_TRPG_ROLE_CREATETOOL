/* Call of Cthulhu 7th Edition character creation data. */
(function(TRPG) {

TRPG.COCCCharacteristic = function(name, formula, fullName, displayOrder) {
    this.name = name;
    this.formula = formula;
    this.fullName = fullName;
    this.displayOrder = displayOrder;
};

TRPG.COC_CHARACTERISTICS = [
    new TRPG.COCCCharacteristic("STR", "3d6",   "Strength",      1),
    new TRPG.COCCCharacteristic("CON", "3d6",   "Constitution",  2),
    new TRPG.COCCCharacteristic("DEX", "3d6",   "Dexterity",     3),
    new TRPG.COCCCharacteristic("POW", "3d6",   "Power",         4),
    new TRPG.COCCCharacteristic("APP", "3d6",   "Appearance",    5),
    new TRPG.COCCCharacteristic("SIZ", "2d6+6", "Size",          6),
    new TRPG.COCCCharacteristic("INT", "2d6+6", "Intelligence",  7),
    new TRPG.COCCCharacteristic("EDU", "2d6+6", "Education",     8)
];

})(window.TRPG = window.TRPG || {});
