"use strict";

/*
 * Return Values in Event-Driven Repository Workflows
 *
 * This Node.js program models a Pull Request review pipeline through
 * explicit return contracts, asynchronous returns, discriminated results,
 * immutable state transitions, and event handlers.
 *
 * Run:
 *   node return_values.js
 */

const assert = require("node:assert/strict");

function success(value) {
  return Object.freeze({ ok: true, value });
}

function failure(code, message, details = {}) {
  return Object.freeze({
    ok: false,
    error: Object.freeze({ code, message, details }),
  });
}

function validatePullRequest(input) {
  if (!input || typeof input !== "object") {
    return failure("INVALID_INPUT", "Pull Request must be an object.");
  }

  const requiredStrings = [
    "id",
    "title",
    "sourceBranch",
    "targetBranch",
    "headSha",
  ];

  for (const field of requiredStrings) {
    if (typeof input[field] !== "string" || !input[field].trim()) {
      return failure("INVALID_FIELD", `${field} must be a non-empty string.`);
    }
  }

  if (input.sourceBranch === input.targetBranch) {
    return failure(
      "SAME_BRANCH",
      "Source and target branches must be different."
    );
  }

  if (!/^[a-f0-9]{7,40}$/i.test(input.headSha)) {
    return failure("INVALID_SHA", "headSha must be a hexadecimal commit ID.");
  }

  return success(
    Object.freeze({
      id: input.id.trim(),
      title: input.title.trim(),
      sourceBranch: input.sourceBranch,
      targetBranch: input.targetBranch,
      headSha: input.headSha.toLowerCase(),
      state: "open",
      draft: Boolean(input.draft),
      reviews: Object.freeze([]),
      checks: Object.freeze({}),
      conversationsResolved: true,
    })
  );
}

function transitionPullRequest(pullRequest, event) {
  if (!pullRequest || !event || typeof event.type !== "string") {
    return failure("INVALID_EVENT", "A Pull Request and event are required.");
  }

  switch (event.type) {
    case "mark_ready":
      if (pullRequest.state !== "open" || !pullRequest.draft) {
        return failure(
          "INVALID_TRANSITION",
          "Only an open draft Pull Request can become ready."
        );
      }
      return success(Object.freeze({ ...pullRequest, draft: false }));

    case "close":
      if (pullRequest.state !== "open") {
        return failure(
          "INVALID_TRANSITION",
          "Only an open Pull Request can be closed."
        );
      }
      return success(Object.freeze({ ...pullRequest, state: "closed" }));

    case "reopen":
      if (pullRequest.state !== "closed") {
        return failure(
          "INVALID_TRANSITION",
          "Only a closed Pull Request can be reopened."
        );
      }
      return success(Object.freeze({ ...pullRequest, state: "open" }));

    case "synchronize":
      if (pullRequest.state !== "open") {
        return failure(
          "INVALID_TRANSITION",
          "Only an open Pull Request can be synchronized."
        );
      }
      if (!/^[a-f0-9]{7,40}$/i.test(event.headSha || "")) {
        return failure("INVALID_SHA", "Synchronization requires a valid SHA.");
      }
      // A new head invalidates approvals tied to the previous commit.
      return success(
        Object.freeze({
          ...pullRequest,
          headSha: event.headSha.toLowerCase(),
          reviews: Object.freeze(
            pullRequest.reviews.filter(
              (review) => review.commitSha === event.headSha.toLowerCase()
            )
          ),
          checks: Object.freeze({}),
        })
      );

    case "resolve_conversations":
      if (pullRequest.state !== "open") {
        return failure(
          "INVALID_TRANSITION",
          "Conversations can only be updated on an open Pull Request."
        );
      }
      return success(
        Object.freeze({
          ...pullRequest,
          conversationsResolved: Boolean(event.resolved),
        })
      );

    default:
      return failure("UNKNOWN_EVENT", `Unsupported event: ${event.type}`);
  }
}

function submitReview(pullRequest, reviewer, state, body = "") {
  const validStates = new Set(["approved", "changes_requested", "commented"]);

  if (!pullRequest || pullRequest.state !== "open") {
    return failure("PR_NOT_OPEN", "Reviews require an open Pull Request.");
  }

  if (!reviewer || !reviewer.id || reviewer.id === pullRequest.authorId) {
    // Self-approval is rejected even if the caller marks the reviewer trusted.
    return failure("INELIGIBLE_REVIEWER", "Reviewer is not eligible.");
  }

  if (!validStates.has(state)) {
    return failure("INVALID_REVIEW_STATE", `Unsupported review state: ${state}`);
  }

  const review = Object.freeze({
    reviewerId: reviewer.id,
    state,
    body,
    commitSha: pullRequest.headSha,
    submittedAt: new Date().toISOString(),
  });

  // Replacing the review from the same reviewer avoids counting old decisions.
  const reviews = pullRequest.reviews
    .filter((item) => item.reviewerId !== reviewer.id)
    .concat(review);

  return success(
    Object.freeze({ ...pullRequest, reviews: Object.freeze(reviews) })
  );
}

function evaluateMergeEligibility(pullRequest, policy) {
  const reasons = [];

  if (!pullRequest || pullRequest.state !== "open") {
    reasons.push("Pull Request must be open.");
    return Object.freeze({ eligible: false, reasons: Object.freeze(reasons) });
  }

  if (pullRequest.draft) reasons.push("Draft Pull Requests cannot merge.");

  if (!policy || !Number.isInteger(policy.requiredApprovals)) {
    reasons.push("Approval policy is invalid.");
    return Object.freeze({ eligible: false, reasons: Object.freeze(reasons) });
  }

  const currentReviews = pullRequest.reviews.filter(
    (review) => review.commitSha === pullRequest.headSha
  );

  const latestByReviewer = new Map();
  for (const review of currentReviews) {
    latestByReviewer.set(review.reviewerId, review);
  }

  const currentReviewValues = [...latestByReviewer.values()];
  const changesRequested = currentReviewValues.some(
    (review) => review.state === "changes_requested"
  );

  const approvals = currentReviewValues.filter(
    (review) => review.state === "approved"
  ).length;

  if (changesRequested) {
    reasons.push("At least one current review requests changes.");
  }

  if (approvals < policy.requiredApprovals) {
    reasons.push(
      `Requires ${policy.requiredApprovals} approval(s); found ${approvals}.`
    );
  }

  for (const checkName of policy.requiredChecks || []) {
    if (pullRequest.checks[checkName] !== "success") {
      reasons.push(`Required status check is not successful: ${checkName}`);
    }
  }

  if (policy.requireResolvedConversations && !pullRequest.conversationsResolved) {
    reasons.push("Review conversations remain unresolved.");
  }

  return Object.freeze({
    eligible: reasons.length === 0,
    approvalCount: approvals,
    reasons: Object.freeze(reasons),
  });
}

async function runStatusCheck(name, implementation) {
  try {
    // Awaiting the returned promise turns rejection into a typed result.
    const value = await implementation();
    return success(Object.freeze({ name, state: "success", value }));
  } catch (error) {
    return failure("CHECK_FAILED", `${name} failed.`, {
      reason: error instanceof Error ? error.message : String(error),
    });
  }
}

async function collectChecks(checks) {
  // Promise.all preserves input order in the returned array.
  const results = await Promise.all(
    checks.map(({ name, implementation }) =>
      runStatusCheck(name, implementation)
    )
  );

  return results.reduce(
    (accumulator, result) => {
      if (result.ok) {
        accumulator[result.value.name] = result.value.state;
      } else {
        accumulator[result.error.details.name || result.error.code] = "failure";
      }
      return accumulator;
    },
    {}
  );
}

class RepositoryWorkflow {
  constructor(pullRequest, policy) {
    this.pullRequest = pullRequest;
    this.policy = policy;
    this.listeners = new Set();
  }

  subscribe(listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function.");
    }

    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  dispatch(event) {
    const outcome = transitionPullRequest(this.pullRequest, event);
    if (!outcome.ok) return outcome;

    this.pullRequest = outcome.value;

    // Listener failures do not roll back the already completed state change.
    for (const listener of this.listeners) {
      try {
        listener(Object.freeze({ type: event.type, pullRequest: this.pullRequest }));
      } catch (error) {
        process.emitWarning(
          `Workflow listener failed: ${
            error instanceof Error ? error.message : String(error)
          }`
        );
      }
    }

    return success(this.pullRequest);
  }

  eligibility() {
    return evaluateMergeEligibility(this.pullRequest, this.policy);
  }
}

async function main() {
  const created = validatePullRequest({
    id: "PR-418",
    title: "Add signed release manifest",
    sourceBranch: "feature/signed-manifest",
    targetBranch: "main",
    headSha: "a".repeat(40),
    draft: true,
  });

  assert.equal(created.ok, true);
  if (!created.ok) throw new Error(created.error.message);

  const workflow = new RepositoryWorkflow(created.value, {
    requiredApprovals: 2,
    requiredChecks: ["unit-tests", "security-scan"],
    requireResolvedConversations: true,
  });

  workflow.subscribe((event) => {
    console.log(`Event ${event.type}: ${event.pullRequest.id}`);
  });

  console.log("Draft merge eligibility:", workflow.eligibility());

  assert.equal(workflow.dispatch({ type: "mark_ready" }).ok, true);

  const invalidReview = submitReview(
    workflow.pullRequest,
    { id: "author" },
    "approved"
  );
  assert.equal(invalidReview.ok, false);

  let reviewed = submitReview(
    workflow.pullRequest,
    { id: "reviewer-ada" },
    "approved",
    "Manifest verification and error handling look correct."
  );
  assert.equal(reviewed.ok, true);
  if (!reviewed.ok) throw new Error(reviewed.error.message);
  workflow.pullRequest = reviewed.value;

  reviewed = submitReview(
    workflow.pullRequest,
    { id: "reviewer-lin" },
    "commented",
    "Consider the release audit implications."
  );
  assert.equal(reviewed.ok, true);
  if (!reviewed.ok) throw new Error(reviewed.error.message);
  workflow.pullRequest = reviewed.value;

  const checkResults = await Promise.all([
    runStatusCheck("unit-tests", async () => ({ passed: 147 })),
    runStatusCheck("security-scan", async () => {
      throw new Error("Critical dependency advisory");
    }),
  ]);

  const checkMap = {};
  for (const result of checkResults) {
    if (result.ok) {
      checkMap[result.value.name] = result.value.state;
    } else {
      checkMap["security-scan"] = "failure";
      console.log("Check error:", result.error);
    }
  }

  workflow.pullRequest = Object.freeze({
    ...workflow.pullRequest,
    checks: Object.freeze(checkMap),
  });

  console.log("Blocked eligibility:", workflow.eligibility());

  // A second independent reviewer approves the current commit.
  reviewed = submitReview(
    workflow.pullRequest,
    { id: "reviewer-grace" },
    "approved",
    "The change is suitable for merging."
  );
  assert.equal(reviewed.ok, true);
  if (!reviewed.ok) throw new Error(reviewed.error.message);
  workflow.pullRequest = reviewed.value;

  workflow.pullRequest = Object.freeze({
    ...workflow.pullRequest,
    checks: Object.freeze({
      "unit-tests": "success",
      "security-scan": "success",
    }),
  });

  console.log("Eligible after checks:", workflow.eligibility());

  const oldHead = workflow.pullRequest.headSha;
  const synchronized = workflow.dispatch({
    type: "synchronize",
    headSha: "b".repeat(40),
  });
  assert.equal(synchronized.ok, true);
  assert.notEqual(workflow.pullRequest.headSha, oldHead);

  console.log("Eligibility after new commits:", workflow.eligibility());

  const closed = workflow.dispatch({ type: "close" });
  assert.equal(closed.ok, true);
  assert.equal(workflow.dispatch({ type: "close" }).ok, false);
  assert.equal(workflow.dispatch({ type: "reopen" }).ok, true);

  console.log("Final Pull Request state:", workflow.pullRequest.state);
  console.log("All assertions passed.");
}

main().catch((error) => {
  console.error("Workflow failed:", error);
  process.exitCode = 1;
});
