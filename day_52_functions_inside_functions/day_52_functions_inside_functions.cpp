#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

enum class PRState {
    Draft,
    Open,
    Closed,
    Merged
};

enum class ReviewState {
    Commented,
    ChangesRequested,
    Approved,
    Dismissed
};

struct Commit {
    std::string sha;
    std::string message;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
};

struct PullRequest {
    int number;
    std::string title;
    std::string sourceBranch;
    std::string targetBranch;
    PRState state;
    std::vector<Commit> commits;
    std::set<std::string> eligibleReviewers;
    std::vector<Review> reviews;
    std::map<std::string, bool> statusChecks;
    int unresolvedConversations;
};

struct BranchProtection {
    std::string protectedBranch;
    int requiredApprovals;
    std::set<std::string> requiredChecks;
    bool requireConversationResolution;
    bool requireLinearHistory;
    bool allowDirectPush;
    bool allowForcePush;
};

class MergeEligibilityEngine {
private:
    BranchProtection protection;

    /*
     * This nested lambda is intentionally returned from the factory.
     * It captures the branch policy by value and behaves as a policy
     * function specialized for one protected branch.
     */
    auto createApprovalCounter() const {
        const BranchProtection policy = protection;

        return [policy](const PullRequest& pr) {
            std::set<std::string> approvedReviewers;

            if (pr.commits.empty()) {
                return approvedReviewers;
            }

            const std::string& latestSha = pr.commits.back().sha;

            for (const Review& review : pr.reviews) {
                if (review.state == ReviewState::Approved &&
                    review.commitSha == latestSha &&
                    pr.eligibleReviewers.count(review.reviewer) > 0) {
                    approvedReviewers.insert(review.reviewer);
                }
            }

            return approvedReviewers;
        };
    }

    bool hasLinearHistory(const PullRequest& pr) const {
        std::set<std::string> seen;

        for (const auto& commit : pr.commits) {
            if (!seen.insert(commit.sha).second) {
                return false;
            }
        }

        return true;
    }

public:
    explicit MergeEligibilityEngine(BranchProtection branchProtection)
        : protection(std::move(branchProtection)) {}

    std::vector<std::string> evaluate(const PullRequest& pr) const {
        std::vector<std::string> failures;

        if (pr.targetBranch != protection.protectedBranch) {
            failures.push_back("incorrect protected target branch");
        }

        if (pr.state != PRState::Open) {
            failures.push_back("Pull Request is not open");
        }

        if (pr.sourceBranch == protection.protectedBranch &&
            !protection.allowDirectPush) {
            failures.push_back("direct modification of protected branch is prohibited");
        }

        if (pr.commits.empty()) {
            failures.push_back("Pull Request contains no commits");
        }

        for (const std::string& check : protection.requiredChecks) {
            auto it = pr.statusChecks.find(check);

            if (it == pr.statusChecks.end() || !it->second) {
                failures.push_back("required status check failed: " + check);
            }
        }

        if (protection.requireConversationResolution &&
            pr.unresolvedConversations > 0) {
            failures.push_back("unresolved review conversations remain");
        }

        auto countApprovals = createApprovalCounter();
        const auto approvals = countApprovals(pr);

        if (static_cast<int>(approvals.size()) <
            protection.requiredApprovals) {
            failures.push_back(
                "insufficient current-commit approvals"
            );
        }

        if (protection.requireLinearHistory &&
            !hasLinearHistory(pr)) {
            failures.push_back("linear-history requirement failed");
        }

        return failures;
    }

    bool merge(PullRequest& pr) const {
        const auto failures = evaluate(pr);

        if (!failures.empty()) {
            std::cout << "PR #" << pr.number << " rejected\n";

            for (const auto& failure : failures) {
                std::cout << "  - " << failure << '\n';
            }

            return false;
        }

        pr.state = PRState::Merged;
        std::cout << "PR #" << pr.number << " merged into "
                  << pr.targetBranch << '\n';

        return true;
    }
};

int main() {
    BranchProtection policy{
        "main",
        2,
        {"tests", "security-scan"},
        true,
        true,
        false,
        false
    };

    MergeEligibilityEngine engine(policy);

    PullRequest pr{
        501,
        "Strengthen authorization workflow",
        "feature/authorization",
        "main",
        PRState::Open,
        {
            {"a100", "authorization policy"},
            {"b200", "security tests"}
        },
        {"alice", "bob", "carol"},
        {
            {"alice", ReviewState::Approved, "b200"},
            {"bob", ReviewState::Approved, "b200"}
        },
        {
            {"tests", true},
            {"security-scan", true}
        },
        0
    };

    engine.merge(pr);

    PullRequest stalePr{
        502,
        "Update deployment controls",
        "feature/deployment",
        "main",
        PRState::Open,
        {
            {"c100", "initial implementation"},
            {"d200", "address review comments"}
        },
        {"alice", "bob"},
        {
            {"alice", ReviewState::Approved, "c100"},
            {"bob", ReviewState::Approved, "c100"}
        },
        {
            {"tests", true},
            {"security-scan", true}
        },
        0
    };

    std::cout << "\nTesting stale approvals:\n";
    engine.merge(stalePr);

    stalePr.reviews.push_back(
        {"alice", ReviewState::Approved, "d200"}
    );
    stalePr.reviews.push_back(
        {"bob", ReviewState::Approved, "d200"}
    );

    std::cout << "\nTesting fresh approvals:\n";
    engine.merge(stalePr);

    PullRequest conflictPr{
        503,
        "Update protected branch directly",
        "main",
        "main",
        PRState::Open,
        {
            {"e100", "unsafe direct change"}
        },
        {"alice", "bob"},
        {},
        {
            {"tests", true},
            {"security-scan", true}
        },
        0
    };

    std::cout << "\nTesting direct-push restriction:\n";
    engine.merge(conflictPr);

    return 0;
}
