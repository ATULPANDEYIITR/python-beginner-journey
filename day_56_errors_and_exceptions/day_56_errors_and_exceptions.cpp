"use strict";

/*
 * Event-driven repository governance model.
 * Errors are explicit domain events rather than generic string failures.
 */

class RepositoryError extends Error {
  constructor(message, code) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
  }
}

class ValidationError extends RepositoryError {}
class StateTransitionError extends RepositoryError {}
class PolicyViolationError extends RepositoryError {}
class MergeConflictError extends RepositoryError {}

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

const CheckState = Object.freeze({
  PASSING: "passing",
  FAILING: "failing",
  PENDING: "pending",
});

class EventBus {
  constructor() {
    this.handlers = new Map();
  }

  on(eventName, handler) {
    if (!this.handlers.has(eventName)) {
      this.handlers.set(eventName, new Set());
    }
    this.handlers.get(eventName).add(handler);
  }

  emit(eventName, payload) {
    for (const handler of this.handlers.get(eventName) ?? []) {
      handler(payload);
    }
  }
}

class Branch {
  constructor(name) {
    if (!name?.trim()) {
      throw new ValidationError("Branch name cannot be empty.", "INVALID_BRANCH");
    }
    this.name = name;
    this.commits = [];
    this.protected = false;
  }

  addCommit(commit) {
    if (!commit?.sha || commit.sha.length < 7) {
      throw new ValidationError("A valid commit SHA is required.", "INVALID_COMMIT");
    }
    if (!commit.message?.trim()) {
      throw new ValidationError("Commit message cannot be empty.", "INVALID_COMMIT");
    }
    this.commits.push(Object.freeze({ ...commit }));
  }
}

class Review {
  constructor(reviewer, state, commitSha) {
    if (!reviewer?.trim()) {
      throw new ValidationError("Reviewer is required.", "INVALID_REVIEWER");
    }
    if (!Object.values(ReviewState).includes(state)) {
      throw new ValidationError("Invalid review state.", "INVALID_REVIEW_STATE");
    }

    this.reviewer = reviewer;
    this.state = state;
    this.commitSha = commitSha;
    this.comments = [];
  }

  comment(body) {
    if (!body?.trim()) {
      throw new ValidationError("Review comment cannot be empty.", "EMPTY_COMMENT");
    }
    this.comments.push({
      body,
      resolved: false,
    });
  }

  resolveAll() {
    for (const comment of this.comments) {
      comment.resolved = true;
    }
  }
}

class PullRequest {
  constructor(number, source, target, draft = false, bus) {
    if (number <= 0) {
      throw new ValidationError("Pull Request number must be positive.", "INVALID_PR");
    }
    if (source === target) {
      throw new ValidationError(
        "Source and target branches must differ.",
        "SAME_BRANCH"
      );
    }

    this.number = number;
    this.source = source;
    this.target = target;
    this.state = draft ? PRState.DRAFT : PRState.OPEN;
    this.draft = draft;
    this.commits = [];
    this.changedFiles = new Set();
    this.reviews = [];
    this.checks = new Map();
    this.bus = bus;
  }

  transition(nextState) {
    const allowed = {
      [PRState.DRAFT]: new Set([PRState.OPEN, PRState.CLOSED]),
      [PRState.OPEN]: new Set([PRState.CLOSED, PRState.MERGED]),
      [PRState.CLOSED]: new Set([PRState.OPEN]),
      [PRState.MERGED]: new Set(),
    };

    if (!allowed[this.state]?.has(nextState)) {
      throw new StateTransitionError(
        `Invalid transition ${this.state} -> ${nextState}.`,
        "INVALID_TRANSITION"
      );
    }

    this.state = nextState;
    this.bus?.emit("pull_request.state_changed", {
      number: this.number,
      state: this.state,
    });
  }

  addCommit(commit) {
    if (this.state !== PRState.OPEN) {
      throw new StateTransitionError(
        "Only open Pull Requests accept commits.",
        "PR_NOT_OPEN"
      );
    }
    this.commits.push(commit);
    this.bus?.emit("pull_request.commit_added", {
      number: this.number,
      sha: commit.sha,
    });
  }

  addReview(review) {
    if (this.state !== PRState.OPEN) {
      throw new StateTransitionError(
        "Reviews require an open Pull Request.",
        "PR_NOT_OPEN"
      );
    }
    this.reviews.push(review);
    this.bus?.emit("review.submitted", {
      number: this.number,
      reviewer: review.reviewer,
      state: review.state,
    });
  }

  addCheck(name, state) {
    if (!Object.values(CheckState).includes(state)) {
      throw new ValidationError("Invalid status-check state.", "INVALID_CHECK");
    }
    this.checks.set(name, state);
    this.bus?.emit("check.updated", {
      number: this.number,
      name,
      state,
    });
  }
}

class BranchProtectionPolicy {
  constructor({
    requiredReviews = 0,
    requiredChecks = [],
    conversationsRequired = true,
    requireLinearHistory = true,
    allowForcePush = false,
    allowDeletion = false,
  } = {}) {
    if (!Number.isInteger(requiredReviews) || requiredReviews < 0) {
      throw new ValidationError(
        "Required review count must be a non-negative integer.",
        "INVALID_POLICY"
      );
    }

    this.requiredReviews = requiredReviews;
    this.requiredChecks = new Set(requiredChecks);
    this.conversationsRequired = conversationsRequired;
    this.requireLinearHistory = requireLinearHistory;
    this.allowForcePush = allowForcePush;
    this.allowDeletion = allowDeletion;
  }
}

class GovernanceEngine {
  constructor(policy) {
    this.policy = policy;
  }

  activeApprovers(pr) {
    return new Set(
      pr.reviews
        .filter((review) => review.state === ReviewState.APPROVED)
        .map((review) => review.reviewer)
    );
  }

  unresolvedComments(pr) {
    return pr.reviews
      .flatMap((review) => review.comments)
      .filter((comment) => !comment.resolved).length;
  }

  validate(pr) {
    if (pr.state !== PRState.OPEN) {
      throw new StateTransitionError(
        "Only open Pull Requests can be evaluated for merge.",
        "PR_NOT_OPEN"
      );
    }

    if (pr.draft) {
      throw new PolicyViolationError(
        "Draft Pull Requests cannot be merged.",
        "DRAFT_PR"
      );
    }

    if (pr.commits.length === 0 || pr.changedFiles.size === 0) {
      throw new ValidationError(
        "A merge candidate needs commits and changed files.",
        "EMPTY_CHANGESET"
      );
    }

    const approvals = this.activeApprovers(pr).size;
    if (approvals < this.policy.requiredReviews) {
      throw new PolicyViolationError(
        `Only ${approvals} of ${this.policy.requiredReviews} approvals exist.`,
        "INSUFFICIENT_APPROVALS"
      );
    }

    for (const requiredCheck of this.policy.requiredChecks) {
      const state = pr.checks.get(requiredCheck);
      if (state !== CheckState.PASSING) {
        throw new PolicyViolationError(
          `Required check is not passing: ${requiredCheck}.`,
          "CHECK_FAILED"
        );
      }
    }

    if (
      this.policy.conversationsRequired &&
      this.unresolvedComments(pr) > 0
    ) {
      throw new PolicyViolationError(
        "Unresolved review conversations remain.",
        "UNRESOLVED_CONVERSATION"
      );
    }

    if (this.policy.requireLinearHistory && pr.commits.length > 10) {
      throw new MergeConflictError(
        "The simplified model rejects an oversized history that requires ancestry inspection.",
        "ANCESTRY_REVIEW_REQUIRED"
      );
    }
  }

  merge(pr) {
    this.validate(pr);
    pr.transition(PRState.MERGED);
    return `Pull Request #${pr.number} merged into ${pr.target.name}.`;
  }
}

function main() {
  const bus = new EventBus();

  bus.on("pull_request.state_changed", (event) => {
    console.log(
      `[event] PR #${event.number} transitioned to ${event.state}`
    );
  });

  bus.on("review.submitted", (event) => {
    console.log(
      `[event] review by ${event.reviewer}: ${event.state}`
    );
  });

  bus.on("check.updated", (event) => {
    console.log(`[event] ${event.name}: ${event.state}`);
  });

  const mainBranch = new Branch("main");
  const featureBranch = new Branch("feature/audit");

  featureBranch.addCommit({
    sha: "abcdef1234567",
    message: "Add audit validation",
  });

  const pr = new PullRequest(
    42,
    featureBranch,
    mainBranch,
    false,
    bus
  );

  pr.changedFiles.add("audit.js");
  pr.addCommit(featureBranch.commits[0]);

  const alice = new Review(
    "alice",
    ReviewState.APPROVED,
    "abcdef1234567"
  );

  const bob = new Review(
    "bob",
    ReviewState.COMMENTED,
    "abcdef1234567"
  );

  bob.comment("Validate malformed audit identifiers.");

  pr.addReview(alice);
  pr.addReview(bob);

  pr.addCheck("unit-tests", CheckState.PASSING);
  pr.addCheck("security-scan", CheckState.PASSING);

  const engine = new GovernanceEngine(
    new BranchProtectionPolicy({
      requiredReviews: 2,
      requiredChecks: ["unit-tests", "security-scan"],
      conversationsRequired: true,
      requireLinearHistory: true,
    })
  );

  try {
    engine.merge(pr);
  } catch (error) {
    if (error instanceof RepositoryError) {
      console.log(`Expected rejection [${error.code}]: ${error.message}`);
    } else {
      throw error;
    }
  }

  bob.resolveAll();
  bob.state = ReviewState.APPROVED;

  console.log(engine.merge(pr));

  try {
    pr.addCommit({
      sha: "deadbeef12345",
      message: "Illegal post-merge change",
    });
  } catch (error) {
    console.log(`Expected state failure: ${error.message}`);
  }
}

main();
