/* Probability distributions for sums of dice and order statistics.
 * All calculations use exact probability math — no random simulation. */
(function(TRPG) {

// ---- Binomial coefficient ----

function comb(n, k) {
    if (k < 0 || k > n) return 0;
    if (k === 0 || k === n) return 1;
    // Use smaller k for efficiency
    if (k > n - k) k = n - k;
    var result = 1;
    for (var i = 0; i < k; i++) {
        result = result * (n - i) / (i + 1);
    }
    return result;
}

// ---- Distribution helpers ----

function mean(dist) {
    var s = 0;
    for (var v in dist) {
        if (dist.hasOwnProperty(v)) s += parseInt(v) * dist[v];
    }
    return s;
}

function sortedKeys(dist) {
    return Object.keys(dist).map(Number).sort(function(a, b) { return a - b; });
}

// ---- Dice sum distribution (PMF) ----

TRPG.diceSumDistribution = function(count, sides) {
    // Start with one die: uniform distribution over 1..sides
    var dist = {};
    var p = 1.0 / sides;
    for (var i = 1; i <= sides; i++) {
        dist[i] = p;
    }
    // Convolve additional dice
    for (var d = 1; d < count; d++) {
        var newDist = {};
        for (var existingSum in dist) {
            if (!dist.hasOwnProperty(existingSum)) continue;
            var existingProb = dist[existingSum];
            var es = parseInt(existingSum);
            for (var face = 1; face <= sides; face++) {
                var newSum = es + face;
                newDist[newSum] = (newDist[newSum] || 0) + existingProb * p;
            }
        }
        dist = newDist;
    }
    return dist;
};

TRPG.diceSumDistributionWithModifier = function(count, sides, modifier) {
    var base = TRPG.diceSumDistribution(count, sides);
    if (modifier === 0) return base;
    var result = {};
    for (var k in base) {
        if (base.hasOwnProperty(k)) {
            result[parseInt(k) + modifier] = base[k];
        }
    }
    return result;
};

// ---- Cumulative distribution (CDF) ----

TRPG.cumulativeDistribution = function(dist) {
    var keys = sortedKeys(dist);
    var cdf = {};
    var cumulative = 0;
    for (var i = 0; i < keys.length; i++) {
        cumulative += dist[keys[i]];
        cdf[keys[i]] = cumulative;
    }
    return cdf;
};

// ---- Expected maximum of K draws ----

TRPG.expectedMaxOfK = function(dist, k) {
    if (k < 1) throw new Error("Number of attempts must be at least 1, got " + k + ".");

    var keys = sortedKeys(dist);

    // For k=1, expected max = expected value of the distribution
    if (k === 1) return mean(dist);

    var cdf = TRPG.cumulativeDistribution(dist);

    // P(max <= x) = P(X <= x)^k
    var expected = 0;
    var prevCdf = 0;
    for (var i = 0; i < keys.length; i++) {
        var x = keys[i];
        var maxCdfX = Math.pow(cdf[x], k);
        var pMaxEqX = maxCdfX - prevCdf;
        expected += x * pMaxEqX;
        prevCdf = maxCdfX;
    }
    return expected;
};

// ---- Expected sum of top K out of N draws ----

TRPG.expectedSumOfTopK = function(dist, n, k) {
    if (k < 1) throw new Error("k must be >= 1, got " + k + ".");
    if (n < k) throw new Error("n (" + n + ") must be >= k (" + k + ").");

    var keys = sortedKeys(dist);
    if (keys.length === 0) throw new Error("Distribution cannot be empty.");

    // When k == 1, delegate to expectedMaxOfK
    if (k === 1) return TRPG.expectedMaxOfK(dist, n);

    // When n == k, we always take all draws: expected sum = n * mean
    if (n === k) return n * mean(dist);

    var cdf = TRPG.cumulativeDistribution(dist);
    var expectedSum = 0;

    // For each of the top k order statistics (j = n-k+1 ... n)
    for (var j = n - k + 1; j <= n; j++) {
        var prevCdfVal = 0;
        var orderExpected = 0;

        for (var vi = 0; vi < keys.length; vi++) {
            var v = keys[vi];
            var F = cdf[v];
            var cdfAtV = 0;

            if (F === 0) {
                cdfAtV = 0;
            } else if (F === 1) {
                cdfAtV = 1;
            } else {
                for (var i = j; i <= n; i++) {
                    cdfAtV += comb(n, i) * Math.pow(F, i) * Math.pow(1 - F, n - i);
                }
            }

            var pEqV = cdfAtV - prevCdfVal;
            if (pEqV > 0) {
                orderExpected += v * pEqV;
            }
            prevCdfVal = cdfAtV;
        }

        expectedSum += orderExpected;
    }

    return expectedSum;
};

// ---- Convolution of multiple distributions ----

TRPG.convolveDistributions = function(dists) {
    if (!dists || dists.length === 0) return {0: 1};

    var result = dists[0];
    for (var di = 1; di < dists.length; di++) {
        var newResult = {};
        var dist = dists[di];
        for (var v1 in result) {
            if (!result.hasOwnProperty(v1)) continue;
            var p1 = result[v1];
            for (var v2 in dist) {
                if (!dist.hasOwnProperty(v2)) continue;
                var p2 = dist[v2];
                var newVal = parseInt(v1) + parseInt(v2);
                newResult[newVal] = (newResult[newVal] || 0) + p1 * p2;
            }
        }
        result = newResult;
    }
    return result;
};

})(window.TRPG = window.TRPG || {});
