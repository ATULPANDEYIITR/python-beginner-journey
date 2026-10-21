"use strict";

/*
 * Functions are first-class values in JavaScript.
 *
 * This model uses functions as repository-policy data:
 * - policy functions are stored in arrays and maps
 * - functions are passed to evaluators
 * - policies are composed dynamically
 * - event handlers are functions
 * - asynchronous status checks are functions returning Promises
 *
 * Pull Requests, Code Review, Approvals, and Branch Protection remain
 * separate domain concepts even though functions connect their behavior.
 */

const PRState = Object.freeze({
  DRAFT: "draft",
  OPEN: "open",
  CLOSED: "closed",
  MERGED: "merged",
});

const ReviewState = Object.freeze({
  COMMENTED: "commented",
  APPROVED: "approved",
  CHANGES_REQUESTED: "changes_requested",
  DISMISSED: "dismissed",
});

const MergeStrategy = Object.freeze({
  MERGE_COMMIT: "merge_commit",
  SQUASH: "squash",
  REBASE: "rebase",
});

class ValidationError extends Error {}

class PullRequest {
  constructor({
    number,
    sourceBranch,
    targetBranch,
    commits = [],
    draft = false,
  }) {
    if (!Number.isInteger(number) || number <= 0) {
      throw new ValidationError("Pull Request number must be positive.");
    }
    if (!sourceBranch || !targetBranch || sourceBranch === targetBranch) {
      throw new ValidationError("Source and target branches are invalid.");
    }

    this.number = number;
    this.sourceBranch = sourceBranch;
    this.targetBranch = targetBranch;
    this.commits = [...commits];
    this.state = draft ? PRState.DRAFT : PRState.OPEN;
    this.reviews = [];
    this.statusChecks = new Map();
    this.openConversations = 0;
    this.mergeable = true;
    this.synchronized = true;
  }

  submitReview(review) {
    if (this.state !== PRState.OPEN) {
      throw new ValidationError("Only open Pull Requests accept reviews.");
    }

    if (!review.reviewer?.trim()) {
      throw new ValidationError("Reviewer is required.");
    }

    if (!Object.values(ReviewState).includes(review.state)) {
      throw new ValidationError("Unknown review state.");
    }

    this.reviews.push({
      reviewer: review.reviewer,
      state: review.state,
      comments: [...(review.comments ?? [])],
    });
  }

  close() {
    if (this.state === PRState.MERGED) {
      throw new ValidationError("Merged Pull Requests cannot be closed.");
    }
    this.state = PRState.CLOSED;
  }

  reopen() {
    if (this.state !== PRState.CLOSED) {
      throw new ValidationError("Only closed Pull Requests can be reopened.");
    }
    this.state = PRState.OPEN;
  }

  synchronize(commits) {
    if (this.state !== PRState.OPEN) {
      throw new ValidationError("Only open Pull Requests can synchronize.");
    }

    this.commits.push(...commits);
    this.synchronized = true;
    this.mergeable = true;
  }

  markConflict() {
    this.mergeable = false;
    this.synchronized = false;
  }
}

class BranchProtection {
  constructor({
    requiredReviews = 0,
    requiredStatusChecks = [],
    requireConversationResolution = false,
    requireLinearHistory = false,
    allowDirectPush = false,
    allowForcePush = false,
    allowDeletion = false,
    allowAdminBypass = false,
  }) {
    this.requiredReviews = requiredReviews;
    this.requiredStatusChecks = [...requiredStatusChecks];
    this.requireConversationResolution = requireConversationResolution;
    this.requireLinearHistory = requireLinearHistory;
    this.allowDirectPush = allowDirectPush;
    this.allowForcePush = allowForcePush;
    this.allowDeletion = allowDeletion;
    this.allowAdminBypass = allowAdminBypass;
  }
}

class Repository {
  constructor(name, defaultBranch) {
    this.name = name;
    this.defaultBranch = defaultBranch;
    this.protection = new Map();
    this.events = new Map();
  }

  protect(branch, policy) {
    this.protection.set(branch, policy);
  }

  on(eventName, handler) {
    if (typeof handler !== "function") {
      throw new TypeError("Event handler must be a function.");
    }

    const handlers = this.events.get(eventName) ?? [];
    handlers.push(handler);
    this.events.set(eventName, handlers);
  }

  emit(eventName, payload) {
    for (const handler of this.events.get(eventName) ?? []) {
      handler(payload);
    }
  }
}

/*
 * These functions represent distinct governance layers.
 * A function can be passed around as data without losing its behavior.
 */

const rules = {
  isOpenAndMergeable: (pr) =>
    pr.state === PRState.OPEN &&
    pr.mergeable &&
    pr.synchronized,

  hasRequiredApprovals: (pr, repository) => {
    const policy = repository.protection.get(pr.targetBranch);
    if (!policy) return true;

    const approvedReviewers = new Set(
      pr.reviews
        .filter((review) => review.state === ReviewState.APPROVED)
        .map((review) => review.reviewer)
    );

    return approvedReviewers.size >= policy.requiredReviews;
  },

  hasNoRequestedChanges: (pr) =>
    !pr.reviews.some(
      (review) => review.state === ReviewState.CHANGES_REQUESTED
    ),

  requiredChecksPass: (pr, repository) => {
    const policy = repository.protection.get(pr.targetBranch);
    if (!policy) return true;

    return policy.requiredStatusChecks.every(
      (check) => pr.statusChecks.get(check) === "passed"
    );
  },

  conversationsResolved: (pr, repository) => {
    const policy = repository.protection.get(pr.targetBranch);

    return (
      !policy?.requireConversationResolution ||
      pr.openConversations === 0
    );
  },
};

function all(...predicates) {
  if (predicates.length === 0) {
    throw new ValidationError("At least one predicate is required.");
  }

  return (...args) => predicates.every((predicate) => predicate(...args));
}

function any(...predicates) {
  if (predicates.length === 0) {
    throw new ValidationError("At least one predicate is required.");
  }

  return (...args) => predicates.some((predicate) => predicate(...args));
}

function buildMergePolicy(repository) {
  return all(
    rules.isOpenAndMergeable,
    rules.hasRequiredApprovals,
    rules.hasNoRequestedChanges,
    rules.requiredChecksPass,
    rules.conversationsResolved
  );
}

function mergePullRequest(pr, repository, strategy) {
  if (!Object.values(MergeStrategy).includes(strategy)) {
    throw new ValidationError("Unsupported merge strategy.");
  }

  const policy = buildMergePolicy(repository);

  if (!policy(pr, repository)) {
    throw new ValidationError(
      `Pull Request #${pr.number} is not merge-eligible.`
    );
  }

  pr.state = PRState.MERGED;

  repository.emit("merged", {
    pullRequest: pr.number,
    target: pr.targetBranch,
    strategy,
  });

  return {
    pullRequest: pr.number,
    strategy,
    target: pr.targetBranch,
  };
}

/*
 * Asynchronous functions are also first-class values.
 * Each status check returns a Promise and can be scheduled dynamically.
 */
async function runStatusCheck(name, implementation) {
  if (typeof implementation !== "function") {
    throw new TypeError("Status check implementation must be callable.");
  }

  const passed = await implementation();
  if (typeof passed !== "boolean") {
    throw new TypeError(`Status check '${name}' must return boolean.`);
  }

  return { name, passed };
}

async function executeChecks(pr, checks) {
  const jobs = Object.entries(checks).map(([name, implementation]) =>
    runStatusCheck(name, implementation)
  );

  const results = await Promise.all(jobs);

  for (const result of results) {
    pr.statusChecks.set(result.name, result.passed ? "passed" : "failed");
  }

  return results;
}

function evaluateRules(pr, repository, policyFunctions) {
  return policyFunctions.map((policy) => ({
    name: policy.name || "anonymous",
    passed: Boolean(policy(pr, repository)),
  }));
}

async function main() {
  const repository = new Repository("orders-service", "main");

  repository.protect(
    "main",
    new BranchProtection({
      requiredReviews: 2,
      requiredStatusChecks: ["unit-tests", "security-scan"],
      requireConversationResolution: true,
      requireLinearHistory: true,
      allowDirectPush: false,
      allowForcePush: false,
    })
  );

  repository.on("merged", (event) => {
    console.log(
      `Event: PR #${event.pullRequest} merged using ${event.strategy}.`
    );
  });

  const pr = new PullRequest({
    number: 101,
    sourceBranch: "feature/order-validation",
    targetBranch: "main",
    commits: [
      { sha: "a001", message: "Validate order totals", author: "alice" },
      { sha: "a002", message: "Add validation tests", author: "alice" },
    ],
  });

  pr.submitReview({
    reviewer: "bob",
    state: ReviewState.APPROVED,
  });

  pr.submitReview({
    reviewer: "carol",
    state: ReviewState.APPROVED,
  });

  const checks = {
    "unit-tests": async () => true,
    "security-scan": async () => true,
  };

  await executeChecks(pr, checks);

  const policyFunctions = Object.values(rules);

  console.table(evaluateRules(pr, repository, policyFunctions));

  console.log(
    "Merge result:",
    mergePullRequest(pr, repository, MergeStrategy.SQUASH)
  );

  /*
   * Functions can be data in collections and can transform data.
   * This example models branch-name normalization without introducing
   * a generic JavaScript tutorial.
   */
  const branchTransformations = [
    (value) => value.trim(),
    (value) => value.toLowerCase(),
    (value) => value.replace(/\s+/g, "-"),
    (value) => value.replace(/[^a-z0-9/_-]/g, ""),
  ];

  const branch = branchTransformations.reduce(
    (value, transformation) =>
      transformation(value),
    " Feature / Payment Validation "
  );

  console.log("Normalized branch:", branch);

  /*
   * Failure case: insufficient approvals.
   * The same policy functions remain reusable as data.
   */
  const blockedPr = new PullRequest({
    number: 102,
    sourceBranch: "feature/reporting",
    targetBranch: "main",
  });

  blockedPr.submitReview({
    reviewer: "bob",
    state: ReviewState.APPROVED,
  });

  await executeChecks(blockedPr, {
    "unit-tests": async () => true,
    "security-scan": async () => true,
  });

  const approvalPolicy = rules.hasRequiredApprovals;

  console.log(
    "Blocked PR approval policy:",
    approvalPolicy(blockedPr, repository)
  );

  try {
    mergePullRequest(
      blockedPr,
      repository,
      MergeStrategy.MERGE_COMMIT
    );
  } catch (error) {
    console.log("Expected merge failure:", error.message);
  }

  /*
   * `any` is another function factory. The returned function itself becomes
   * policy data and can later be passed to another evaluator.
   */
  const safeOrApproved = any(
    rules.hasRequiredApprovals,
    rules.conversationsResolved
  );

  console.log(
    "Composite policy result:",
    safeOrApproved(blockedPr, repository)
  );
}

main().catch((error) => {
  console.error("Workflow failed:", error.message);
  process.exitCode = 1;
});
