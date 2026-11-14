"use strict";

/*
 * Project Dependency Management
 * Event-driven dependency governance engine.
 *
 * Node.js 18+; no external packages required.
 */

const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const path = require("node:path");
const EventEmitter = require("node:events");

class DependencyError extends Error {}
class ValidationError extends DependencyError {}
class GovernanceError extends DependencyError {}

const PRState = Object.freeze({
    DRAFT: "draft",
    OPEN: "open",
    MERGED: "merged",
    CLOSED: "closed"
});

const ReviewState = Object.freeze({
    APPROVED: "approved",
    CHANGES_REQUESTED: "changes_requested",
    COMMENTED: "commented",
    DISMISSED: "dismissed"
});

const CheckState = Object.freeze({
    PENDING: "pending",
    PASSED: "passed",
    FAILED: "failed"
});

function parseVersion(value) {
    if (
        typeof value !== "string" ||
        !/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(value)
    ) {
        throw new ValidationError(`Invalid version: ${value}`);
    }

    return value.split(".").map(Number);
}

function compareVersions(a, b) {
    const left = parseVersion(a);
    const right = parseVersion(b);

    for (let i = 0; i < 3; i++) {
        if (left[i] !== right[i]) {
            return left[i] - right[i];
        }
    }

    return 0;
}

function hash(value) {
    return crypto.createHash("sha256")
        .update(value)
        .digest("hex");
}

class Dependency {
    constructor({
        name,
        version,
        minimum,
        maximum = null,
        direct = true,
        license = "MIT",
        vulnerabilities = 0,
        dependencies = [],
        source = "public-registry"
    }) {
        if (!/^[A-Za-z0-9_.-]{1,100}$/.test(name)) {
            throw new ValidationError("Invalid package name");
        }

        parseVersion(version);
        parseVersion(minimum);

        if (maximum !== null) parseVersion(maximum);

        if (compareVersions(version, minimum) < 0) {
            throw new ValidationError(`${name} is below minimum version`);
        }

        if (maximum && compareVersions(version, maximum) > 0) {
            throw new ValidationError(`${name} exceeds maximum version`);
        }

        if (!Number.isInteger(vulnerabilities) || vulnerabilities < 0) {
            throw new ValidationError("Invalid vulnerability count");
        }

        if (!Array.isArray(dependencies)) {
            throw new ValidationError("Dependencies must be an array");
        }

        this.name = name;
        this.version = version;
        this.minimum = minimum;
        this.maximum = maximum;
        this.direct = direct;
        this.license = license;
        this.vulnerabilities = vulnerabilities;
        this.dependencies = [...new Set(dependencies)];
        this.source = source;
    }
}

class Repository extends EventEmitter {
    constructor(name, policy = {}) {
        super();

        this.name = name;
        this.dependencies = new Map();
        this.branches = new Map([
            ["main", new Map()]
        ]);
        this.protectedBranches = new Set(["main"]);
        this.pullRequests = new Map();
        this.nextPR = 1;

        this.policy = {
            allowedLicenses: new Set([
                "MIT",
                "Apache-2.0",
                "BSD-3-Clause"
            ]),
            maximumVulnerabilities: 0,
            requiredApprovals: 2,
            requirePassingChecks: true,
            requireResolvedConversations: true,
            requireLockfile: true,
            dismissStaleApprovals: true,
            rejectDirectPush: true,
            rejectForcePush: true,
            rejectBranchDeletion: true,
            requireLinearHistory: true,
            administratorBypass: false,
            ...policy
        };
    }

    addDependency(dependency) {
        if (!(dependency instanceof Dependency)) {
            throw new ValidationError("Expected a Dependency object");
        }

        if (this.dependencies.has(dependency.name)) {
            throw new ValidationError("Duplicate dependency");
        }

        this.dependencies.set(dependency.name, dependency);
        this.emit("dependency:added", dependency);
    }

    validateGraph() {
        const graph = this.dependencies;
        const colors = new Map();
        const order = [];

        // DFS detects cycles and produces prerequisite-first ordering.
        const visit = (name) => {
            const color = colors.get(name) || 0;

            if (color === 1) {
                throw new GovernanceError(
                    `Circular dependency involving ${name}`
                );
            }

            if (color === 2) return;

            const dependency = graph.get(name);

            if (!dependency) {
                throw new ValidationError(`Unknown dependency: ${name}`);
            }

            colors.set(name, 1);

            for (const child of dependency.dependencies) {
                if (!graph.has(child)) {
                    throw new ValidationError(
                        `Missing transitive dependency: ${child}`
                    );
                }
                visit(child);
            }

            colors.set(name, 2);
            order.push(name);
        };

        for (const name of [...graph.keys()].sort()) {
            visit(name);
        }

        return order;
    }

    audit() {
        const violations = [];

        for (const dependency of this.dependencies.values()) {
            if (!this.policy.allowedLicenses.has(dependency.license)) {
                violations.push(
                    `${dependency.name}: prohibited license ${dependency.license}`
                );
            }

            if (
                dependency.vulnerabilities >
                this.policy.maximumVulnerabilities
            ) {
                violations.push(
                    `${dependency.name}: vulnerability threshold exceeded`
                );
            }
        }

        try {
            this.validateGraph();
        } catch (error) {
            violations.push(error.message);
        }

        return violations;
    }

    planUpdates(available) {
        const plan = new Map();

        for (const [name, version] of Object.entries(available)) {
            const current = this.dependencies.get(name);

            if (!current) {
                throw new ValidationError(`Unknown dependency: ${name}`);
            }

            parseVersion(version);

            if (compareVersions(version, current.version) <= 0) {
                continue;
            }

            if (current.maximum &&
                compareVersions(version, current.maximum) > 0) {
                continue;
            }

            plan.set(name, version);
        }

        return plan;
    }

    createPullRequest({
        source = "dependency/update",
        target = "main",
        changes,
        draft = false
    }) {
        if (source === target) {
            throw new ValidationError("Source and target must differ");
        }

        if (!this.protectedBranches.has(target)) {
            throw new ValidationError("Target is not protected");
        }

        if (!(changes instanceof Map) || changes.size === 0) {
            throw new ValidationError("A nonempty update plan is required");
        }

        for (const [name, version] of changes) {
            const dependency = this.dependencies.get(name);

            if (!dependency) {
                throw new ValidationError(`Unknown package: ${name}`);
            }

            if (compareVersions(version, dependency.version) <= 0) {
                throw new ValidationError(`Not an upgrade: ${name}`);
            }

            if (dependency.maximum &&
                compareVersions(version, dependency.maximum) > 0) {
                throw new ValidationError(`Version exceeds policy: ${name}`);
            }
        }

        const id = this.nextPR++;

        const pr = {
            id,
            source,
            target,
            changes: new Map(changes),
            state: draft ? PRState.DRAFT : PRState.OPEN,
            draft,
            reviews: new Map(),
            checks: new Map(),
            conversations: new Map(),
            synchronized: true,
            conflicts: false,
            headCommit: hash(`${id}:${JSON.stringify([...changes])}`)
        };

        this.pullRequests.set(id, pr);
        this.emit("pull-request:opened", pr);

        return pr;
    }

    async runChecks(pr, checkFunctions) {
        if (pr.state !== PRState.OPEN || pr.draft) {
            throw new GovernanceError("PR is not ready for checks");
        }

        const results = await Promise.all(
            Object.entries(checkFunctions).map(async ([name, fn]) => {
                try {
                    const passed = await fn(pr);
                    return [name, passed ? CheckState.PASSED : CheckState.FAILED];
                } catch {
                    return [name, CheckState.FAILED];
                }
            })
        );

        pr.checks = new Map(results);

        this.emit("checks:completed", {
            pr: pr.id,
            checks: pr.checks
        });

        return pr.checks;
    }

    addReview(pr, reviewer, state) {
        if (pr.state !== PRState.OPEN || pr.draft) {
            throw new GovernanceError("PR is not reviewable");
        }

        if (!Object.values(ReviewState).includes(state)) {
            throw new ValidationError("Invalid review state");
        }

        if (!reviewer || typeof reviewer !== "string") {
            throw new ValidationError("Reviewer identity is required");
        }

        pr.reviews.set(reviewer, {
            reviewer,
            state,
            commit: pr.headCommit,
            timestamp: new Date().toISOString()
        });

        this.emit("review:submitted", {
            pr: pr.id,
            reviewer,
            state
        });
    }

    resolveConversation(pr, id) {
        if (!pr.conversations.has(id)) {
            throw new ValidationError("Conversation does not exist");
        }

        pr.conversations.set(id, true);
    }

    pushCommit(pr, changes) {
        if (pr.state !== PRState.OPEN) {
            throw new GovernanceError("PR is not open");
        }

        for (const [name, version] of changes) {
            if (!pr.changes.has(name)) {
                throw new ValidationError("Unexpected dependency change");
            }
            parseVersion(version);
            pr.changes.set(name, version);
        }

        pr.headCommit = hash(
            pr.headCommit + JSON.stringify([...pr.changes])
        );

        // Existing reviews become stale; CI must run again.
        if (this.policy.dismissStaleApprovals) {
            for (const [reviewer, review] of pr.reviews) {
                if (review.state === ReviewState.APPROVED) {
                    pr.reviews.set(reviewer, {
                        ...review,
                        state: ReviewState.DISMISSED
                    });
                }
            }
        }

        for (const name of pr.checks.keys()) {
            pr.checks.set(name, CheckState.PENDING);
        }

        this.emit("commit:pushed", pr);
    }

    evaluateMerge(pr) {
        const failures = [];

        if (pr.state !== PRState.OPEN) failures.push("PR is not open");
        if (pr.draft) failures.push("Draft PR cannot be merged");
        if (pr.conflicts) failures.push("Merge conflicts exist");
        if (!pr.synchronized) failures.push("Base branch is outdated");

        if (this.policy.requireResolvedConversations) {
            if ([...pr.conversations.values()].some(v => !v)) {
                failures.push("Unresolved review conversations");
            }
        }

        if (this.policy.requirePassingChecks) {
            if (pr.checks.size === 0) {
                failures.push("No required checks configured");
            } else if (
                [...pr.checks.values()].some(
                    state => state !== CheckState.PASSED
                )
            ) {
                failures.push("Required status checks have not passed");
            }
        }

        const currentReviews = [...pr.reviews.values()].filter(
            review => review.commit === pr.headCommit
        );

        if (currentReviews.some(
            review => review.state === ReviewState.CHANGES_REQUESTED
        )) {
            failures.push("Changes requested by reviewer");
        }

        const approvals = new Set(
            currentReviews
                .filter(review => review.state === ReviewState.APPROVED)
                .map(review => review.reviewer)
        );

        if (approvals.size < this.policy.requiredApprovals) {
            failures.push(
                `Insufficient approvals: ${approvals.size}/` +
                `${this.policy.requiredApprovals}`
            );
        }

        failures.push(...this.audit());

        return {
            eligible: failures.length === 0,
            failures
        };
    }

    merge(pr, strategy = "squash") {
        const allowedStrategies = new Set([
            "merge",
            "squash",
            "rebase"
        ]);

        if (!allowedStrategies.has(strategy)) {
            throw new ValidationError("Unsupported merge strategy");
        }

        const result = this.evaluateMerge(pr);

        if (!result.eligible) {
            throw new GovernanceError(result.failures.join("; "));
        }

        // Apply proposed dependency state only after governance succeeds.
        for (const [name, version] of pr.changes) {
            this.dependencies.get(name).version = version;
        }

        pr.state = PRState.MERGED;
        pr.mergeCommit = hash(
            `${pr.id}:${pr.headCommit}:${strategy}`
        );

        this.emit("pull-request:merged", pr);

        return pr.mergeCommit;
    }

    generateLockfile() {
        const order = this.validateGraph();
        const entries = {};

        for (const name of order) {
            const dep = this.dependencies.get(name);

            entries[name] = {
                version: dep.version,
                direct: dep.direct,
                license: dep.license,
                dependencies: [...dep.dependencies].sort(),
                source: dep.source
            };
        }

        const canonical = JSON.stringify(entries);

        return {
            format: 1,
            generatedAt: new Date().toISOString(),
            dependencies: entries,
            integrity: hash(canonical)
        };
    }

    async saveLockfile(filename) {
        const data = this.generateLockfile();
        const target = path.resolve(filename);
        const temporary = `${target}.${process.pid}.tmp`;

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(data, null, 2),
                { encoding: "utf8", flag: "wx", mode: 0o600 }
            );

            await fs.rename(temporary, target);
        } catch (error) {
            await fs.rm(temporary, { force: true }).catch(() => {});
            throw error;
        }
    }
}

async function main() {
    const repository = new Repository("enterprise-platform");

    repository.on("pull-request:merged", pr => {
        console.log(`EVENT: PR #${pr.id} merged`);
    });

    repository.on("review:submitted", event => {
        console.log(
            `EVENT: ${event.reviewer} submitted ${event.state}`
        );
    });

    repository.addDependency(new Dependency({
        name: "httpx",
        version: "0.27.0",
        minimum: "0.25.0",
        license: "BSD-3-Clause"
    }));

    repository.addDependency(new Dependency({
        name: "pydantic",
        version: "2.8.2",
        minimum: "2.5.0",
        license: "MIT"
    }));

    repository.addDependency(new Dependency({
        name: "fastapi",
        version: "0.112.0",
        minimum: "0.100.0",
        dependencies: ["httpx", "pydantic"]
    }));

    repository.addDependency(new Dependency({
        name: "cryptography",
        version: "43.0.0",
        minimum: "42.0.0",
        license: "Apache-2.0"
    }));

    console.log("\nDEPENDENCY INSTALLATION ORDER");
    console.log(repository.validateGraph().join(" -> "));

    console.log("\nPOLICY AUDIT");
    console.log(repository.audit());

    const updates = repository.planUpdates({
        httpx: "0.28.1",
        pydantic: "2.9.2",
        fastapi: "0.115.0"
    });

    const pr = repository.createPullRequest({
        source: "dependency/quarterly-update",
        target: "main",
        changes: updates
    });

    pr.checks.set("unit-tests", CheckState.PENDING);
    pr.checks.set("security-scan", CheckState.PENDING);
    pr.checks.set("license-audit", CheckState.PENDING);

    pr.conversations.set("compatibility-analysis", true);
    pr.conversations.set("migration-review", true);

    await repository.runChecks(pr, {
        "unit-tests": async () => true,
        "security-scan": async () => true,
        "license-audit": async () => true
    });

    repository.addReview(pr, "security-reviewer", ReviewState.APPROVED);
    repository.addReview(pr, "platform-reviewer", ReviewState.APPROVED);

    const eligibility = repository.evaluateMerge(pr);

    console.log("\nMERGE ELIGIBILITY");
    console.log(eligibility);

    if (eligibility.eligible) {
        repository.merge(pr, "squash");
    }

    const lockfile = repository.generateLockfile();
    console.log("\nLOCKFILE INTEGRITY");
    console.log(lockfile.integrity);

    console.log("\nEXECUTION COMPLETED");
}

main().catch(error => {
    console.error(`FATAL: ${error.message}`);
    process.exitCode = 1;
});
