'use strict';

/**
 * Event-driven repository governance and merge-policy evaluation.
 * Run with Node.js 18 or later.
 */

const { EventEmitter } = require('node:events');
const crypto = require('node:crypto');

const PRState = Object.freeze({
  DRAFT: 'draft',
  OPEN: 'open',
  MERGED: 'merged',
  CLOSED: 'closed'
});

const ReviewState = Object.freeze({
  COMMENTED: 'commented',
  APPROVED: 'approved',
  CHANGES_REQUESTED: 'changes_requested',
  DISMISSED: 'dismissed'
});

class ValidationError extends Error {}
class GovernanceError extends Error {}

function requireText(value, field) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new ValidationError(`${field} must be a non-empty string`);
  }
  return value.trim();
}

function createCommit(message, parent = null) {
  const cleanMessage = requireText(message, 'Commit message');
  const sha = crypto
    .createHash('sha256')
    .update(`${parent ?? 'root'}:${cleanMessage}:${crypto.randomUUID()}`)
    .digest('hex')
    .slice(0, 12);

  return Object.freeze({
    sha,
    message: cleanMessage,
    parent,
    createdAt: new Date().toISOString()
  });
}

class Branch {
  constructor(name, commits = []) {
    this.name = requireText(name, 'Branch name');
    this.commits = [...commits];
    this.deleted = false;
    this.forcePushEnabled = false;
  }

  get head() {
    return this.commits.at(-1)?.sha ?? null;
  }

  addCommit(commit) {
    if (this.deleted) throw new GovernanceError('Branch was deleted');
    if (!commit || typeof commit.sha !== 'string') {
      throw new ValidationError('A valid commit is required');
    }
    if (this.commits.some(existing => existing.sha === commit.sha)) {
      throw new ValidationError('Duplicate commit SHA');
    }
    this.commits.push(commit);
  }
}

class BranchProtection {
  constructor({
    requiredApprovals = 2,
    requiredChecks = ['build', 'tests', 'security'],
    requireResolvedConversations = true,
    requireLinearHistory = true,
    restrictDirectPush = true,
    allowForcePush = false,
    allowDeletion = false,
    allowAdminBypass = false
  } = {}) {
    if (!Number.isInteger(requiredApprovals) || requiredApprovals < 0) {
      throw new ValidationError(
        'requiredApprovals must be a non-negative integer'
      );
    }
    if (!Array.isArray(requiredChecks) ||
        requiredChecks.some(name => typeof name !== 'string' || !name.trim())) {
      throw new ValidationError('requiredChecks must contain valid names');
    }

    this.requiredApprovals = requiredApprovals;
    this.requiredChecks = Object.freeze([...new Set(requiredChecks)]);
    this.requireResolvedConversations = requireResolvedConversations;
    this.requireLinearHistory = requireLinearHistory;
    this.restrictDirectPush = restrictDirectPush;
    this.allowForcePush = allowForcePush;
    this.allowDeletion = allowDeletion;
    this.allowAdminBypass = allowAdminBypass;
  }
}

class PullRequest extends EventEmitter {
  constructor({
    number,
    author,
    source,
    target,
    eligibleReviewers,
    mergeStrategy = 'squash'
  }) {
    super();
    if (!Number.isInteger(number) || number <= 0) {
      throw new ValidationError('PR number must be a positive integer');
    }
    this.number = number;
    this.author = requireText(author, 'Author');
    if (!(source instanceof Branch) || !(target instanceof Branch)) {
      throw new ValidationError('Source and target must be Branch instances');
    }
    if (source === target || source.name === target.name) {
      throw new ValidationError('Source and target branches must differ');
    }

    this.source = source;
    this.target = target;
    this.eligibleReviewers = new Set(eligibleReviewers);
    if (this.eligibleReviewers.has(author)) {
      throw new ValidationError('Author cannot review their own PR');
    }

    this.mergeStrategy = mergeStrategy;
    this.state = PRState.OPEN;
    this.headSha = source.head;
    this.baseSha = target.head;
    this.reviews = [];
    this.checks = new Map();
    this.conversations = new Map();
    this.events = [];
    this.mergedCommit = null;
    this.record('opened', { number, author });
  }

  record(type, details = {}) {
    const event = Object.freeze({
      type,
      details: Object.freeze({ ...details }),
      at: new Date().toISOString()
    });
    this.events.push(event);
    this.emit(type, event);
  }

  requireOpen() {
    if (this.state !== PRState.OPEN) {
      throw new GovernanceError(`PR must be open, current state: ${this.state}`);
    }
  }

  markDraft() {
    this.requireOpen();
    this.state = PRState.DRAFT;
    this.record('drafted');
  }

  markReady() {
    if (this.state !== PRState.DRAFT) {
      throw new GovernanceError('Only a draft PR can become ready');
    }
    this.state = PRState.OPEN;
    this.record('ready');
  }

  synchronize() {
    this.requireOpen();
    this.headSha = this.source.head;
    this.baseSha = this.target.head;
    this.record('synchronized', {
      headSha: this.headSha,
      baseSha: this.baseSha
    });
  }

  submitReview(reviewer, state, comments = []) {
    this.requireOpen();
    if (!this.eligibleReviewers.has(reviewer)) {
      throw new GovernanceError('Reviewer is not eligible');
    }
    if (reviewer === this.author) {
      throw new GovernanceError('Self-approval is prohibited');
    }
    if (!Object.values(ReviewState).includes(state) ||
        state === ReviewState.DISMISSED) {
      throw new ValidationError('Invalid submitted review state');
    }
    if (!this.headSha) throw new GovernanceError('Cannot review an empty PR');
    if (!Array.isArray(comments) ||
        comments.some(comment => typeof comment !== 'string')) {
      throw new ValidationError('Comments must be an array of strings');
    }

    const review = {
      id: crypto.randomUUID(),
      reviewer,
      state,
      headSha: this.headSha,
      comments: comments.map((body, index) => ({
        id: `${this.number}-${reviewer}-${index}-${crypto.randomUUID()}`,
        body,
        resolved: false,
        createdAt: new Date().toISOString()
      })),
      submittedAt: new Date().toISOString()
    };
    this.reviews.push(review);
    this.record('review_submitted', {
      reviewer,
      state,
      headSha: this.headSha
    });
    return review;
  }

  dismissReview(reviewer) {
    this.requireOpen();
    const latest = this.latestReviews().get(reviewer);
    if (!latest || latest.state === ReviewState.DISMISSED) {
      throw new GovernanceError('No active review decision to dismiss');
    }
    latest.state = ReviewState.DISMISSED;
    this.record('review_dismissed', { reviewer });
  }

  latestReviews() {
    const latest = new Map();
    for (const review of this.reviews) latest.set(review.reviewer, review);
    return latest;
  }

  setCheck(name, status) {
    this.requireOpen();
    requireText(name, 'Check name');
    if (!['pending', 'success', 'failure'].includes(status)) {
      throw new ValidationError('Check status must be pending, success, or failure');
    }
    this.checks.set(name, { status, headSha: this.headSha });
    this.record('check_updated', { name, status, headSha: this.headSha });
  }

  addConversation(id, body) {
    this.requireOpen();
    requireText(id, 'Conversation ID');
    requireText(body, 'Conversation body');
    if (this.conversations.has(id)) {
      throw new ValidationError('Conversation ID already exists');
    }
    this.conversations.set(id, { id, body, resolved: false });
  }

  resolveConversation(id) {
    this.requireOpen();
    const conversation = this.conversations.get(id);
    if (!conversation) throw new GovernanceError('Conversation not found');
    conversation.resolved = true;
    this.record('conversation_resolved', { id });
  }

  evaluate(policy) {
    const blockers = [];
    if (this.state !== PRState.OPEN) blockers.push('PR is not open');
    if (!this.headSha) blockers.push('Source branch is empty');
    if (this.headSha !== this.source.head) blockers.push('Source head is stale');
    if (this.baseSha !== this.target.head) blockers.push('Target base is stale');

    const approvals = new Set();
    for (const [reviewer, review] of this.latestReviews()) {
      if (review.state === ReviewState.APPROVED &&
          review.headSha === this.headSha &&
          this.eligibleReviewers.has(reviewer)) {
        approvals.add(reviewer);
      }
    }

    if (approvals.size < policy.requiredApprovals) {
      blockers.push(
        `Need ${policy.requiredApprovals} current approvals; found ${approvals.size}`
      );
    }

    for (const name of policy.requiredChecks) {
      const check = this.checks.get(name);
      if (!check || check.status !== 'success' || check.headSha !== this.headSha) {
        blockers.push(`Check missing, failing, pending, or stale: ${name}`);
      }
    }

    if (policy.requireResolvedConversations &&
        [...this.conversations.values()].some(item => !item.resolved)) {
      blockers.push('Unresolved conversations remain');
    }

    if (policy.requireLinearHistory && this.mergeStrategy === 'merge') {
      blockers.push('Merge commits violate linear-history policy');
    }

    if (!['merge', 'squash', 'rebase'].includes(this.mergeStrategy)) {
      blockers.push('Unsupported merge strategy');
    }

    return Object.freeze({
      eligible: blockers.length === 0,
      blockers: Object.freeze(blockers),
      approvals: Object.freeze([...approvals])
    });
  }

  merge(policy) {
    this.requireOpen();
    const result = this.evaluate(policy);
    if (!result.eligible) {
      throw new GovernanceError(`Merge blocked: ${result.blockers.join('; ')}`);
    }

    const commit = createCommit(
      `Merge PR #${this.number} (${this.mergeStrategy})`,
      this.target.head
    );
    this.target.addCommit(commit);
    this.mergedCommit = commit.sha;
    this.state = PRState.MERGED;
    this.record('merged', { commit: commit.sha, strategy: this.mergeStrategy });
    return commit;
  }

  close() {
    this.requireOpen();
    this.state = PRState.CLOSED;
    this.record('closed');
  }

  reopen() {
    if (this.state !== PRState.CLOSED) {
      throw new GovernanceError('Only closed, unmerged PRs can reopen');
    }
    this.state = PRState.OPEN;
    this.headSha = this.source.head;
    this.baseSha = this.target.head;
    this.record('reopened');
  }
}

function runChecks(pr, checks) {
  const results = Promise.all(
    Object.entries(checks).map(async ([name, check]) => {
      try {
        const passed = await check();
        pr.setCheck(name, passed ? 'success' : 'failure');
        return { name, passed: Boolean(passed) };
      } catch (error) {
        pr.setCheck(name, 'failure');
        return { name, passed: false, error: error.message };
      }
    })
  );
  return results;
}

async function main() {
  const mainBranch = new Branch('main', [
    createCommit('Initial release')
  ]);
  const feature = new Branch('feature/payment-validation', [
    createCommit('Validate payment requests')
  ]);

  const policy = new BranchProtection({
    requiredApprovals: 2,
    requiredChecks: ['build', 'tests', 'security'],
    requireResolvedConversations: true,
    requireLinearHistory: true,
    restrictDirectPush: true
  });

  const pr = new PullRequest({
    number: 42,
    author: 'developer',
    source: feature,
    target: mainBranch,
    eligibleReviewers: ['alex', 'sam', 'jordan'],
    mergeStrategy: 'squash'
  });

  pr.on('review_submitted', event => {
    console.log(`Review event: ${event.details.reviewer} -> ${event.details.state}`);
  });
  pr.on('merged', event => {
    console.log(`Merged commit: ${event.details.commit}`);
  });

  pr.addConversation('thread-1', 'Add a duplicate transaction test.');

  await runChecks(pr, {
    build: async () => true,
    tests: async () => 120 >= 120,
    security: async () => true
  });

  pr.submitReview('alex', ReviewState.APPROVED, [
    'Missing identifier validation is covered.'
  ]);
  pr.submitReview('sam', ReviewState.CHANGES_REQUESTED, [
    'Test duplicate transaction identifiers.'
  ]);

  console.log('Initial evaluation:', pr.evaluate(policy));

  pr.submitReview('sam', ReviewState.APPROVED, [
    'Duplicate transaction test now passes.'
  ]);
  pr.resolveConversation('thread-1');

  const evaluation = pr.evaluate(policy);
  console.log('Final evaluation:', evaluation);
  if (!evaluation.eligible) throw new GovernanceError('Unexpected blockers');

  pr.merge(policy);

  // A new commit invalidates the stored head snapshot and previous approvals.
  const followUp = createCommit('Handle empty payment identifiers', feature.head);
  feature.addCommit(followUp);
  if (pr.evaluate(policy).eligible) {
    throw new Error('Stale branch state should prevent merging');
  }
  console.log('Stale state correctly blocks a subsequent merge.');

  try {
    new BranchProtection({ requiredApprovals: -1 });
  } catch (error) {
    console.log(`Policy validation: ${error.message}`);
  }
}

main().catch(error => {
  console.error(`Workflow failed: ${error.name}: ${error.message}`);
  process.exitCode = 1;
});
