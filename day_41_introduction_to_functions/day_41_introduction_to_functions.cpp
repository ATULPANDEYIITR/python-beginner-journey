#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Repository governance case study.
 *
 * Scenario: a payment-platform team evaluates changes to a protected main
 * branch. A merge is permitted only when review policy, required checks,
 * branch restrictions, and change freshness are all satisfied.
 *
 * Compile: g++ -std=c++17 -Wall -Wextra -pedantic repository_functions.cpp -o repository_functions
 */

enum class RequestState {
    Draft,
    Open,
    Closed,
    Merged
};

enum class ReviewDecision {
    Approved,
    ChangesRequested,
    Commented
};

enum class CheckState {
    Pending,
    Success,
    Failure
};

std::string toString(RequestState state) {
    switch (state) {
        case RequestState::Draft: return "draft";
        case RequestState::Open: return "open";
        case RequestState::Closed: return "closed";
        case RequestState::Merged: return "merged";
    }
    throw std::logic_error("Unknown request state");
}

std::string toString(CheckState state) {
    switch (state) {
        case CheckState::Pending: return "pending";
        case CheckState::Success: return "success";
        case CheckState::Failure: return "failure";
    }
    throw std::logic_error("Unknown check state");
}

struct Commit {
    std::string sha;
    std::string message;
};

struct Review {
    std::string reviewer;
    ReviewDecision decision;
    std::string commitSha;
    bool dismissed = false;
};

struct GovernancePolicy {
    std::size_t requiredApprovals = 2;
    std::set<std::string> requiredChecks{"unit-tests", "security-scan"};
    std::set<std::string> eligibleReviewers{"alex", "priya", "sam"};
    bool requireLinearHistory = true;
    bool prohibitForcePush = true;
    bool prohibitBranchDeletion = true;
    bool prohibitDirectPush = true;
    bool requireResolvedConversations = true;
    bool administratorMayBypass = false;
};

struct PullRequest {
    int id;
    std::string author;
    std::string sourceBranch;
    std::string targetBranch;
    RequestState state = RequestState::Draft;
    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::map<std::string, CheckState> checks;
    std::size_t unresolvedConversations = 0;
    bool baseSynchronized = false;
    bool linearHistoryAvailable = true;
    bool conflictsPresent = false;
};

struct Eligibility {
    bool allowed = false;
    std::vector<std::string> reasons;
};

class RepositoryGovernance {
private:
    GovernancePolicy policy_;

    static bool validIdentifier(const std::string& value) {
        return !value.empty()
            && std::all_of(value.begin(), value.end(), [](unsigned char ch) {
                return std::isalnum(ch) || ch == '-' || ch == '_' || ch == '/';
            });
    }

public:
    explicit RepositoryGovernance(GovernancePolicy policy)
        : policy_(std::move(policy)) {
        if (policy_.requiredApprovals == 0) {
            throw std::invalid_argument("At least one approval is required");
        }
        if (policy_.eligibleReviewers.empty()) {
            throw std::invalid_argument("Eligible reviewer set cannot be empty");
        }
    }

    void openRequest(PullRequest& request) const {
        if (request.state != RequestState::Draft
            && request.state != RequestState::Closed) {
            throw std::logic_error("Only a draft or closed request can be opened");
        }
        if (request.sourceBranch == request.targetBranch
            || !validIdentifier(request.sourceBranch)
            || !validIdentifier(request.targetBranch)) {
            throw std::invalid_argument("Invalid source or target branch");
        }
        if (request.commits.empty()) {
            throw std::logic_error("A request needs at least one commit");
        }
        request.state = RequestState::Open;
    }

    void addCommit(PullRequest& request, Commit commit) const {
        if (request.state == RequestState::Merged
            || request.state == RequestState::Closed) {
            throw std::logic_error("Cannot update a closed or merged request");
        }
        if (commit.sha.size() < 7 || commit.message.empty()) {
            throw std::invalid_argument("Commit identifier or message is invalid");
        }
        if (!std::all_of(commit.sha.begin(), commit.sha.end(), [](unsigned char ch) {
                return std::isxdigit(ch);
            })) {
            throw std::invalid_argument("Commit identifier must be hexadecimal");
        }

        request.commits.push_back(std::move(commit));

        // A new head commit makes approvals tied to the previous head stale.
        // The reviewer can re-review the new changeset instead of silently
        // inheriting approval for code that has not been inspected.
    }

    void submitReview(
        PullRequest& request,
        const std::string& reviewer,
        ReviewDecision decision
    ) const {
        if (request.state != RequestState::Open) {
            throw std::logic_error("Review requires an open request");
        }
        if (reviewer.empty() || reviewer == request.author) {
            throw std::invalid_argument("Author cannot approve their own request");
        }
        if (policy_.eligibleReviewers.count(reviewer) == 0) {
            throw std::invalid_argument("Reviewer is not eligible under policy");
        }
        if (request.commits.empty()) {
            throw std::logic_error("Cannot review an empty changeset");
        }

        request.reviews.push_back(
            Review{reviewer, decision, request.commits.back().sha, false}
        );
    }

    void dismissReview(
        PullRequest& request,
        const std::string& reviewer
    ) const {
        // Dismissal is an explicit policy action. It does not delete the audit
        // record, which remains useful when investigating merge decisions.
        for (auto it = request.reviews.rbegin(); it != request.reviews.rend(); ++it) {
            if (it->reviewer == reviewer && !it->dismissed) {
                it->dismissed = true;
                return;
            }
        }
        throw std::invalid_argument("No active review exists for that reviewer");
    }

    void updateCheck(
        PullRequest& request,
        const std::string& name,
        CheckState state
    ) const {
        if (name.empty()) {
            throw std::invalid_argument("Check name cannot be empty");
        }
        request.checks[name] = state;
    }

    Eligibility evaluate(const PullRequest& request) const {
        Eligibility result;

        if (request.state != RequestState::Open) {
            result.reasons.push_back("Request is not open");
        }
        if (request.commits.empty()) {
            result.reasons.push_back("No commits are available to merge");
        }
        if (request.conflictsPresent) {
            result.reasons.push_back("Source branch has merge conflicts");
        }
        if (!request.baseSynchronized) {
            result.reasons.push_back("Source branch is not synchronized with base");
        }
        if (policy_.requireLinearHistory && !request.linearHistoryAvailable) {
            result.reasons.push_back("Required linear history cannot be produced");
        }
        if (policy_.requireResolvedConversations
            && request.unresolvedConversations != 0) {
            result.reasons.push_back("Review conversations remain unresolved");
        }

        std::map<std::string, Review> latestReview;
        for (const Review& review : request.reviews) {
            if (!review.dismissed) {
                latestReview[review.reviewer] = review;
            }
        }

        std::size_t approvals = 0;
        bool blockingChangesRequest = false;
        const std::string head = request.commits.empty()
            ? ""
            : request.commits.back().sha;

        for (const auto& entry : latestReview) {
            const Review& review = entry.second;

            // Approval only applies to the current head commit. New commits
            // invalidate older approvals for this simplified policy model.
            if (review.commitSha != head) {
                continue;
            }
            if (review.decision == ReviewDecision::Approved
                && review.reviewer != request.author
                && policy_.eligibleReviewers.count(review.reviewer) > 0) {
                ++approvals;
            }
            if (review.decision == ReviewDecision::ChangesRequested) {
                blockingChangesRequest = true;
            }
        }

        if (approvals < policy_.requiredApprovals) {
            result.reasons.push_back(
                "Insufficient current approvals: " + std::to_string(approvals)
                + "/" + std::to_string(policy_.requiredApprovals)
            );
        }
        if (blockingChangesRequest) {
            result.reasons.push_back("A current review requests changes");
        }

        for (const std::string& required : policy_.requiredChecks) {
            const auto found = request.checks.find(required);
            if (found == request.checks.end()
                || found->second != CheckState::Success) {
                result.reasons.push_back(
                    "Required check is not successful: " + required
                );
            }
        }

        result.allowed = result.reasons.empty();
        return result;
    }

    void merge(PullRequest& request) const {
        const Eligibility decision = evaluate(request);
        if (!decision.allowed) {
            throw std::logic_error("Merge rejected by repository governance");
        }
        request.state = RequestState::Merged;
    }

    void printEvaluation(const PullRequest& request) const {
        const Eligibility decision = evaluate(request);
        std::cout << "Pull Request #" << request.id
                  << " (" << request.sourceBranch
                  << " -> " << request.targetBranch << ")\n";
        std::cout << "State: " << toString(request.state) << '\n';
        std::cout << "Merge eligible: "
                  << (decision.allowed ? "yes" : "no") << '\n';

        for (const std::string& reason : decision.reasons) {
            std::cout << "  Blocker: " << reason << '\n';
        }
    }
};

int main() {
    try {
        GovernancePolicy policy;
        RepositoryGovernance governance(policy);

        PullRequest request{
            105,
            "developer",
            "feature/payment-validation",
            "main"
        };

        governance.addCommit(
            request,
            Commit{"a1b2c3d", "Reject invalid payment amounts"}
        );
        governance.openRequest(request);

        governance.submitReview(request, "alex", ReviewDecision::Approved);
        governance.submitReview(request, "priya", ReviewDecision::Approved);
        governance.updateCheck(request, "unit-tests", CheckState::Success);
        governance.updateCheck(request, "security-scan", CheckState::Pending);

        request.baseSynchronized = true;
        request.linearHistoryAvailable = true;
        request.unresolvedConversations = 1;

        std::cout << "Initial governance evaluation\n";
        governance.printEvaluation(request);

        std::cout << "\nUpdating failed merge conditions\n";
        governance.updateCheck(request, "security-scan", CheckState::Success);
        request.unresolvedConversations = 0;

        std::cout << "Final governance evaluation\n";
        governance.printEvaluation(request);

        governance.merge(request);
        std::cout << "Final state: " << toString(request.state) << '\n';

        std::cout << "\nTesting stale approval behavior\n";
        PullRequest stale{
            106,
            "developer",
            "feature/audit-logging",
            "main"
        };
        governance.addCommit(stale, Commit{"111aaaa", "Add audit events"});
        governance.openRequest(stale);
        governance.submitReview(stale, "alex", ReviewDecision::Approved);
        governance.submitReview(stale, "priya", ReviewDecision::Approved);

        governance.addCommit(stale, Commit{"222bbbb", "Fix audit event ordering"});
        stale.baseSynchronized = true;
        governance.updateCheck(stale, "unit-tests", CheckState::Success);
        governance.updateCheck(stale, "security-scan", CheckState::Success);
        governance.printEvaluation(stale);

        std::cout << "\nTesting direct state manipulation safeguards\n";
        try {
            PullRequest invalid{
                107,
                "developer",
                "feature/example",
                "main"
            };
            governance.openRequest(invalid);
        } catch (const std::exception& error) {
            std::cout << "Rejected invalid request: " << error.what() << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Governance engine error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
