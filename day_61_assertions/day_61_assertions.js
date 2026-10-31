'use strict';

/*
 * Assertions: executable JavaScript learning artifact.
 *
 * Demonstrates:
 * - Node.js assertions
 * - explicit validation versus assertions
 * - preconditions and postconditions
 * - object invariants
 * - event-driven assertion failures
 * - asynchronous assertions
 * - policy-style validation
 */

const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

function requireCondition(condition, message) {
    if (!condition) {
        throw new ValidationError(message);
    }
}

function ensure(condition, message) {
    assert.ok(condition, message);
}

class Repository {
    constructor(name, defaultBranch = 'main') {
        requireCondition(
            typeof name === 'string' && name.trim().length > 0,
            'repository name is required'
        );
        requireCondition(
            typeof defaultBranch === 'string' && defaultBranch.trim().length > 0,
            'default branch is required'
        );

        this.name = name;
        this.defaultBranch = defaultBranch;
        this.commits = new Set();
        this.#checkInvariants();
    }

    addCommit(commitId) {
        requireCondition(
            typeof commitId === 'string' && commitId.trim().length > 0,
            'commit ID is required'
        );

        requireCondition(!this.commits.has(commitId), 'duplicate commit ID');

        const before = this.commits.size;
        this.commits.add(commitId);

        ensure(
            this.commits.size === before + 1,
            'adding a commit must increase repository size'
        );

        this.#checkInvariants();
    }

    #checkInvariants() {
        assert.ok(this.name.trim(), 'repository name invariant failed');
        assert.ok(this.defaultBranch.trim(), 'default branch invariant failed');
        assert.ok(this.commits instanceof Set, 'commit collection invariant failed');
    }
}

class PullRequest extends EventEmitter {
    constructor(number, sourceBranch, targetBranch, commits = [], draft = false) {
        super();

        requireCondition(Number.isInteger(number) && number > 0, 'PR number must be positive');
        requireCondition(
            sourceBranch !== targetBranch,
            'source and target branches must differ'
        );

        this.number = number;
        this.sourceBranch = sourceBranch;
        this.targetBranch = targetBranch;
        this.commits = new Set(commits);
        this.draft = draft;
        this.merged = false;

        this.#checkInvariants();
    }

    addCommit(commitId) {
        requireCondition(!this.merged, 'merged PRs cannot receive commits');
        requireCondition(
            typeof commitId === 'string' && commitId.trim().length > 0,
            'commit ID is required'
        );
        requireCondition(!this.commits.has(commitId), 'duplicate PR commit');

        this.commits.add(commitId);
        this.emit('commitAdded', { number: this.number, commitId });

        this.#checkInvariants();
    }

    markReady() {
        requireCondition(!this.merged, 'merged PR cannot become ready');
        this.draft = false;
        this.emit('ready', this.number);
        this.#checkInvariants();
    }

    merge() {
        requireCondition(!this.merged, 'PR is already merged');
        requireCondition(this.commits.size > 0, 'PR must contain a commit');

        this.merged = true;
        this.emit('merged', this.number);
        this.#checkInvariants();
    }

    #checkInvariants() {
        assert.ok(this.number > 0, 'PR number invariant failed');
        assert.notEqual(
            this.sourceBranch,
            this.targetBranch,
            'branch invariant failed'
        );
        assert.ok(
            !this.merged || !this.draft,
            'merged PR cannot remain draft'
        );
    }
}

function calculateAverage(values) {
    requireCondition(Array.isArray(values), 'values must be an array');
    requireCondition(values.length > 0, 'at least one value is required');
    requireCondition(
        values.every(value => typeof value === 'number' && Number.isFinite(value)),
        'all values must be finite numbers'
    );

    const average = values.reduce((sum, value) => sum + value, 0) / values.length;

    ensure(
        average >= Math.min(...values) && average <= Math.max(...values),
        'average postcondition failed'
    );

    return average;
}

async function verifyAsyncState() {
    const state = await Promise.resolve({
        ready: true,
        count: 3
    });

    assert.equal(state.ready, true);
    assert.equal(state.count, 3);

    return state;
}

function runEventDrivenExample() {
    const pullRequest = new PullRequest(
        17,
        'feature/assertions',
        'main',
        ['c1'],
        true
    );

    const events = [];

    pullRequest.on('commitAdded', event => events.push(`commit:${event.commitId}`));
    pullRequest.on('ready', number => events.push(`ready:${number}`));
    pullRequest.on('merged', number => events.push(`merged:${number}`));

    pullRequest.addCommit('c2');
    pullRequest.markReady();
    pullRequest.merge();

    assert.deepEqual(events, ['commit:c2', 'ready:17', 'merged:17']);
}

async function main() {
    const repository = new Repository('assertion-lab');
    repository.addCommit('c1');
    repository.addCommit('c2');

    assert.equal(repository.commits.size, 2);
    assert.ok(repository.commits.has('c1'));

    try {
        repository.addCommit('c1');
        assert.fail('duplicate commit should have failed');
    } catch (error) {
        assert.ok(error instanceof ValidationError);
    }

    const pullRequest = new PullRequest(
        42,
        'feature/assertions',
        'main',
        ['c1']
    );

    pullRequest.addCommit('c2');
    pullRequest.merge();

    assert.equal(pullRequest.merged, true);

    try {
        pullRequest.addCommit('c3');
        assert.fail('mutation of merged PR should have failed');
    } catch (error) {
        assert.ok(error instanceof ValidationError);
    }

    assert.equal(calculateAverage([10, 20, 30]), 20);

    try {
        calculateAverage([]);
        assert.fail('empty input should have failed');
    } catch (error) {
        assert.ok(error instanceof ValidationError);
    }

    runEventDrivenExample();

    const state = await verifyAsyncState();
    assert.equal(state.count, 3);

    console.log('All JavaScript assertion demonstrations and tests passed.');
}

main().catch(error => {
    console.error('Execution failed:', error.message);
    process.exitCode = 1;
});
