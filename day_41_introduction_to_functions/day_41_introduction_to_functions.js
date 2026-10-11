"use strict";

/*
 * Introduction to Functions
 * Node.js implementation emphasizing callbacks, closures, promises,
 * asynchronous composition, validation, and reusable domain operations.
 *
 * Run: node introduction-to-functions.js
 */

const assert = require("node:assert/strict");
const { performance } = require("node:perf_hooks");

function section(title) {
    console.log(`\n${"=".repeat(68)}\n${title}\n${"=".repeat(68)}`);
}

// A pure function produces a result without modifying external state.
function calculateShipping(weightKg, distanceKm) {
    if (!Number.isFinite(weightKg) || weightKg < 0) {
        throw new RangeError("Weight must be finite and non-negative.");
    }
    if (!Number.isFinite(distanceKm) || distanceKm < 0) {
        throw new RangeError("Distance must be finite and non-negative.");
    }
    return Math.round((40 + weightKg * 12 + distanceKm * 0.8) * 100) / 100;
}

// Destructuring gives a function a readable configuration-object interface.
function calculateSubscription({
    monthlyFee,
    months,
    discountRate = 0
}) {
    if (!Number.isFinite(monthlyFee) || monthlyFee < 0) {
        throw new RangeError("Monthly fee must be non-negative.");
    }
    if (!Number.isInteger(months) || months < 1) {
        throw new RangeError("Months must be a positive integer.");
    }
    if (!Number.isFinite(discountRate) || discountRate < 0 || discountRate > 1) {
        throw new RangeError("Discount rate must be between zero and one.");
    }
    return Number((monthlyFee * months * (1 - discountRate)).toFixed(2));
}

// Rest parameters gather an arbitrary number of numeric arguments.
function average(...values) {
    if (values.length === 0) {
        throw new RangeError("At least one value is required.");
    }
    if (values.some(value => !Number.isFinite(value))) {
        throw new TypeError("Every value must be finite.");
    }
    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

// The returned function remembers the prefix supplied when it was created.
function createLogger(prefix) {
    return function log(message, details = {}) {
        console.log(`[${prefix}] ${message}`, details);
    };
}

// Higher-order functions receive behavior as an argument.
function mapWithValidation(values, transform) {
    if (!Array.isArray(values)) {
        throw new TypeError("Values must be an array.");
    }
    if (typeof transform !== "function") {
        throw new TypeError("Transform must be a function.");
    }
    return values.map((value, index) => transform(value, index));
}

// Function factories can encode reusable policies without global variables.
function createDiscountPolicy(rate) {
    if (!Number.isFinite(rate) || rate < 0 || rate > 1) {
        throw new RangeError("Invalid discount rate.");
    }
    return amount => {
        if (!Number.isFinite(amount) || amount < 0) {
            throw new RangeError("Amount must be non-negative.");
        }
        return Number((amount * (1 - rate)).toFixed(2));
    };
}

// A wrapper adds timing behavior while preserving the wrapped function's result.
function withTiming(operation, label = operation.name || "anonymous") {
    return function timedOperation(...args) {
        const start = performance.now();
        try {
            return operation(...args);
        } finally {
            console.log(`${label}: ${(performance.now() - start).toFixed(3)} ms`);
        }
    };
}

// Closures can implement a small stateful abstraction with a controlled interface.
function createSequence(start = 0) {
    if (!Number.isSafeInteger(start)) {
        throw new RangeError("Start must be a safe integer.");
    }
    let current = start;
    return Object.freeze({
        next() {
            if (current === Number.MAX_SAFE_INTEGER) {
                throw new RangeError("Sequence exhausted.");
            }
            current += 1;
            return current;
        },
        current() {
            return current;
        }
    });
}

// An explicit state transition is safer than arbitrary changes to an object.
const pullRequestTransitions = Object.freeze({
    draft: new Set(["ready", "closed"]),
    ready: new Set(["draft", "closed", "merged"]),
    closed: new Set(["ready"]),
    merged: new Set()
});

class PullRequest {
    constructor(id, sourceBranch, targetBranch) {
        if (!Number.isInteger(id) || id <= 0) {
            throw new RangeError("Pull request ID must be positive.");
        }
        if (!sourceBranch || !targetBranch || sourceBranch === targetBranch) {
            throw new Error("Distinct source and target branches are required.");
        }
        this.id = id;
        this.sourceBranch = sourceBranch;
        this.targetBranch = targetBranch;
        this.state = "draft";
        this.reviews = [];
        this.checks = new Map();
        this.commits = [];
        this.events = [];
    }

    transition(nextState) {
        const permitted = pullRequestTransitions[this.state];
        if (!permitted || !permitted.has(nextState)) {
            throw new Error(`Invalid transition: ${this.state} -> ${nextState}`);
        }
        this.state = nextState;
        this.events.push({ type: "state_changed", state: nextState });
    }

    addCommit(sha, message) {
        if (this.state === "closed" || this.state === "merged") {
            throw new Error("Cannot add commits to a closed or merged request.");
        }
        if (!/^[a-f0-9]{7,40}$/i.test(sha) || !message.trim()) {
            throw new Error("A valid commit identifier and message are required.");
        }
        this.commits.push({ sha, message });
        this.events.push({ type: "commit_added", sha });
    }

    submitReview(reviewer, decision, commitSha) {
        if (this.state !== "ready") {
            throw new Error("Reviews can be submitted only on ready requests.");
        }
        if (!reviewer || reviewer === "author") {
            throw new Error("A distinct reviewer identity is required.");
        }
        if (!["approved", "changes_requested", "commented"].includes(decision)) {
            throw new Error("Unsupported review decision.");
        }
        if (!this.commits.some(commit => commit.sha === commitSha)) {
            throw new Error("Review must refer to a commit in this request.");
        }
        this.reviews.push({ reviewer, decision, commitSha });
        this.events.push({ type: "review_submitted", reviewer, decision });
    }

    setCheck(name, status) {
        if (!name.trim() || !["pending", "success", "failure"].includes(status)) {
            throw new Error("Invalid status check.");
        }
        this.checks.set(name, status);
        this.events.push({ type: "check_updated", name, status });
    }

    mergeEligibility(policy) {
        const latestReviewByReviewer = new Map();
        for (const review of this.reviews) {
            latestReviewByReviewer.set(review.reviewer, review);
        }

        const approvals = [...latestReviewByReviewer.values()].filter(
            review => review.decision === "approved"
                && review.commitSha === this.commits.at(-1)?.sha
                && review.reviewer !== policy.author
                && !policy.ineligibleReviewers.has(review.reviewer)
        );

        const latestChangesRequest = [...latestReviewByReviewer.values()].some(
            review => review.decision === "changes_requested"
                && review.commitSha === this.commits.at(-1)?.sha
        );

        const failedChecks = policy.requiredChecks.filter(
            name => this.checks.get(name) !== "success"
        );

        const violations = [];
        if (this.state !== "ready") violations.push("Request is not ready.");
        if (this.commits.length === 0) violations.push("No commits are present.");
        if (approvals.length < policy.requiredApprovals) {
            violations.push(`Requires ${policy.requiredApprovals} eligible approval(s).`);
        }
        if (latestChangesRequest) violations.push("Changes are requested.");
        if (failedChecks.length) {
            violations.push(`Unsuccessful required checks: ${failedChecks.join(", ")}`);
        }

        return {
            eligible: violations.length === 0,
            approvals: approvals.map(review => review.reviewer),
            violations
        };
    }

    merge(policy) {
        const evaluation = this.mergeEligibility(policy);
        if (!evaluation.eligible) {
            throw new Error(`Merge blocked: ${evaluation.violations.join(" ")}`);
        }
        this.transition("merged");
        this.events.push({ type: "merged", targetBranch: this.targetBranch });
    }
}

// Promises model operations that may finish later or fail independently.
function simulateStatusCheck(name, delayMs, outcome = "success") {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (outcome === "failure") {
                reject(new Error(`${name} failed`));
            } else {
                resolve({ name, status: outcome });
            }
        }, delayMs);
    });
}

async function runChecksConcurrently(checkDefinitions) {
    // Promise.all rejects on any failure; allSettled preserves every result.
    const results = await Promise.allSettled(
        checkDefinitions.map(definition =>
            simulateStatusCheck(
                definition.name,
                definition.delayMs,
                definition.outcome
            )
        )
    );

    return results.map((result, index) => ({
        name: checkDefinitions[index].name,
        status: result.status === "fulfilled"
            ? result.value.status
            : "failure",
        error: result.status === "rejected" ? result.reason.message : null
    }));
}

async function main() {
    section("Basic function calls");
    console.log("Shipping:", calculateShipping(2.5, 120));
    console.log("Subscription:", calculateSubscription({
        monthlyFee: 799,
        months: 12,
        discountRate: 0.1
    }));
    console.log("Average:", average(76, 84, 91));

    section("Closures and higher-order functions");
    const audit = createLogger("ORDER-AUDIT");
    audit("Subscription calculated", { amount: 8629.2 });
    console.log("Double values:", mapWithValidation([2, 4, 6], value => value * 2));
    const employeeDiscount = createDiscountPolicy(0.15);
    console.log("Employee price:", employeeDiscount(1200));
    console.log("Sequence:", createSequence(40).next());

    section("Measured operation");
    const measuredSum = withTiming(
        values => values.reduce((sum, value) => sum + value, 0),
        "sum-array"
    );
    console.log("Sum:", measuredSum(Array.from({ length: 10000 }, (_, i) => i)));

    section("Pull Request review and policy workflow");
    const request = new PullRequest(42, "feature/payment-validation", "main");
    request.addCommit("a1b2c3d", "Validate payment amounts");
    request.transition("ready");

    const policy = {
        author: "author",
        requiredApprovals: 2,
        requiredChecks: ["tests", "security-scan"],
        ineligibleReviewers: new Set(["author", "bot-account"])
    };

    request.submitReview("reviewer-alex", "approved", "a1b2c3d");
    request.submitReview("reviewer-priya", "approved", "a1b2c3d");

    const checkResults = await runChecksConcurrently([
        { name: "tests", delayMs: 10, outcome: "success" },
        { name: "security-scan", delayMs: 15, outcome: "success" },
        { name: "documentation", delayMs: 5, outcome: "failure" }
    ]);

    for (const check of checkResults) {
        request.setCheck(check.name, check.status);
        console.log(check);
    }

    const evaluation = request.mergeEligibility(policy);
    console.log("Merge eligibility:", evaluation);

    assert.equal(evaluation.eligible, true);
    request.merge(policy);
    console.log("Final request state:", request.state);
    console.log("Recorded events:", request.events);

    section("Function contracts and edge cases");
    assert.throws(() => average(), RangeError);
    assert.throws(() => calculateShipping(-1, 20), RangeError);
    assert.throws(() => request.addCommit("1234567", "Late change"), /Cannot add commits/);

    const invalidTransitions = new PullRequest(43, "feature/report", "main");
    assert.throws(() => invalidTransitions.transition("merged"), /Invalid transition/);

    const failedChecks = await runChecksConcurrently([
        { name: "unit-tests", delayMs: 1, outcome: "failure" },
        { name: "lint", delayMs: 1, outcome: "success" }
    ]);
    assert.equal(failedChecks.find(check => check.name === "unit-tests").status, "failure");

    console.log("All assertions passed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
