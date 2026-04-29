/* Main application logic — DOM wiring, tab switching, event handlers. */
(function() {

var TRPG = window.TRPG;

// ---- Tab switching ----

function switchTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach(function(btn) {
        btn.classList.remove("active");
    });
    document.querySelectorAll(".tab-panel").forEach(function(panel) {
        panel.classList.remove("active");
    });

    var activeBtn = document.querySelector(".tab-btn[data-tab='" + tabName + "']");
    var activePanel = document.getElementById("tab-" + tabName);
    if (activeBtn) activeBtn.classList.add("active");
    if (activePanel) activePanel.classList.add("active");

    if (tabName === "coc-ref") renderCoCReference();
}

// ---- Number formatting ----

function fmt(n, decimals) {
    if (decimals === undefined) decimals = 1;
    return Number(n).toFixed(decimals);
}

// =====================================================================
// Tab 1: Expected Value Calculator
// =====================================================================

function renderExpectedValue() {
    var notation = document.getElementById("ev-input").value.trim();
    var resultDiv = document.getElementById("ev-result");
    var errorDiv = document.getElementById("ev-error");
    var infoDiv = document.getElementById("ev-info");

    resultDiv.innerHTML = "";
    errorDiv.textContent = "";
    errorDiv.classList.remove("visible");
    infoDiv.classList.add("hidden");

    if (!notation) {
        infoDiv.classList.remove("hidden");
        return;
    }

    try {
        var expr = TRPG.parse(notation);
        var total = TRPG.expectedValue(expr);
        var rawExpected = total / 5;
        var perDie = (expr.sides + 1) / 2;

        var html = '<div class="result-cards">';

        html += '<div class="card"><div class="card-label">Formula</div><div class="card-value">' + expr.notation() + '</div></div>';
        html += '<div class="card"><div class="card-label">Expected Value</div><div class="card-value accent">' + fmt(rawExpected) + '</div></div>';

        html += '</div>';

        html += '<div class="breakdown">';
        html += '<div class="breakdown-title">Breakdown</div>';
        html += '<div>Per-die expected: <strong>' + fmt(perDie) + '</strong></div>';
        html += '<div>Dice count: <strong>' + expr.count + '</strong></div>';
        if (expr.modifier) {
            var sign = expr.modifier > 0 ? "+" : "";
            html += '<div>Flat modifier: <strong>' + sign + expr.modifier + '</strong></div>';
        }
        html += '</div>';

        resultDiv.innerHTML = html;
        infoDiv.classList.add("hidden");

    } catch (e) {
        errorDiv.textContent = e.message;
        errorDiv.classList.add("visible");
        resultDiv.innerHTML = "";
        infoDiv.classList.add("hidden");
    }
}

// =====================================================================
// Tab 2: CoC 7e Character Creation Reference
// =====================================================================

function renderCoCReference() {
    var chars = TRPG.COC_CHARACTERISTICS;
    var names = [];
    var formulas = [];
    var expectedVals = [];
    var fullNames = [];

    for (var i = 0; i < chars.length; i++) {
        names.push(chars[i].name);
        formulas.push(chars[i].formula);
        var ev = TRPG.expectedValue(TRPG.parse(chars[i].formula));
        expectedVals.push(ev);
        fullNames.push(chars[i].fullName);
    }

    var total = expectedVals.reduce(function(a, b) { return a + b; }, 0);
    var avg = total / expectedVals.length;

    // Summary cards
    document.getElementById("coc-total").textContent = fmt(total);
    document.getElementById("coc-avg").textContent = fmt(avg);
    document.getElementById("coc-count").textContent = expectedVals.length;

    // Bar chart
    var maxEv = Math.max.apply(null, expectedVals);
    var chartHtml = "";
    for (var j = 0; j < expectedVals.length; j++) {
        var pct = (expectedVals[j] / maxEv) * 100;
        var barClass = formulas[j] === "3d6" ? "bar-3d6" : "bar-2d6";
        chartHtml += '<div class="bar-row">';
        chartHtml += '<div class="bar-label">' + names[j] + '</div>';
        chartHtml += '<div class="bar-track"><div class="bar-fill ' + barClass + '" style="width:' + pct + '%"></div></div>';
        chartHtml += '<div class="bar-value">' + fmt(expectedVals[j]) + '</div>';
        chartHtml += '</div>';
    }
    document.getElementById("coc-chart").innerHTML = chartHtml;

    // Table
    var tbody = document.getElementById("coc-tbody");
    tbody.innerHTML = "";
    for (var k = 0; k < names.length; k++) {
        var rowClass = formulas[k] === "2d6+6" ? "row-2d6" : "";
        tbody.innerHTML += '<tr class="' + rowClass + '">' +
            '<td>' + names[k] + '</td>' +
            '<td>' + formulas[k] + '</td>' +
            '<td>' + fmt(expectedVals[k]) + '</td>' +
            '<td>' + fullNames[k] + '</td>' +
            '</tr>';
    }
}

// =====================================================================
// Tab 3: Roll vs Point-Buy Comparison
// =====================================================================

function renderComparison() {
    var budget = parseFloat(document.getElementById("rb-budget").value);
    var attempts = parseInt(document.getElementById("rb-attempts").value);
    var modeRadio = document.querySelector("input[name='rb-mode']:checked");
    var mode = modeRadio ? modeRadio.value : "full_set";

    var resultDiv = document.getElementById("rb-result");
    var errorDiv = document.getElementById("rb-error");

    resultDiv.innerHTML = "";
    errorDiv.textContent = "";
    errorDiv.classList.remove("visible");

    if (isNaN(budget) || budget < 0) {
        errorDiv.textContent = "Please enter a valid budget (>= 0).";
        errorDiv.classList.add("visible");
        return;
    }
    if (isNaN(attempts) || attempts < 1) {
        errorDiv.textContent = "Please enter a valid number of attempts (>= 1).";
        errorDiv.classList.add("visible");
        return;
    }

    try {
        var result = TRPG.compareRollVsBuy(budget, attempts, mode);
        var diff = result.difference();

        var html = "";

        // Mode header
        html += '<h3>' + (result.mode === "full_set" ? "Mode A — Best of K Full Sets" : "Mode B — Best per Formula Group") + '</h3>';

        // Key metrics
        html += '<div class="result-cards">';
        var deltaStr = (diff >= 0 ? "+" : "") + fmt(diff) + " vs budget";
        var deltaClass = diff > 0 ? "delta-positive" : (diff < 0 ? "delta-negative" : "");
        html += '<div class="card"><div class="card-label">Expected Best Total</div><div class="card-value accent">' + fmt(result.expectedBestTotal) + '</div><div class="card-delta ' + deltaClass + '">' + deltaStr + '</div></div>';
        html += '<div class="card"><div class="card-label">Point-Buy Budget</div><div class="card-value">' + fmt(result.pointBuyTotal) + '</div></div>';
        html += '<div class="card"><div class="card-label">Difference</div><div class="card-value ' + (diff > 0 ? "text-positive" : (diff < 0 ? "text-negative" : "")) + '">' + (diff >= 0 ? "+" : "") + fmt(diff) + '</div><div class="card-delta ' + (diff > 0 ? "delta-positive" : (diff < 0 ? "delta-negative" : "")) + '">' + (diff > 0 ? "Rolling wins!" : (diff < 0 ? "Buying wins!" : "Tie")) + '</div></div>';
        html += '</div>';

        // Recommendation
        if (diff > 0) {
            html += '<div class="msg msg-success">' + result.recommendation() + '</div>';
        } else if (diff < 0) {
            html += '<div class="msg msg-warning">' + result.recommendation() + '</div>';
        } else {
            html += '<div class="msg msg-info">' + result.recommendation() + '</div>';
        }

        // Detailed breakdown
        html += '<div class="breakdown">';
        if (result.mode === "full_set") {
            html += '<div class="breakdown-title">Mode A — Full Set Breakdown</div>';
            var singleSet = result.singleSetExpected || 0;
            html += '<div class="sub-grid">';
            html += '<div class="card"><div class="card-label">Single Set Expected</div><div class="card-value">' + fmt(singleSet) + '</div></div>';
            html += '<div class="card"><div class="card-label">Best of ' + result.attempts + ' Sets</div><div class="card-value accent">' + fmt(result.expectedBestTotal) + '</div><div class="card-delta">' + (result.expectedBestTotal - singleSet >= 0 ? "+" : "") + fmt(result.expectedBestTotal - singleSet) + ' over single set</div></div>';
            html += '</div>';
            html += '<p class="hint">Mode A is more constrained: you must take all 8 attributes from the same rolled set.</p>';
        } else {
            html += '<div class="breakdown-title">Mode B — Per Group Breakdown</div>';
            html += '<p><strong>Pool:</strong> 5 &times; 3d6 across ' + result.attempts + ' set(s) &rarr; <strong>' + result.group3d6PoolSize + ' rolls</strong>, pick best 5</p>';
            html += '<p><strong>Pool:</strong> 3 &times; 2d6+6 across ' + result.attempts + ' set(s) &rarr; <strong>' + result.group2d6PoolSize + ' rolls</strong>, pick best 3</p>';
            html += '<div class="sub-grid sub-grid-3">';
            html += '<div class="card"><div class="card-label">Best 3d6 Total</div><div class="card-value">' + fmt(result.group3d6ExpectedBest) + '</div></div>';
            html += '<div class="card"><div class="card-label">Best 2d6+6 Total</div><div class="card-value">' + fmt(result.group2d6ExpectedBest) + '</div></div>';
            html += '<div class="card"><div class="card-label">Combined Total</div><div class="card-value accent">' + fmt(result.expectedBestTotal) + '</div></div>';
            html += '</div>';
            html += '<p class="hint">Mode B gives more selection freedom: you independently optimize within each formula group.</p>';
        }
        html += '</div>';

        resultDiv.innerHTML = html;

    } catch (e) {
        errorDiv.textContent = e.message;
        errorDiv.classList.add("visible");
        resultDiv.innerHTML = "";
    }
}

// ---- Initialization ----

document.addEventListener("DOMContentLoaded", function() {
    // Tab buttons
    document.querySelectorAll(".tab-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            switchTab(this.getAttribute("data-tab"));
        });
    });

    // Expected Value — calculate button
    document.getElementById("ev-calc-btn").addEventListener("click", renderExpectedValue);
    // Calculate on Enter key
    document.getElementById("ev-input").addEventListener("keydown", function(e) {
        if (e.key === "Enter") renderExpectedValue();
    });

    // Roll vs Buy — compare button
    document.getElementById("rb-compare-btn").addEventListener("click", renderComparison);

    // Pre-render CoC reference (visible tab by default)
    renderCoCReference();
});

})();
