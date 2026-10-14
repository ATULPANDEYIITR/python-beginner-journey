"use strict";

/*
 * Default arguments in a repository-governance workflow.
 * Run with Node.js 18 or later. No third-party packages are required.
 */

const DEFAULT_BASE_BRANCH = "main";
const DEFAULT_REQUIRED_APPROVALS = 2;
const TERMINAL_STATES = new Set(["merged", "closed"]);

function requireText(value, field) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new TypeError(`${field} must be a non-empty string.`);
  }
  return value.trim();
}

function createPullRequest({
  number,
  title,
  sourceBranch,
  targetBranch = DEFAULT_BASE_BRANCH,
  draft = true,
  labels = [],
} = {}) {
  if (!Number.isInteger(number) || number <= 0) {
    throw new TypeError("Pull request number must be a positive integer.");
  }

  requireText(title, "title");
  requireText(sourceBranch, "sourceBranch");
  requireText(targetBranch, "targetBranch");

  if (sourceBranch === targetBranch) {
    throw new Error("Source and target branches must differ.");
  }
  if (typeof draft !== "boolean") {
    throw new TypeError("draft must be a boolean.");
  }
  if (!Array.isArray(labels) || labels.some(label => typeof label !== "string")) {
    throw new TypeError("labels must be an array of strings.");
  }

  // Copy caller-owned collections so later external mutations cannot
  // silently alter the pull request's initial state.
  return {
    number,
    title: title.trim(),
    sourceBranch: sourceBranch.trim(),
    targetBranch: targetBranch.trim(),
    draft,
    labels: [...new Set(labels.map(label => label.trim().toLowerCase()).filter(Boolean))],
    commits: [],
    reviews: [],
    checks: new Map(),
    conversations: [],
    state: "open",
    revision: 0,
  };
}

function addCommit(pullRequest, sha, message) {
  if (pullRequest.state !== "open") {
    throw new Error("Commits can only be added to an open pull request.");
  }

  requireText(sha, "sha");
  requireText(message, "message");

  if (pullRequest.commits.some(commit => commit.sha === sha)) {
    throw new Error(`Duplicate commit: ${sha}`);
  }

  pullRequest.commits.push({ sha, message: message.trim() });
  pullRequest.revision += 1;

  // A new changeset can invalidate approvals tied to the previous revision.
  for (const review of pullRequest.reviews) {
    if (review.state === "APPROVED") {
      review.stale = true;
    }
  }
}

function requestReview(pullRequest, reviewer, { team = "engineering" } = {}) {
  if (pullRequest.state !== "open") {
    throw new Error("Reviews can only be requested on an open pull request.");
  }

  const identity = requireText(reviewer, "reviewer");
  const reviewTeam = requireText(team, "team");

  if (identity === pullRequest.author) {
    throw new Error("Authors cannot review their own pull request.");
  }

  pullRequest.requestedReviewers ??= new Map();
  pullRequest.requestedReviewers.set(identity, reviewTeam);
}

function submitReview(
  pullRequest,
  reviewer,
  decision = "COMMENTED",
  { comment = "", line = null, file = null } = {},
) {
  if (pullRequest.state !== "open") {
    throw new Error("Cannot submit a review on a non-open pull request.");
  }

  const identity = requireText(reviewer, "reviewer");
  const allowed = new Set(["APPROVED", "CHANGES_REQUESTED", "COMMENTED"]);

  if (!allowed.has(decision)) {
    throw new Error(`Invalid review decision: ${decision}`);
  }
  if (identity === pullRequest.author) {
    throw new Error("Authors cannot review their own pull request.");
  }
  if (line !== null && (!Number.isInteger(line) || line < 1)) {
    throw new TypeError("An inline comment line must be a positive integer.");
  }
  if (line !== null && file === null) {
    throw new Error("An inline comment requires a file path.");
  }

  const review = {
    reviewer: identity,
    state: decision,
    comment: String(comment),
    line,
    file,
    revision: pullRequest.revision,
    stale: false,
    submittedAt: new Date().toISOString(),
  };

  pullRequest.reviews.push(review);
  pullRequest.requestedReviewers?.delete(identity);
  return review;
}

function setStatusCheck(pullRequest, name, state, { required = true } = {}) {
  requireText(name, "check name");

  if (!["success", "failure", "pending"].includes(state)) {
    throw new Error(`Unsupported check state: ${state}`);
  }

  pullRequest.checks.set(name, { state, required });
}

function addConversation(pullRequest, thread) {
  if (!["open", "closed"].includes(pullRequest.state)) {
    throw new Error("Cannot modify a merged pull request.");
  }

  if (typeof thread !== "object" || thread === null) {
    throw new TypeError("Conversation must be an object.");
  }

  pullRequest.conversations.push({
    id: requireText(thread.id, "thread id"),
    resolved: Boolean(thread.resolved),
    text: requireText(thread.text, "thread text"),
  });
}

function evaluateMergeEligibility(
  pullRequest,
  {
    requiredApprovals = DEFAULT_REQUIRED_APPROVALS,
    requiredChecks = ["ci", "security"],
    requireResolvedConversations = true,
    requireLinearHistory = false,
    allowDraftMerge = false,
    dismissStaleApprovals = true,
    mergeMethod = "squash",
  } = {},
) {
  if (!Number.isInteger(requiredApprovals) || requiredApprovals < 0) {
    throw new TypeError("requiredApprovals must be a non-negative integer.");
  }
  if (!Array.isArray(requiredChecks)) {
    throw new TypeError("requiredChecks must be an array.");
  }
  if (!["merge", "squash", "rebase"].includes(mergeMethod)) {
    throw new Error("Unsupported merge method.");
  }

  const failures = [];

  if (pullRequest.state !== "open") {
    failures.push(`Pull request is ${pullRequest.state}.`);
  }
  if (pullRequest.draft && !allowDraftMerge) {
    failures.push("Pull request is still a draft.");
  }

  const approvalsByReviewer = new Map();

  // Only the latest review from each reviewer counts. A dismissed or stale
  // review cannot be treated as a fresh approval.
  for (const review of pullRequest.reviews) {
    const current = approvalsByReviewer.get(review.reviewer);
    if (!current || current.submittedAt < review.submittedAt) {
      approvalsByReviewer.set(review.reviewer, review);
    }
  }

  const approvals = [...approvalsByReviewer.values()].filter(review =>
    review.state === "APPROVED" &&
    (!dismissStaleApprovals || !review.stale) &&
    review.revision === pullRequest.revision
  );

  if (approvals.length < requiredApprovals) {
    failures.push(`Requires ${requiredApprovals} current approval(s); found ${approvals.length}.`);
  }

  for (const name of requiredChecks) {
    const check = pullRequest.checks.get(name);
    if (!check || check.state !== "success") {
      failures.push(`Required status check '${name}' has not succeeded.`);
    }
  }

  if (
    requireResolvedConversations &&
    pullRequest.conversations.some(thread => !thread.resolved)
  ) {
    failures.push("Unresolved review conversations remain.");
  }

  if (requireLinearHistory && mergeMethod === "merge") {
    failures.push("Merge commits are prohibited by the linear-history policy.");
  }

  if (pullRequest.requestedReviewers?.size > 0) {
    failures.push("Requested reviews are still outstanding.");
  }

  return {
    eligible: failures.length === 0,
    failures,
    countedApprovals: approvals.length,
    mergeMethod,
  };
}

function synchronizeWithBase(pullRequest, {
  baseRevision,
  conflicts = [],
} = {}) {
  if (pullRequest.state !== "open") {
    throw new Error("Only open pull requests can be synchronized.");
  }
  if (!Number.isInteger(baseRevision) || baseRevision < 0) {
    throw new TypeError("baseRevision must be a non-negative integer.");
  }

  if (conflicts.length > 0) {
    return {
      synchronized: false,
      conflicts: [...conflicts],
      message: "Resolve the listed conflicts before merging.",
    };
  }

  pullRequest.baseRevision = baseRevision;
  pullRequest.revision += 1;

  for (const review of pullRequest.reviews) {
    if (review.state === "APPROVED") {
      review.stale = true;
    }
  }

  return {
    synchronized: true,
    conflicts: [],
    message: "Base branch synchronization completed; revalidation is required.",
  };
}

function closePullRequest(pullRequest, { merged = false } = {}) {
  if (TERMINAL_STATES.has(pullRequest.state)) {
    throw new Error(`Pull request is already ${pullRequest.state}.`);
  }

  if (merged) {
    const eligibility = evaluateMergeEligibility(pullRequest);
    if (!eligibility.eligible) {
      throw new Error(`Merge rejected: ${eligibility.failures.join("; ")}`);
    }
    pullRequest.state = "merged";
  } else {
    pullRequest.state = "closed";
  }
}

function reopenPullRequest(pullRequest) {
  if (pullRequest.state !== "closed") {
    throw new Error("Only a closed, unmerged pull request can be reopened.");
  }

  pullRequest.state = "open";
  // Reopening does not restore validity to reviews or status checks that
  // have become stale; eligibility is recalculated from current state.
}

async function runChecksAsynchronously(pullRequest, checkRunners) {
  // Promise.allSettled records every result instead of abandoning the report
  // when one independent CI or security check rejects.
  const results = await Promise.allSettled(
    checkRunners.map(async ({ name, run }) => {
      const result = await run();
      return { name, state: result ? "success" : "failure" };
    }),
  );

  results.forEach((result, index) => {
    const name = checkRunners[index].name;
    if (result.status === "fulfilled") {
      setStatusCheck(pullRequest, name, result.value.state);
    } else {
      setStatusCheck(pullRequest, name, "failure");
      console.error(`Check ${name} failed: ${result.reason}`);
    }
  });

  return results;
}

async function main() {
  const pullRequest = createPullRequest({
    number: 104,
    title: "Enforce authorization on deployment settings",
    sourceBranch: "feature/deployment-auth",
    // targetBranch defaults to main; this call intentionally uses that default.
    draft: false,
    labels: ["Security", "security", "governance"],
  });

  pullRequest.author = "developer-lee";

  console.log("Initial pull request:", pullRequest);

  addCommit(pullRequest, "a91c3e0", "Add authorization middleware");
  addCommit(pullRequest, "b52d7f1", "Test unauthorized deployment requests");

  requestReview(pullRequest, "reviewer-alex");
  requestReview(pullRequest, "reviewer-sam", { team: "security" });

  submitReview(
    pullRequest,
    "reviewer-alex",
    "APPROVED",
    { comment: "Authorization is enforced at the service boundary." },
  );

  submitReview(
    pullRequest,
    "reviewer-sam",
    "COMMENTED",
    {
      comment: "Please retain the audit event for denied requests.",
      file: "src/deployment.js",
      line: 88,
    },
  );

  addConversation(pullRequest, {
    id: "thread-1",
    text: "Audit event coverage needs confirmation.",
    resolved: true,
  });

  await runChecksAsynchronously(pullRequest, [
    { name: "ci", run: async () => true },
    { name: "security", run: async () => true },
  ]);

  console.log(
    "Initial eligibility:",
    evaluateMergeEligibility(pullRequest),
  );

  submitReview(
    pullRequest,
    "reviewer-sam",
    "APPROVED",
    { comment: "Audit coverage verified." },
  );

  console.log(
    "After approval:",
    evaluateMergeEligibility(pullRequest),
  );

  const synchronization = synchronizeWithBase(pullRequest, {
    baseRevision: 87,
    conflicts: [],
  });
  console.log("Base synchronization:", synchronization);

  console.log(
    "After synchronization:",
    evaluateMergeEligibility(pullRequest),
  );

  // Re-approval is necessary because the changeset changed.
  submitReview(pullRequest, "reviewer-alex", "APPROVED");
  submitReview(pullRequest, "reviewer-sam", "APPROVED");

  console.log(
    "Final eligibility:",
    evaluateMergeEligibility(pullRequest, { mergeMethod: "squash" }),
  );

  closePullRequest(pullRequest, { merged: true });
  console.log(`Pull request state: ${pullRequest.state}`);
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
