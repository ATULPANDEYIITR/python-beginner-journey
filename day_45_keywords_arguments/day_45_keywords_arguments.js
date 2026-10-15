"use strict";

/*
 * Keyword arguments are not native named parameters in JavaScript.
 * JavaScript commonly represents the same design with an options object.
 * This program explores that distinction through an event-driven repository
 * governance workflow, immutable event snapshots, and explicit policy checks.
 */

const assert = require("node:assert/strict");

function heading(title) {
    console.log(`\n========== ${title} ==========`);
}

// Destructuring gives an options object named parameters with defaults.
// Object validation is explicit because JavaScript does not enforce types.
function createPullRequest({
    title,
    sourceBranch,
    targetBranch = "main",
    draft = false,
    reviewers = [],
} = {}) {
    if (typeof title !== "string" || title.trim() === "") {
        throw new TypeError("title must be a non-empty string");
    }

    if (
        typeof sourceBranch !== "string" ||
        !sourceBranch.startsWith("feature/")
    ) {
        throw new TypeError("sourceBranch must start with feature/");
    }

    if (
        typeof targetBranch !== "string" ||
        targetBranch.trim() === "" ||
        sourceBranch === targetBranch
    ) {
        throw new TypeError("Invalid target branch");
    }

    if (typeof draft !== "boolean") {
        throw new TypeError("draft must be a boolean");
    }

    if (
        !Array.isArray(reviewers) ||
        reviewers.some(
            (reviewer) =>
                typeof reviewer !== "string" || reviewer.trim() === ""
        )
    ) {
        throw new TypeError("reviewers must be non-empty strings");
    }

    return {
        id: `PR-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
        title: title.trim(),
        sourceBranch,
        targetBranch,
        draft,
        reviewers: [...new Set(reviewers)],
        state: draft ? "draft" : "open",
        commits: [],
        reviews: [],
        checks: {},
        conversations: [],
        events: [],
    };
}

function demonstrateOptionsObjects() {
    heading("Named configuration through options objects");

    const proposal = createPullRequest({
        title: "Enforce token audience validation",
        sourceBranch: "feature/token-audience",
        reviewers: ["Maya", "Daniel"],
        draft: true,
    });

    console.log(proposal);

    const defaultedProposal = createPullRequest({
        title: "Harden dependency checks",
        sourceBranch: "feature/dependency-checks",
    });

    console.log("Defaults:", {
        targetBranch: defaultedProposal.targetBranch,
        draft: defaultedProposal.draft,
    });

    assert.throws(
        () =>
            createPullRequest({
                title: "Invalid branch",
                sourceBranch: "hotfix/invalid",
            }),
        /sourceBranch/
    );

    assert.throws(
        () =>
            createPullRequest({
                title: "Wrong type",
                sourceBranch: "feature/type-check",
                draft: "false",
            }),
        /draft/
    );
}

// JavaScript rest parameters collect remaining positional arguments into an
// array. They do not collect named arguments as Python's **kwargs does.
function recordReview(reviewer, state, ...comments) {
    const validStates = new Set([
        "approved",
        "changes_requested",
        "commented",
    ]);

    if (!validStates.has(state)) {
        throw new RangeError(`Invalid review state: ${state}`);
    }

    return {
        reviewer,
        state,
        comments: comments.map((comment) => {
            if (typeof comment !== "string" || !comment.trim()) {
                throw new TypeError("Review comments must be non-empty strings");
            }
            return comment.trim();
        }),
    };
}

function demonstrateRestParameters() {
    heading("Rest parameters versus named options");

    console.log(
        recordReview(
            "Maya",
            "changes_requested",
            "Reject unsigned tokens",
            "Add a regression test"
        )
    );

    // An options object makes optional review settings explicit.
    function submitReview(
        reviewer,
        { state, commitSha, dismissPrevious = false } = {}
    ) {
        if (!reviewer.trim()) {
            throw new TypeError("Reviewer is required");
        }

        if (!/^[a-f0-9]{7,40}$/.test(commitSha ?? "")) {
            throw new TypeError("A valid lowercase commit SHA is required");
        }

        if (typeof dismissPrevious !== "boolean") {
            throw new TypeError("dismissPrevious must be boolean");
        }

        return { reviewer, state, commitSha, dismissPrevious };
    }

    console.log(
        submitReview("Daniel", {
            state: "approved",
            commitSha: "a1b2c3d",
        })
    );
}

// Spread syntax expands objects. A later object wins on duplicate properties.
// Explicit allowlists prevent arbitrary input from overriding core settings.
const PROTECTION_FIELDS = new Set([
    "requiredApprovals",
    "requiredChecks",
    "dismissStaleReviews",
    "requireLinearHistory",
    "restrictPushes",
    "allowForcePush",
    "allowDeletion",
    "requireConversationResolution",
    "enforceForAdministrators",
    "allowBypass",
]);

function configureProtection(branch, overrides = {}) {
    if (typeof branch !== "string" || !branch.trim()) {
        throw new TypeError("A protected branch name is required");
    }

    if (
        overrides === null ||
        typeof overrides !== "object" ||
        Array.isArray(overrides)
    ) {
        throw new TypeError("Overrides must be a plain configuration object");
    }

    const unknown = Object.keys(overrides).filter(
        (key) => !PROTECTION_FIELDS.has(key)
    );

    if (unknown.length) {
        throw new TypeError(`Unknown policy fields: ${unknown.join(", ")}`);
    }

    const policy = {
        branch,
        requiredApprovals: 2,
        requiredChecks: ["unit-tests", "lint"],
        dismissStaleReviews: true,
        requireLinearHistory: true,
        restrictPushes: true,
        allowForcePush: false,
        allowDeletion: false,
        requireConversationResolution: true,
        enforceForAdministrators: true,
        allowBypass: false,
        ...overrides,
    };

    if (
        !Number.isInteger(policy.requiredApprovals) ||
        policy.requiredApprovals < 0
    ) {
        throw new TypeError("requiredApprovals must be a non-negative integer");
    }

    if (
        !Array.isArray(policy.requiredChecks) ||
        policy.requiredChecks.some(
            (check) => typeof check !== "string" || !check.trim()
        )
    ) {
        throw new TypeError("requiredChecks must contain valid check names");
    }

    for (const field of [
        "dismissStaleReviews",
        "requireLinearHistory",
        "restrictPushes",
        "allowForcePush",
        "allowDeletion",
        "requireConversationResolution",
        "enforceForAdministrators",
        "allowBypass",
    ]) {
        if (typeof policy[field] !== "boolean") {
            throw new TypeError(`${field} must be boolean`);
        }
    }

    policy.requiredChecks = [...new Set(policy.requiredChecks)];
    return Object.freeze(policy);
}

function demonstrateObjectComposition() {
    heading("Object composition and policy validation");

    const organizationDefaults = {
        requiredApprovals: 2,
        requiredChecks: ["unit-tests", "lint"],
        allowForcePush: false,
    };

    const serviceOverrides = {
        ...organizationDefaults,
        requiredApprovals: 3,
        requiredChecks: ["unit-tests", "security-scan"],
    };

    console.log(
        configureProtection("main", {
            ...serviceOverrides,
            enforceForAdministrators: true,
        })
    );

    assert.throws(
        () => configureProtection("main", { allowForcePuh: true }),
        /Unknown policy fields/
    );
}

// An event emitter models lifecycle changes independently of review decisions.
// Event listeners receive a consistent event payload, not shared mutable state.
class PullRequestWorkflow {
    #pullRequest;
    #listeners = new Map();

    constructor(pullRequest, policy) {
        this.#pullRequest = structuredClone(pullRequest);
        this.policy = policy;
    }

    get snapshot() {
        return structuredClone(this.#pullRequest);
    }

    on(eventName, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("Listener must be a function");
        }

        const listeners = this.#listeners.get(eventName) ?? [];
        listeners.push(listener);
        this.#listeners.set(eventName, listeners);

        return () => {
            this.#listeners.set(
                eventName,
                listeners.filter((registered) => registered !== listener)
            );
        };
    }

    #emit(eventName, details = {}) {
        const event = Object.freeze({
            eventName,
            pullRequestId: this.#pullRequest.id,
            occurredAt: new Date().toISOString(),
            details: structuredClone(details),
        });

        for (const listener of this.#listeners.get(eventName) ?? []) {
            listener(event);
        }

        this.#pullRequest.events.push(event);
    }

    #requireOpen() {
        if (this.#pullRequest.state !== "open") {
            throw new Error(
                `Operation requires an open Pull Request; state is ${this.#pullRequest.state}`
            );
        }
    }

    markReady() {
        if (this.#pullRequest.state !== "draft") {
            throw new Error("Only a draft can be marked ready");
        }

        this.#pullRequest.state = "open";
        this.#emit("ready_for_review");
    }

    addCommit(sha, changedFiles) {
        this.#requireOpen();

        if (!/^[a-f0-9]{7,40}$/.test(sha)) {
            throw new TypeError("Invalid commit SHA");
        }

        if (!Array.isArray(changedFiles) || changedFiles.length === 0) {
            throw new TypeError("A commit must identify changed files");
        }

        if (this.#pullRequest.commits.some((commit) => commit.sha === sha)) {
            throw new Error("Duplicate commit");
        }

        this.#pullRequest.commits.push({
            sha,
            changedFiles: [...new Set(changedFiles)],
        });

        // New commits make previous approvals stale when policy requires
        // approval of the latest reviewed revision.
        if (this.policy.dismissStaleReviews) {
            this.#pullRequest.reviews = this.#pullRequest.reviews.map(
                (review) => ({
                    ...review,
                    dismissed: review.dismissed || review.commitSha !== sha,
                })
            );
        }

        this.#emit("commit_added", { sha, changedFiles });
    }

    addReview({ reviewer, state, commitSha, isEligible = true }) {
        this.#requireOpen();

        if (!isEligible) {
            throw new Error(`${reviewer} is not eligible to review this change`);
        }

        if (!this.#pullRequest.commits.some((commit) => commit.sha === commitSha)) {
            throw new Error("Review must refer to a commit in this Pull Request");
        }

        if (!["approved", "changes_requested", "commented"].includes(state)) {
            throw new RangeError("Unsupported review state");
        }

        const previous = this.#pullRequest.reviews.find(
            (review) => review.reviewer === reviewer && !review.dismissed
        );

        if (previous) {
            previous.dismissed = true;
        }

        this.#pullRequest.reviews.push({
            reviewer,
            state,
            commitSha,
            dismissed: false,
        });

        this.#emit("review_submitted", { reviewer, state, commitSha });
    }

    setCheck(name, status) {
        this.#requireOpen();

        if (!["success", "failure", "pending"].includes(status)) {
            throw new RangeError("Unsupported status-check result");
        }

        this.#pullRequest.checks[name] = status;
        this.#emit("status_check_updated", { name, status });
    }

    addConversation(id, resolved = false) {
        this.#requireOpen();

        if (!id.trim()) {
            throw new TypeError("Conversation ID is required");
        }

        if (this.#pullRequest.conversations.some((item) => item.id === id)) {
            throw new Error("Conversation ID must be unique");
        }

        this.#pullRequest.conversations.push({ id, resolved });
        this.#emit("conversation_added", { id, resolved });
    }

    resolveConversation(id) {
        this.#requireOpen();

        const conversation = this.#pullRequest.conversations.find(
            (item) => item.id === id
        );

        if (!conversation) {
            throw new Error(`Conversation not found: ${id}`);
        }

        conversation.resolved = true;
        this.#emit("conversation_resolved", { id });
    }

    evaluate() {
        const pr = this.#pullRequest;
        const reasons = [];

        if (pr.state !== "open") {
            reasons.push("Pull Request is not open");
        }

        if (pr.commits.length === 0) {
            reasons.push("No commits are present");
        }

        const latestSha = pr.commits.at(-1)?.sha;

        const activeReviews = pr.reviews.filter(
            (review) =>
                !review.dismissed &&
                review.commitSha === latestSha &&
                pr.reviewers.includes(review.reviewer)
        );

        const latestByReviewer = new Map();
        for (const review of activeReviews) {
            latestByReviewer.set(review.reviewer, review);
        }

        const reviews = [...latestByReviewer.values()];

        if (reviews.some((review) => review.state === "changes_requested")) {
            reasons.push("A current eligible reviewer requested changes");
        }

        const approvals = reviews.filter(
            (review) => review.state === "approved"
        ).length;

        if (approvals < this.policy.requiredApprovals) {
            reasons.push(
                `Requires ${this.policy.requiredApprovals} approvals; received ${approvals}`
            );
        }

        for (const requiredCheck of this.policy.requiredChecks) {
            if (pr.checks[requiredCheck] !== "success") {
                reasons.push(`Required check is not successful: ${requiredCheck}`);
            }
        }

        if (
            this.policy.requireConversationResolution &&
            pr.conversations.some((conversation) => !conversation.resolved)
        ) {
            reasons.push("Unresolved review conversations remain");
        }

        return {
            eligible: reasons.length === 0,
            approvals,
            latestCommit: latestSha ?? null,
            reasons,
        };
    }

    merge({ actor, strategy = "squash" } = {}) {
        if (!actor?.trim()) {
            throw new TypeError("Merge actor is required");
        }

        if (!["merge", "squash", "rebase"].includes(strategy)) {
            throw new RangeError("Unsupported merge strategy");
        }

        const evaluation = this.evaluate();

        if (!evaluation.eligible) {
            throw new Error(
                `Merge blocked: ${evaluation.reasons.join("; ")}`
            );
        }

        this.#pullRequest.state = "merged";
        this.#pullRequest.merge = {
            actor,
            strategy,
            commitSha: evaluation.latestCommit,
        };

        this.#emit("merged", this.#pullRequest.merge);
        return structuredClone(this.#pullRequest.merge);
    }
}

function demonstrateWorkflow() {
    heading("Event-driven Pull Request lifecycle");

    const policy = configureProtection("main", {
        requiredApprovals: 2,
        requiredChecks: ["unit-tests", "security-scan"],
        dismissStaleReviews: true,
        requireConversationResolution: true,
    });

    const proposal = createPullRequest({
        title: "Enforce signed deployment artifacts",
        sourceBranch: "feature/signed-artifacts",
        targetBranch: "main",
        reviewers: ["Maya", "Daniel"],
    });

    const workflow = new PullRequestWorkflow(proposal, policy);

    workflow.on("review_submitted", (event) => {
        console.log("Review event:", event.details);
    });

    workflow.on("merged", (event) => {
        console.log("Merge event:", event.details);
    });

    workflow.addCommit("a1b2c3d", ["src/signature.js", "test/signature.test.js"]);
    workflow.addConversation("security-comment-17");
    workflow.addReview({
        reviewer: "Maya",
        state: "approved",
        commitSha: "a1b2c3d",
    });
    workflow.addReview({
        reviewer: "Daniel",
        state: "approved",
        commitSha: "a1b2c3d",
    });
    workflow.setCheck("unit-tests", "success");
    workflow.setCheck("security-scan", "success");

    console.log("Before resolving discussion:", workflow.evaluate());

    workflow.resolveConversation("security-comment-17");

    console.log("Before merge:", workflow.evaluate());

    // Adding a new commit makes earlier approvals stale under this policy.
    workflow.addCommit("b2c3d4e", ["src/signature.js"]);

    assert.equal(workflow.evaluate().eligible, false);

    workflow.addReview({
        reviewer: "Maya",
        state: "approved",
        commitSha: "b2c3d4e",
    });

    workflow.addReview({
        reviewer: "Daniel",
        state: "approved",
        commitSha: "b2c3d4e",
    });

    console.log("After fresh approvals:", workflow.evaluate());

    console.log(
        "Merge result:",
        workflow.merge({ actor: "release-maintainer", strategy: "squash" })
    );

    assert.throws(
        () => workflow.merge({ actor: "release-maintainer" }),
        /not open/
    );
}

async function demonstrateAsyncPolicyEvaluation() {
    heading("Asynchronous status-check evaluation");

    // Promise.all permits independent checks to run concurrently. A rejection
    // must be treated as a failed evaluation rather than as a successful check.
    const checks = [
        Promise.resolve({ name: "unit-tests", status: "success" }),
        Promise.resolve({ name: "security-scan", status: "success" }),
        Promise.resolve({ name: "lint", status: "success" }),
    ];

    const results = await Promise.all(checks);
    const failed = results.filter((result) => result.status !== "success");

    console.log({ results, eligible: failed.length === 0 });

    try {
        await Promise.all([
            Promise.resolve({ name: "unit-tests", status: "success" }),
            Promise.reject(new Error("Security scanner timed out")),
        ]);
    } catch (error) {
        console.log("Infrastructure failure blocks the evaluation:", error.message);
    }
}

async function main() {
    demonstrateOptionsObjects();
    demonstrateRestParameters();
    demonstrateObjectComposition();
    demonstrateWorkflow();
    await demonstrateAsyncPolicyEvaluation();

    heading("Execution completed");
}

main().catch((error) => {
    console.error("Workflow failed:", error);
    process.exitCode = 1;
});
