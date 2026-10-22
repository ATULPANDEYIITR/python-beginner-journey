"use strict";

/*
 * Functions inside functions are used here to build a small,
 * event-driven repository governance engine.
 *
 * The outer factory creates repository-specific state.
 * Nested functions retain access to that state through closures.
 */

class PullRequest {
    constructor({
        number,
        title,
        sourceBranch,
        targetBranch,
        commits = [],
        reviewers = [],
        reviews = [],
        statusChecks = {},
        unresolvedConversations = 0,
        draft = false,
    }) {
        if (!Number.isInteger(number) || number <= 0) {
            throw new Error("Pull Request number must be a positive integer");
        }

        if (!title.trim()) {
            throw new Error("Pull Request title cannot be empty");
        }

        if (!sourceBranch || !targetBranch) {
            throw new Error("Source and target branches are required");
        }

        this.number = number;
        this.title = title;
        this.sourceBranch = sourceBranch;
        this.targetBranch = targetBranch;
        this.commits = [...commits];
        this.reviewers = new Set(reviewers);
        this.reviews = [...reviews];
        this.statusChecks = { ...statusChecks };
        this.unresolvedConversations = unresolvedConversations;
        this.draft = draft;
        this.state = draft ? "draft" : "open";
    }
}


class GovernanceEngine {
    constructor(repositoryName, protection) {
        this.repositoryName = repositoryName;
        this.protection = Object.freeze({ ...protection });
        this.listeners = new Map();
        this.auditEvents = [];

        this.on("merged", (event) => {
            this.auditEvents.push(
                `PR #${event.number} merged into ${event.targetBranch}`
            );
        });

        this.on("rejected", (event) => {
            this.auditEvents.push(
                `PR #${event.number} rejected: ${event.failures.join("; ")}`
            );
        });
    }

    on(eventName, handler) {
        if (typeof handler !== "function") {
            throw new TypeError("Event handler must be a function");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(handler);
    }

    emit(eventName, payload) {
        const handlers = this.listeners.get(eventName) ?? [];

        for (const handler of handlers) {
            handler(payload);
        }
    }

    createPolicyEvaluator() {
        const policy = this.protection;
        const repository = this.repositoryName;

        /*
         * This nested function closes over policy and repository.
         * It becomes a reusable evaluator specialized for this repository.
         */
        return (pullRequest) => {
            const failures = [];

            if (pullRequest.targetBranch !== policy.protectedBranch) {
                failures.push(
                    `target branch must be ${policy.protectedBranch}`
                );
            }

            if (pullRequest.state !== "open") {
                failures.push("Pull Request must be open");
            }

            if (pullRequest.draft) {
                failures.push("draft Pull Requests cannot be merged");
            }

            if (
                !policy.allowDirectPush &&
                pullRequest.sourceBranch === policy.protectedBranch
            ) {
                failures.push("direct changes to protected branch are prohibited");
            }

            for (const requiredCheck of policy.requiredChecks) {
                if (pullRequest.statusChecks[requiredCheck] !== "passed") {
                    failures.push(`status check '${requiredCheck}' is not passing`);
                }
            }

            if (
                policy.requireConversationResolution &&
                pullRequest.unresolvedConversations > 0
            ) {
                failures.push("unresolved review conversations remain");
            }

            const countApprovals = () => {
                const latestCommit =
                    pullRequest.commits[pullRequest.commits.length - 1];

                if (!latestCommit) {
                    return 0;
                }

                const approved = new Set();

                for (const review of pullRequest.reviews) {
                    if (
                        review.state === "approved" &&
                        review.commitSha === latestCommit.sha &&
                        pullRequest.reviewers.has(review.reviewer) &&
                        !review.dismissed
                    ) {
                        approved.add(review.reviewer);
                    }
                }

                return approved.size;
            };

            const approvals = countApprovals();

            if (approvals < policy.requiredApprovals) {
                failures.push(
                    `requires ${policy.requiredApprovals} valid approval(s), found ${approvals}`
                );
            }

            if (policy.requireLinearHistory) {
                const seen = new Set();

                for (const commit of pullRequest.commits) {
                    if (seen.has(commit.sha)) {
                        failures.push("duplicate commit detected");
                        break;
                    }

                    seen.add(commit.sha);
                }
            }

            if (repository.length === 0) {
                failures.push("repository name cannot be empty");
            }

            return failures;
        };
    }

    evaluate(pullRequest) {
        const evaluator = this.createPolicyEvaluator();
        return evaluator(pullRequest);
    }

    merge(pullRequest) {
        const failures = this.evaluate(pullRequest);

        if (failures.length > 0) {
            this.emit("rejected", {
                number: pullRequest.number,
                failures,
            });

            return {
                merged: false,
                failures,
            };
        }

        pullRequest.state = "merged";

        this.emit("merged", {
            number: pullRequest.number,
            targetBranch: pullRequest.targetBranch,
        });

        return {
            merged: true,
            failures: [],
        };
    }
}


function createReview(reviewer, state, commitSha, dismissed = false) {
    if (!reviewer || !commitSha) {
        throw new Error("Reviewer and commit SHA are required");
    }

    return {
        reviewer,
        state,
        commitSha,
        dismissed,
    };
}


function demonstrateNestedFunctions() {
    const engine = new GovernanceEngine("secure-api", {
        protectedBranch: "main",
        requiredApprovals: 2,
        requiredChecks: ["tests", "security-scan"],
        requireConversationResolution: true,
        requireLinearHistory: true,
        allowDirectPush: false,
    });

    const pr = new PullRequest({
        number: 100,
        title: "Strengthen authentication checks",
        sourceBranch: "feature/auth",
        targetBranch: "main",
        commits: [
            { sha: "a10", message: "authentication policy" },
            { sha: "b20", message: "validation tests" },
        ],
        reviewers: ["alice", "bob", "carol"],
        reviews: [
            createReview("alice", "approved", "b20"),
            createReview("bob", "approved", "b20"),
        ],
        statusChecks: {
            tests: "passed",
            "security-scan": "passed",
        },
    });

    console.log("First evaluation:");
    console.log(engine.evaluate(pr));
    console.log("Merge result:", engine.merge(pr));

    const staleApprovalPR = new PullRequest({
        number: 101,
        title: "Update deployment policy",
        sourceBranch: "feature/deployment",
        targetBranch: "main",
        commits: [
            { sha: "c10", message: "initial policy" },
            { sha: "d20", message: "address reviewer feedback" },
        ],
        reviewers: ["alice", "bob"],
        reviews: [
            createReview("alice", "approved", "c10"),
            createReview("bob", "approved", "c10"),
        ],
        statusChecks: {
            tests: "passed",
            "security-scan": "passed",
        },
    });

    console.log("\nStale approval evaluation:");
    console.log(engine.evaluate(staleApprovalPR));
    console.log("Merge result:", engine.merge(staleApprovalPR));

    staleApprovalPR.reviews.push(
        createReview("alice", "approved", "d20"),
        createReview("bob", "approved", "d20")
    );

    console.log("\nAfter fresh approvals:");
    console.log(engine.evaluate(staleApprovalPR));
    console.log("Merge result:", engine.merge(staleApprovalPR));

    console.log("\nAudit events:");
    for (const event of engine.auditEvents) {
        console.log("-", event);
    }
}


try {
    demonstrateNestedFunctions();
} catch (error) {
    console.error("Governance engine failure:", error.message);
    process.exitCode = 1;
}
