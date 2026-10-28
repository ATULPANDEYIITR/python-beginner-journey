"use strict";

const { EventEmitter } = require("node:events");

const PullRequestState = Object.freeze({
  DRAFT: "draft",
  OPEN: "open",
  CLOSED: "closed",
  MERGED: "merged"
});

const ReviewState = Object.freeze({
  COMMENTED: "commented",
  CHANGES_REQUESTED: "changes_requested",
  APPROVED: "approved",
  DISMISSED: "dismissed"
});

class MergePolicyError extends Error {
  constructor(message) {
    super(message);
    this.name = "MergePolicyError";
  }
}

class Review {
  constructor({ reviewer, state, commitSha }) {
    if (!reviewer || !commitSha) {
      throw new TypeError("Reviewer and commit SHA are required.");
    }
    this.reviewer = reviewer;
    this.state = state;
    this.commitSha = commitSha;
    this.stale = false;
  }
}

class PullRequest extends EventEmitter {
  constructor({ number, sourceBranch, targetBranch, commits, draft = false }) {
    super();

    if (!Number.isInteger(number) || number <= 0) {
      throw new RangeError("PR number must be positive.");
    }
    if (!sourceBranch || !targetBranch || sourceBranch === targetBranch) {
      throw new TypeError("Source and target branches must be distinct.");
    }
    if (!Array.isArray(commits) || commits.length === 0) {
      throw new TypeError("A PR requires at least one commit.");
    }

    this.number = number;
    this.sourceBranch = sourceBranch;
    this.targetBranch = targetBranch;
    this.commits = [...commits];
    this.headSha = commits.at(-1);
    this.state = draft ? PullRequestState.DRAFT : PullRequestState.OPEN;
    this.reviews = [];
    this.statusChecks = new Map();
    this.unresolvedConversations = 0;
    this.synchronizedWithBase = true;
    this.mergeStrategy = "squash";
  }

  addReview(review) {
    if (![PullRequestState.OPEN, PullRequestState.DRAFT].includes(this.state)) {
      throw new MergePolicyError("Reviews cannot be added after closure or merge.");
    }
    this.reviews.push(review);
    this.emit("review", review);
  }

  setStatus(name, passed) {
    if (!name) throw new TypeError("Status check name is required.");
    this.statusChecks.set(name, Boolean(passed));
    this.emit("status", { name, passed: Boolean(passed) });
  }

  activeApprovals() {
    return this.reviews.filter(
      (review) =>
        review.state === ReviewState.APPROVED &&
        !review.stale &&
        review.commitSha === this.headSha
    ).length;
  }

  synchronize() {
    this.synchronizedWithBase = true;
    for (const review of this.reviews) {
      review.stale = true;
    }
    this.emit("synchronized");
  }
}

class RepositoryGovernance {
  constructor(name, protection) {
    this.name = name;
    this.branches = new Set(["main", "develop"]);
    this.protection = {
      requiredApprovals: protection.requiredApprovals ?? 2,
      requiredChecks: new Set(protection.requiredChecks ?? []),
      requireResolvedConversations:
        protection.requireResolvedConversations ?? true,
      requireLinearHistory: protection.requireLinearHistory ?? true
    };
    this.commits = new Set();
    this.pullRequests = new Map();
    this.nextPrNumber = 1;
    this.audit = [];
  }

  createCommit(sha) {
    if (typeof sha !== "string" || sha.length < 7) {
      throw new TypeError("Commit SHA must contain at least seven characters.");
    }
    if (this.commits.has(sha)) {
      throw new MergePolicyError("Duplicate commit.");
    }
    this.commits.add(sha);
  }

  openPullRequest(sourceBranch, targetBranch, commits, draft = false) {
    if (!this.branches.has(sourceBranch) || !this.branches.has(targetBranch)) {
      throw new MergePolicyError("Unknown branch.");
    }
    if (sourceBranch === targetBranch) {
      throw new MergePolicyError("Source and target branches must differ.");
    }
    if (!commits.every((commit) => this.commits.has(commit))) {
      throw new MergePolicyError("PR contains an unknown commit.");
    }

    const pr = new PullRequest({
      number: this.nextPrNumber++,
      sourceBranch,
      targetBranch,
      commits,
      draft
    });

    pr.on("review", (review) => {
      this.audit.push(
        `PR-${pr.number}: review by ${review.reviewer} -> ${review.state}`
      );
    });

    pr.on("status", ({ name, passed }) => {
      this.audit.push(`PR-${pr.number}: ${name}=${passed}`);
    });

    pr.on("synchronized", () => {
      this.audit.push(`PR-${pr.number}: synchronized`);
    });

    this.pullRequests.set(pr.number, pr);
    return pr;
  }

  evaluate(pr) {
    const failures = [];

    if (pr.state !== PullRequestState.OPEN) {
      failures.push("PR is not open.");
    }

    if (!pr.synchronizedWithBase) {
      failures.push("PR is behind the base branch.");
    }

    if (pr.activeApprovals() < this.protection.requiredApprovals) {
      failures.push(
        `Requires ${this.protection.requiredApprovals} current approvals.`
      );
    }

    for (const check of this.protection.requiredChecks) {
      if (pr.statusChecks.get(check) !== true) {
        failures.push(`Required check '${check}' is not passing.`);
      }
    }

    if (
      this.protection.requireResolvedConversations &&
      pr.unresolvedConversations > 0
    ) {
      failures.push("Unresolved review conversations remain.");
    }

    if (
      this.protection.requireLinearHistory &&
      pr.mergeStrategy === "merge"
    ) {
      failures.push("Merge commits are prohibited by linear-history policy.");
    }

    return { eligible: failures.length === 0, failures };
  }

  async merge(pr) {
    try {
      const result = this.evaluate(pr);

      // The else-style success path is represented by an explicit branch
      // because JavaScript has no native try/else construct.
      if (!result.eligible) {
        throw new MergePolicyError(result.failures.join(" "));
      } else {
        pr.state = PullRequestState.MERGED;
        this.audit.push(`PR-${pr.number}: merged`);
        return true;
      }
    } catch (error) {
      if (error instanceof MergePolicyError) {
        this.audit.push(`PR-${pr.number}: rejected - ${error.message}`);
        return false;
      }
      throw error;
    } finally {
      // finally is guaranteed to execute after success or handled failure.
      this.audit.push(`PR-${pr.number}: merge attempt finalized`);
    }
  }
}

async function runCheck(pr, name, checker) {
  try {
    const passed = await Promise.resolve().then(() => checker(pr));
    pr.setStatus(name, passed);
    return passed;
  } catch (error) {
    pr.setStatus(name, false);
    console.error(`Check '${name}' failed: ${error.message}`);
    return false;
  } finally {
    console.log(`Check '${name}' finished.`);
  }
}

async function main() {
  const repository = new RepositoryGovernance("payments-platform", {
    requiredApprovals: 2,
    requiredChecks: ["tests", "security"],
    requireResolvedConversations: true,
    requireLinearHistory: true
  });

  for (const sha of ["1111111abc", "2222222def"]) {
    repository.createCommit(sha);
  }

  const pr = repository.openPullRequest(
    "develop",
    "main",
    ["1111111abc", "2222222def"]
  );

  pr.addReview(
    new Review({
      reviewer: "alice",
      state: ReviewState.APPROVED,
      commitSha: pr.headSha
    })
  );

  pr.addReview(
    new Review({
      reviewer: "bob",
      state: ReviewState.APPROVED,
      commitSha: pr.headSha
    })
  );

  await runCheck(pr, "tests", (current) => current.commits.length <= 20);
  await runCheck(pr, "security", (current) => current.headSha.length >= 7);

  const eligibility = repository.evaluate(pr);

  if (eligibility.eligible) {
    console.log("PR is eligible for merge.");
  } else {
    console.log("PR is blocked:", eligibility.failures);
  }

  const merged = await repository.merge(pr);
  console.log(`Merged: ${merged}`);
  console.log(`State: ${pr.state}`);

  console.log("\nAudit trail:");
  for (const event of repository.audit) {
    console.log(`  ${event}`);
  }

  // Demonstrate stale approvals after base synchronization.
  if (pr.state === PullRequestState.MERGED) {
    console.log("\nMerged PR does not require further approval.");
  } else {
    pr.synchronize();
    console.log(
      `Current approvals after synchronization: ${pr.activeApprovals()}`
    );
  }
}

main().catch((error) => {
  console.error("Fatal workflow error:", error);
  process.exitCode = 1;
});
