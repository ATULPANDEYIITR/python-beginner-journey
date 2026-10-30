"use strict";

const { EventEmitter } = require("node:events");

/*
 * A custom exception hierarchy gives callers stable error codes, structured
 * context, and retry information without relying on fragile message parsing.
 */
class WorkflowError extends Error {
  constructor(message, { code = "WORKFLOW_ERROR", context = {}, retryable = false } = {}) {
    super(message);
    this.name = new.target.name;
    this.code = code;
    this.context = Object.freeze({ ...context });
    this.retryable = retryable;
    Error.captureStackTrace?.(this, new.target);
  }

  toJSON() {
    return {
      type: this.name,
      code: this.code,
      message: this.message,
      context: this.context,
      retryable: this.retryable,
    };
  }
}

class ValidationError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, { code: "VALIDATION_ERROR", context });
  }
}

class ResourceNotFoundError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, { code: "RESOURCE_NOT_FOUND", context });
  }
}

class StateTransitionError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, { code: "INVALID_STATE_TRANSITION", context });
  }
}

class ReviewerEligibilityError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, { code: "REVIEWER_NOT_ELIGIBLE", context });
  }
}

class ProtectionViolationError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, { code: "BRANCH_PROTECTION_VIOLATION", context });
  }
}

class MergeConflictError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, { code: "MERGE_CONFLICT", context });
  }
}

class MergeEligibilityError extends WorkflowError {
  constructor(message, reasons = []) {
    super(message, {
      code: "MERGE_NOT_ELIGIBLE",
      context: { reasons },
    });
  }
}

class ConcurrencyError extends WorkflowError {
  constructor(message, context = {}) {
    super(message, {
      code: "CONCURRENCY_CONFLICT",
      context,
      retryable: true,
    });
  }
}

const PRState = Object.freeze({
  DRAFT: "DRAFT",
  OPEN: "OPEN",
  CLOSED: "CLOSED",
  MERGED: "MERGED",
});

const ReviewDecision = Object.freeze({
  COMMENTED: "COMMENTED",
  APPROVED: "APPROVED",
  CHANGES_REQUESTED: "CHANGES_REQUESTED",
  DISMISSED: "DISMISSED",
});

const CheckState = Object.freeze({
  PENDING: "PENDING",
  SUCCESS: "SUCCESS",
  FAILURE: "FAILURE",
});

const MergeStrategy = Object.freeze({
  MERGE: "MERGE",
  SQUASH: "SQUASH",
  REBASE: "REBASE",
});

function requireText(value, field) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new ValidationError(`${field} must be a non-empty string.`, { field });
  }
  return value.trim();
}

class Repository extends EventEmitter {
  constructor(name, options = {}) {
    super();
    this.name = requireText(name, "Repository name");
    this.branches = new Map();
    this.pullRequests = new Map();
    this.eligibleReviewers = new Set(options.eligibleReviewers ?? []);
    this.commitCounter = 0;
    this.pullRequestCounter = 0;
    this.commentCounter = 0;

    this.policy = {
      requiredReviews: 1,
      requiredChecks: new Set(["unit-tests", "security-scan"]),
      requireConversationResolution: true,
      requireLinearHistory: true,
      restrictDirectPush: true,
      restrictForcePush: true,
      restrictDeletion: true,
      dismissStaleReviews: true,
      allowedStrategies: new Set([
        MergeStrategy.SQUASH,
        MergeStrategy.REBASE,
      ]),
      allowBypass: false,
      enforceAdmins: true,
      bypassUsers: new Set(),
      ...options.policy,
    };

    // Convert externally supplied arrays to Sets so policy checks are O(1).
    this.policy.requiredChecks = new Set(this.policy.requiredChecks);
    this.policy.allowedStrategies = new Set(this.policy.allowedStrategies);
    this.policy.bypassUsers = new Set(this.policy.bypassUsers);

    const root = this.createCommit(
      "Initial repository state",
      null,
      "system"
    );
    this.branches.set("main", {
      name: "main",
      headSha: root.sha,
      protected: true,
      deleted: false,
    });
  }

  createCommit(message, parentSha, author) {
    const commit = Object.freeze({
      sha: `sha-${String(++this.commitCounter).padStart(8, "0")}`,
      message: requireText(message, "Commit message"),
      parentSha,
      author: requireText(author, "Commit author"),
    });
    return commit;
  }

  getBranch(name) {
    const branch = this.branches.get(name);
    if (!branch || branch.deleted) {
      throw new ResourceNotFoundError(`Branch '${name}' does not exist.`, {
        branch: name,
      });
    }
    return branch;
  }

  getPullRequest(number) {
    const pr = this.pullRequests.get(number);
    if (!pr) {
      throw new ResourceNotFoundError(`Pull Request #${number} does not exist.`, {
        pullRequest: number,
      });
    }
    return pr;
  }

  isBypassActor(actor) {
    return (
      this.policy.allowBypass &&
      !this.policy.enforceAdmins &&
      this.policy.bypassUsers.has(actor)
    );
  }

  createBranch(name, fromBranch = "main") {
    name = requireText(name, "Branch name");
    const parent = this.getBranch(fromBranch);

    if (this.branches.has(name) && !this.branches.get(name).deleted) {
      throw new ValidationError(`Branch '${name}' already exists.`, {
        branch: name,
      });
    }

    const branch = {
      name,
      headSha: parent.headSha,
      protected: false,
      deleted: false,
    };
    this.branches.set(name, branch);
    this.emit("branch.created", { name, fromBranch });
    return branch;
  }

  pushCommit(branchName, message, author, options = {}) {
    const branch = this.getBranch(branchName);
    const { force = false, expectedParent = branch.headSha } = options;
    const bypass = this.isBypassActor(author);

    if (branch.protected && !bypass) {
      if (this.policy.restrictDirectPush) {
        throw new ProtectionViolationError(
          `Direct pushes to '${branchName}' are prohibited.`,
          { branch: branchName, actor: author }
        );
      }
      if (force && this.policy.restrictForcePush) {
        throw new ProtectionViolationError(
          `Force pushes to '${branchName}' are prohibited.`,
          { branch: branchName, actor: author }
        );
      }
    }

    if (expectedParent !== branch.headSha) {
      throw new ConcurrencyError(
        "The branch head changed before the commit was applied.",
        {
          branch: branchName,
          expectedParent,
          currentHead: branch.headSha,
        }
      );
    }

    const commit = this.createCommit(message, branch.headSha, author);
    branch.headSha = commit.sha;

    for (const pr of this.pullRequests.values()) {
      if (
        pr.sourceBranch === branchName &&
        [PRState.OPEN, PRState.DRAFT].includes(pr.state)
      ) {
        pr.version += 1;
      }
    }

    this.emit("commit.pushed", {
      branch: branchName,
      commit: commit.sha,
      author,
    });
    return commit;
  }

  deleteBranch(name, actor) {
    const branch = this.getBranch(name);
    if (
      branch.protected &&
      this.policy.restrictDeletion &&
      !this.isBypassActor(actor)
    ) {
      throw new ProtectionViolationError(
        `Deletion of protected branch '${name}' is prohibited.`,
        { branch: name, actor }
      );
    }
    branch.deleted = true;
    this.emit("branch.deleted", { name, actor });
  }

  createPullRequest({ title, sourceBranch, targetBranch, author, draft = false }) {
    title = requireText(title, "Pull Request title");
    const source = this.getBranch(sourceBranch);
    const target = this.getBranch(targetBranch);

    if (sourceBranch === targetBranch) {
      throw new ValidationError("Source and target branches must differ.");
    }
    if (source.headSha === target.headSha) {
      throw new ValidationError("The source branch has no new commits.");
    }

    for (const existing of this.pullRequests.values()) {
      if (
        existing.sourceBranch === sourceBranch &&
        existing.targetBranch === targetBranch &&
        [PRState.DRAFT, PRState.OPEN].includes(existing.state)
      ) {
        throw new ValidationError("An active Pull Request already exists.", {
          existingPullRequest: existing.number,
        });
      }
    }

    const pr = {
      number: ++this.pullRequestCounter,
      title,
      author: requireText(author, "Pull Request author"),
      sourceBranch,
      targetBranch,
      state: draft ? PRState.DRAFT : PRState.OPEN,
      baseShaSeen: target.headSha,
      version: 1,
      requestedReviewers: new Set(),
      reviews: [],
      comments: [],
      checks: new Map(),
      hasConflicts: false,
      mergedSha: null,
    };

    this.pullRequests.set(pr.number, pr);
    this.emit("pull-request.opened", {
      number: pr.number,
      state: pr.state,
      sourceBranch,
      targetBranch,
    });
    return pr;
  }

  readyForReview(number) {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.DRAFT) {
      throw new StateTransitionError(
        "Only a draft Pull Request can become ready for review.",
        { state: pr.state }
      );
    }
    pr.state = PRState.OPEN;
    pr.version += 1;
    this.emit("pull-request.ready", { number });
  }

  requestReview(number, reviewer) {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.OPEN) {
      throw new StateTransitionError("Review requests require an open Pull Request.");
    }
    if (reviewer === pr.author || !this.eligibleReviewers.has(reviewer)) {
      throw new ReviewerEligibilityError(
        `${reviewer} is not eligible to review this change.`,
        { reviewer, author: pr.author }
      );
    }
    pr.requestedReviewers.add(reviewer);
    pr.version += 1;
    this.emit("review.requested", { number, reviewer });
  }

  submitReview(number, reviewer, decision, body = "") {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.OPEN) {
      throw new StateTransitionError("Reviews require an open Pull Request.");
    }
    if (reviewer === pr.author || !this.eligibleReviewers.has(reviewer)) {
      throw new ReviewerEligibilityError(
        "The author cannot approve their own change.",
        { reviewer, author: pr.author }
      );
    }
    if (!Object.values(ReviewDecision).includes(decision)) {
      throw new ValidationError("Unknown review decision.", { decision });
    }

    const review = Object.freeze({
      reviewer,
      decision,
      commitSha: this.getBranch(pr.sourceBranch).headSha,
      baseSha: this.getBranch(pr.targetBranch).headSha,
      body: String(body),
      submittedAt: new Date().toISOString(),
    });

    pr.reviews.push(review);
    pr.requestedReviewers.delete(reviewer);
    pr.version += 1;
    this.emit("review.submitted", { number, reviewer, decision });
    return review;
  }

  dismissReview(number, reviewer, actor) {
    const pr = this.getPullRequest(number);
    if (!this.eligibleReviewers.has(actor)) {
      throw new ReviewerEligibilityError("Only an eligible reviewer may dismiss a review.");
    }

    const index = pr.reviews.map((r) => r.reviewer).lastIndexOf(reviewer);
    if (index < 0) {
      throw new ResourceNotFoundError("No review by this reviewer exists.", {
        reviewer,
      });
    }

    const old = pr.reviews[index];
    pr.reviews[index] = Object.freeze({
      ...old,
      decision: ReviewDecision.DISMISSED,
    });
    pr.version += 1;
    this.emit("review.dismissed", { number, reviewer, actor });
  }

  addInlineComment(number, reviewer, path, line, body) {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.OPEN) {
      throw new StateTransitionError("Comments require an open Pull Request.");
    }
    if (reviewer === pr.author || !this.eligibleReviewers.has(reviewer)) {
      throw new ReviewerEligibilityError("The commenter is not an eligible reviewer.");
    }
    if (!Number.isInteger(line) || line < 1) {
      throw new ValidationError("Comment line must be a positive integer.", {
        line,
      });
    }

    const comment = {
      id: ++this.commentCounter,
      reviewer,
      path: requireText(path, "Comment path"),
      line,
      body: requireText(body, "Comment body"),
      resolved: false,
    };
    pr.comments.push(comment);
    pr.version += 1;
    this.emit("discussion.created", { number, commentId: comment.id });
    return comment;
  }

  resolveDiscussion(number, commentId, actor) {
    const pr = this.getPullRequest(number);
    const comment = pr.comments.find((item) => item.id === commentId);
    if (!comment) {
      throw new ResourceNotFoundError("Review discussion does not exist.", {
        number,
        commentId,
      });
    }
    if (!actor) {
      throw new ValidationError("A discussion resolver must be identified.");
    }
    comment.resolved = true;
    pr.version += 1;
    this.emit("discussion.resolved", { number, commentId, actor });
  }

  setStatusCheck(number, name, state, details = "", testedSha = null) {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.OPEN) {
      throw new StateTransitionError("Checks require an open Pull Request.");
    }
    if (!Object.values(CheckState).includes(state)) {
      throw new ValidationError("Unknown status-check state.", { state });
    }

    const currentSha = this.getBranch(pr.sourceBranch).headSha;
    const commitSha = testedSha ?? currentSha;
    if (commitSha !== currentSha) {
      throw new ValidationError("A status check cannot certify an old source commit.", {
        testedSha: commitSha,
        currentSha,
      });
    }

    name = requireText(name, "Status check name");
    const check = Object.freeze({
      name,
      state,
      commitSha,
      details: String(details),
      updatedAt: new Date().toISOString(),
    });
    pr.checks.set(`${name}:${commitSha}`, check);
    pr.version += 1;
    this.emit("check.updated", { number, name, state, commitSha });
    return check;
  }

  /*
   * Promise.allSettled preserves the outcome of every independent check.
   * A failing scanner is recorded as a failed check rather than hiding the
   * outcomes of the remaining checks.
   */
  async runChecks(number, checkDefinitions) {
    const pr = this.getPullRequest(number);
    if (!checkDefinitions || typeof checkDefinitions !== "object") {
      throw new ValidationError("Check definitions must be an object.");
    }

    const currentSha = this.getBranch(pr.sourceBranch).headSha;
    const entries = Object.entries(checkDefinitions);
    if (entries.length === 0) {
      throw new ValidationError("At least one check must be supplied.");
    }

    const outcomes = await Promise.allSettled(
      entries.map(async ([name, checkFunction]) => {
        if (typeof checkFunction !== "function") {
          throw new ValidationError(`Check '${name}' must be a function.`);
        }
        return checkFunction({
          pullRequest: number,
          commitSha: currentSha,
        });
      })
    );

    return outcomes.map((outcome, index) => {
      const [name] = entries[index];
      if (outcome.status === "fulfilled") {
        const result = outcome.value;
        const state = result === true ? CheckState.SUCCESS : CheckState.FAILURE;
        return this.setStatusCheck(
          number,
          name,
          state,
          state === CheckState.SUCCESS ? "Check passed" : "Check did not pass",
          currentSha
        );
      }

      this.setStatusCheck(
        number,
        name,
        CheckState.FAILURE,
        outcome.reason?.message ?? "Check execution failed",
        currentSha
      );
      return {
        name,
        state: CheckState.FAILURE,
        commitSha: currentSha,
        error: outcome.reason?.message ?? "Unknown check failure",
      };
    });
  }

  synchronizeBase(number, { conflict = false } = {}) {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.OPEN) {
      throw new StateTransitionError("Only open Pull Requests can synchronize.");
    }

    if (conflict) {
      pr.hasConflicts = true;
      pr.version += 1;
      this.emit("synchronization.conflict", { number });
      throw new MergeConflictError(
        "Base synchronization produced conflicts.",
        { number }
      );
    }

    pr.baseShaSeen = this.getBranch(pr.targetBranch).headSha;
    pr.hasConflicts = false;
    pr.version += 1;
    this.emit("base.synchronized", { number, baseSha: pr.baseShaSeen });
  }

  latestReviews(pr) {
    const latest = new Map();
    for (const review of pr.reviews) {
      latest.set(review.reviewer, review);
    }
    return latest;
  }

  evaluateMerge(number, strategy, actor) {
    const pr = this.getPullRequest(number);
    const source = this.getBranch(pr.sourceBranch);
    const target = this.getBranch(pr.targetBranch);
    const reasons = [];
    const bypass = this.isBypassActor(actor);

    if (pr.state !== PRState.OPEN) {
      reasons.push(`Pull Request state is ${pr.state}, not OPEN.`);
    }
    if (pr.baseShaSeen !== target.headSha) {
      reasons.push("Base branch has advanced and must be synchronized.");
    }
    if (pr.hasConflicts) {
      reasons.push("Merge conflicts are unresolved.");
    }
    if (!this.policy.allowedStrategies.has(strategy)) {
      reasons.push(`Merge strategy '${strategy}' is not allowed.`);
    }
    if (this.policy.requireLinearHistory && strategy === MergeStrategy.MERGE) {
      reasons.push("A merge commit would violate the linear-history policy.");
    }

    const latest = [...this.latestReviews(pr).values()];
    const applicable = this.policy.dismissStaleReviews
      ? latest.filter(
          (review) =>
            review.commitSha === source.headSha &&
            review.decision !== ReviewDecision.DISMISSED
        )
      : latest.filter((review) => review.decision !== ReviewDecision.DISMISSED);

    const approvals = applicable.filter(
      (review) => review.decision === ReviewDecision.APPROVED
    ).length;
    const changesRequested = applicable.some(
      (review) => review.decision === ReviewDecision.CHANGES_REQUESTED
    );

    if (!bypass) {
      if (approvals < this.policy.requiredReviews) {
        reasons.push(
          `Requires ${this.policy.requiredReviews} approval(s); ${approvals} currently apply.`
        );
      }
      if (changesRequested) {
        reasons.push("An active review requests changes.");
      }

      const missingChecks = [...this.policy.requiredChecks].filter((name) => {
        const check = pr.checks.get(`${name}:${source.headSha}`);
        return !check || check.state !== CheckState.SUCCESS;
      });
      if (missingChecks.length > 0) {
        reasons.push(`Required checks are missing or unsuccessful: ${missingChecks.join(", ")}.`);
      }

      if (
        this.policy.requireConversationResolution &&
        pr.comments.some((comment) => !comment.resolved)
      ) {
        reasons.push("At least one review discussion remains unresolved.");
      }
    }

    return Object.freeze({
      pullRequest: number,
      eligible: reasons.length === 0,
      strategy,
      sourceHead: source.headSha,
      targetHead: target.headSha,
      approvals,
      requiredApprovals: this.policy.requiredReviews,
      bypassApplied: bypass,
      version: pr.version,
      reasons: Object.freeze(reasons),
    });
  }

  merge(number, strategy, actor, expectedVersion = null) {
    const pr = this.getPullRequest(number);
    if (expectedVersion !== null && expectedVersion !== pr.version) {
      throw new ConcurrencyError(
        "Pull Request changed after the client read it.",
        { expectedVersion, actualVersion: pr.version }
      );
    }

    const report = this.evaluateMerge(number, strategy, actor);
    if (!report.eligible) {
      throw new MergeEligibilityError(
        "Repository policy rejected the merge.",
        report.reasons
      );
    }

    const target = this.getBranch(pr.targetBranch);
    const commit = this.createCommit(
      `${strategy} Pull Request #${number}: ${pr.title}`,
      target.headSha,
      actor
    );

    target.headSha = commit.sha;
    pr.mergedSha = commit.sha;
    pr.state = PRState.MERGED;
    pr.version += 1;
    this.emit("pull-request.merged", {
      number,
      strategy,
      mergeCommit: commit.sha,
      actor,
    });
    return commit;
  }

  closePullRequest(number) {
    const pr = this.getPullRequest(number);
    if (![PRState.OPEN, PRState.DRAFT].includes(pr.state)) {
      throw new StateTransitionError("This Pull Request cannot be closed.", {
        state: pr.state,
      });
    }
    pr.state = PRState.CLOSED;
    pr.version += 1;
    this.emit("pull-request.closed", { number });
  }

  reopenPullRequest(number) {
    const pr = this.getPullRequest(number);
    if (pr.state !== PRState.CLOSED) {
      throw new StateTransitionError("Only a closed Pull Request can be reopened.", {
        state: pr.state,
      });
    }
    pr.state = PRState.OPEN;
    pr.version += 1;
    this.emit("pull-request.reopened", { number });
  }
}

async function main() {
  const repository = new Repository("acme/payments", {
    eligibleReviewers: ["bob", "carol", "dave"],
    policy: {
      requiredReviews: 1,
      requiredChecks: ["unit-tests", "security-scan"],
      requireConversationResolution: true,
      requireLinearHistory: true,
    },
  });

  // Event listeners provide an audit trail separate from exception handling.
  repository.on("pull-request.opened", (event) => {
    console.log("Event:", event);
  });
  repository.on("review.submitted", (event) => {
    console.log("Event:", event);
  });
  repository.on("pull-request.merged", (event) => {
    console.log("Event:", event);
  });

  repository.createBranch("feature/refund-validation");
  repository.pushCommit(
    "feature/refund-validation",
    "Validate refund amounts",
    "alice"
  );

  const pr = repository.createPullRequest({
    title: "Add refund validation",
    sourceBranch: "feature/refund-validation",
    targetBranch: "main",
    author: "alice",
    draft: true,
  });

  repository.readyForReview(pr.number);
  repository.requestReview(pr.number, "bob");

  const comment = repository.addInlineComment(
    pr.number,
    "bob",
    "payments/refunds.js",
    34,
    "Reject negative refund amounts before creating a transaction."
  );
  repository.resolveDiscussion(pr.number, comment.id, "bob");

  // Independent checks run concurrently and return separate outcomes.
  const checkResults = await repository.runChecks(pr.number, {
    "unit-tests": async ({ commitSha }) => commitSha.length > 0,
    "security-scan": async () => true,
  });
  console.log("\nCheck results:", checkResults);

  repository.submitReview(pr.number, "bob", ReviewDecision.APPROVED);
  const report = repository.evaluateMerge(
    pr.number,
    MergeStrategy.SQUASH,
    "alice"
  );
  console.log("\nMerge evaluation:", report);

  const mergeCommit = repository.merge(
    pr.number,
    MergeStrategy.SQUASH,
    "alice",
    pr.version
  );
  console.log("\nMerge commit:", mergeCommit);

  try {
    repository.pushCommit("main", "Attempt unauthorized direct push", "alice");
  } catch (error) {
    if (error instanceof WorkflowError) {
      console.log("\nProtected branch error:", error.toJSON());
    } else {
      throw error;
    }
  }

  repository.createBranch("feature/second-change");
  repository.pushCommit("feature/second-change", "Add another validation rule", "alice");
  const second = repository.createPullRequest({
    title: "Add an additional validation rule",
    sourceBranch: "feature/second-change",
    targetBranch: "main",
    author: "alice",
  });

  try {
    repository.submitReview(
      second.number,
      "alice",
      ReviewDecision.APPROVED
    );
  } catch (error) {
    console.log("\nSelf-review rejection:", error.toJSON());
  }

  repository.requestReview(second.number, "bob");
  repository.submitReview(second.number, "bob", ReviewDecision.APPROVED);

  // A new commit changes the source head, making the earlier approval stale.
  repository.pushCommit(
    "feature/second-change",
    "Fix a refund boundary condition",
    "alice"
  );

  await repository.runChecks(second.number, {
    "unit-tests": async () => true,
    "security-scan": async () => true,
  });

  const staleReport = repository.evaluateMerge(
    second.number,
    MergeStrategy.SQUASH,
    "alice"
  );
  console.log("\nEvaluation after source update:", staleReport);

  try {
    repository.merge(second.number, MergeStrategy.SQUASH, "alice");
  } catch (error) {
    if (!(error instanceof MergeEligibilityError)) {
      throw error;
    }
    console.log("\nMerge eligibility error:", error.toJSON());
  }
}

main().catch((error) => {
  if (error instanceof WorkflowError) {
    console.error(JSON.stringify(error.toJSON(), null, 2));
    process.exitCode = 1;
  } else {
    console.error("Unexpected failure:", error);
    process.exitCode = 1;
  }
});
