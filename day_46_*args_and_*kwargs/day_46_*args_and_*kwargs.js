"use strict";

/*
 * Practical exploration of flexible function arguments in JavaScript.
 * The file focuses on repository workflow events, callback forwarding,
 * configuration precedence, and review-policy evaluation.
 *
 * Run with: node args_kwargs_workflow.js
 */

// JavaScript uses rest parameters to collect positional arguments into an array.
// Unlike Python's **kwargs, JavaScript does not have a dedicated keyword-argument
// syntax. Named options are conventionally passed as one object.
function collectCommitMessages(pullRequestNumber, ...messages) {
  if (!Number.isInteger(pullRequestNumber) || pullRequestNumber <= 0) {
    throw new TypeError("Pull request number must be a positive integer.");
  }
  if (!messages.every(
    message => typeof message === "string" && message.trim().length > 0
  )) {
    throw new TypeError("Every commit message must be a non-empty string.");
  }

  return {
    pullRequestNumber,
    messageCount: messages.length,
    messages
  };
}

function openPullRequest({
  title,
  sourceBranch,
  targetBranch,
  author,
  repository,
  draft = true,
  labels = [],
  reviewers = []
} = {}) {
  if (![title, sourceBranch, targetBranch, author, repository].every(
    value => typeof value === "string" && value.trim().length > 0
  )) {
    throw new TypeError("Required pull request fields must be non-empty strings.");
  }
  if (sourceBranch === targetBranch) {
    throw new Error("Source and target branches must differ.");
  }
  if (!Array.isArray(labels) || !Array.isArray(reviewers)) {
    throw new TypeError("Labels and reviewers must be arrays.");
  }

  return {
    title,
    sourceBranch,
    targetBranch,
    author,
    repository,
    draft: Boolean(draft),
    labels: [...labels],
    reviewers: [...reviewers],
    state: "open"
  };
}

// Object spread is the closest common JavaScript pattern to merging **kwargs.
// Later properties take precedence, so the order is a policy decision.
function mergeRepositorySettings(organization, repository) {
  return { ...organization, ...repository };
}

function validatePolicy({
  requiredApprovals = 2,
  requiredChecks = ["unit-tests"],
  requireResolvedConversations = true,
  dismissStaleApprovals = true,
  allowAuthorApproval = false
} = {}) {
  if (!Number.isInteger(requiredApprovals) || requiredApprovals < 0) {
    throw new TypeError("requiredApprovals must be a non-negative integer.");
  }
  if (
    !Array.isArray(requiredChecks) ||
    !requiredChecks.every(name => typeof name === "string" && name.trim())
  ) {
    throw new TypeError("requiredChecks must contain non-empty strings.");
  }

  return Object.freeze({
    requiredApprovals,
    requiredChecks: Object.freeze([...new Set(requiredChecks)]),
    requireResolvedConversations: Boolean(requireResolvedConversations),
    dismissStaleApprovals: Boolean(dismissStaleApprovals),
    allowAuthorApproval: Boolean(allowAuthorApproval)
  });
}

class PullRequestWorkflow {
  #listeners = new Map();
  #reviews = [];
  #checks = new Map();
  #conversations = new Map();

  constructor({ number, author, headSha, draft = true }) {
    if (!Number.isInteger(number) || number <= 0) {
      throw new TypeError("Invalid pull request number.");
    }
    if (![author, headSha].every(
      value => typeof value === "string" && value.trim()
    )) {
      throw new TypeError("Author and head SHA are required.");
    }

    this.number = number;
    this.author = author;
    this.headSha = headSha;
    this.draft = Boolean(draft);
    this.state = "open";
  }

  on(eventName, listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function.");
    }

    const listeners = this.#listeners.get(eventName) ?? new Set();
    listeners.add(listener);
    this.#listeners.set(eventName, listeners);

    // Returning an unsubscribe function makes listener lifetime explicit.
    return () => listeners.delete(listener);
  }

  #emit(eventName, payload) {
    for (const listener of this.#listeners.get(eventName) ?? []) {
      listener(Object.freeze({ eventName, number: this.number, ...payload }));
    }
  }

  markReady() {
    this.#assertOpen();
    if (!this.draft) return;
    this.draft = false;
    this.#emit("ready_for_review", { headSha: this.headSha });
  }

  submitReview({ reviewer, state, commitSha = this.headSha }) {
    this.#assertOpen();

    if (reviewer === this.author) {
      throw new Error("The author cannot approve their own pull request.");
    }
    if (!["approved", "changes_requested", "commented"].includes(state)) {
      throw new TypeError("Unsupported review state.");
    }
    if (commitSha !== this.headSha) {
      throw new Error("Review does not apply to the current head commit.");
    }

    this.#reviews.push({ reviewer, state, commitSha });
    this.#emit("review_submitted", { reviewer, state, commitSha });
  }

  setCheck(name, state) {
    this.#assertOpen();
    if (!name.trim() || !["passed", "failed", "pending"].includes(state)) {
      throw new TypeError("Invalid status check.");
    }
    this.#checks.set(name, state);
    this.#emit("status_check_updated", { name, state });
  }

  setConversation(conversationId, resolved) {
    this.#assertOpen();
    if (!conversationId.trim() || typeof resolved !== "boolean") {
      throw new TypeError("Invalid conversation state.");
    }
    this.#conversations.set(conversationId, resolved);
    this.#emit("conversation_updated", { conversationId, resolved });
  }

  synchronize(newHeadSha) {
    this.#assertOpen();
    if (!newHeadSha.trim() || newHeadSha === this.headSha) {
      throw new TypeError("A different, non-empty head SHA is required.");
    }

    const previousHead = this.headSha;
    this.headSha = newHeadSha;
    this.#checks.clear();

    // Reviews are retained as history. Eligibility logic determines whether
    // they still apply to the updated head, rather than deleting audit data.
    this.#emit("synchronized", { previousHead, headSha: newHeadSha });
  }

  evaluate(policy) {
    const blockers = [];

    if (this.state !== "open") blockers.push("pull request is not open");
    if (this.draft) blockers.push("pull request is still a draft");

    const latestByReviewer = new Map();
    for (const review of this.#reviews) {
      if (review.commitSha === this.headSha) {
        latestByReviewer.set(review.reviewer, review);
      }
    }

    const approvalCount = [...latestByReviewer.values()].filter(
      review => review.state === "approved"
    ).length;

    if (approvalCount < policy.requiredApprovals) {
      blockers.push("insufficient current approvals");
    }

    for (const requiredName of policy.requiredChecks) {
      if (this.#checks.get(requiredName) !== "passed") {
        blockers.push(`required check not passed: ${requiredName}`);
      }
    }

    if (
      policy.requireResolvedConversations &&
      [...this.#conversations.values()].some(resolved => !resolved)
    ) {
      blockers.push("unresolved review conversations");
    }

    return Object.freeze({
      number: this.number,
      mergeable: blockers.length === 0,
      approvalCount,
      blockers
    });
  }

  close() {
    this.#assertOpen();
    this.state = "closed";
    this.#emit("closed", {});
  }

  reopen() {
    if (this.state !== "closed") {
      throw new Error("Only a closed pull request can be reopened.");
    }
    this.state = "open";
    this.#emit("reopened", {});
  }

  #assertOpen() {
    if (this.state !== "open") {
      throw new Error("Operation requires an open pull request.");
    }
  }
}

// This higher-order function forwards any positional arguments and named
// options through a reusable asynchronous operation wrapper.
function withTiming(operationName, operation) {
  return async (...args) => {
    const startedAt = performance.now();
    try {
      return await operation(...args);
    } finally {
      const elapsed = performance.now() - startedAt;
      console.log(`${operationName} completed in ${elapsed.toFixed(2)} ms`);
    }
  };
}

async function publishAuditEvent(eventType, ...details) {
  // The variadic signature allows different event types to attach different
  // detail values without introducing a separate function for every event.
  await Promise.resolve();
  return { eventType, details, recordedAt: new Date().toISOString() };
}

async function main() {
  console.log("Commit collection:", collectCommitMessages(
    42,
    "Validate webhook signatures",
    "Add policy audit logging"
  ));

  const request = openPullRequest({
    title: "Enforce repository review policy",
    sourceBranch: "feature/review-policy",
    targetBranch: "main",
    author: "maya",
    repository: "platform-api",
    draft: false,
    labels: ["security", "governance"],
    reviewers: ["alex", "sam"]
  });
  console.log("Pull request:", request);

  const settings = mergeRepositorySettings(
    { requiredApprovals: 2, allowForcePush: false },
    { requiredApprovals: 3 }
  );
  console.log("Effective settings:", settings);

  const policy = validatePolicy({
    requiredApprovals: 2,
    requiredChecks: ["unit-tests", "security-scan"]
  });

  const workflow = new PullRequestWorkflow({
    number: 42,
    author: "maya",
    headSha: "a91c2ef",
    draft: true
  });

  const unsubscribe = workflow.on("review_submitted", event => {
    console.log("Review event:", event);
  });

  workflow.on("synchronized", event => {
    console.log("Source branch updated:", event.previousHead, "->", event.headSha);
  });

  workflow.markReady();
  workflow.submitReview({ reviewer: "alex", state: "approved" });
  workflow.submitReview({ reviewer: "sam", state: "approved" });
  workflow.setCheck("unit-tests", "passed");
  workflow.setCheck("security-scan", "passed");
  workflow.setConversation("discussion-17", true);

  console.log("Before source update:", workflow.evaluate(policy));

  workflow.synchronize("c814d02");
  console.log("After source update:", workflow.evaluate(policy));

  workflow.submitReview({ reviewer: "alex", state: "approved" });
  workflow.submitReview({ reviewer: "sam", state: "approved" });
  workflow.setCheck("unit-tests", "passed");
  workflow.setCheck("security-scan", "passed");

  console.log("After fresh reviews and checks:", workflow.evaluate(policy));
  unsubscribe();

  const timedPublish = withTiming("Audit publication", publishAuditEvent);
  console.log(await timedPublish("pull_request.merged", 42, "main"));

  try {
    workflow.submitReview({ reviewer: "maya", state: "approved" });
  } catch (error) {
    console.log("Rejected operation:", error.message);
  }

  workflow.close();
  workflow.reopen();
  console.log("Reopened state:", workflow.state);
}

main().catch(error => {
  console.error("Workflow failed:", error);
  process.exitCode = 1;
});
