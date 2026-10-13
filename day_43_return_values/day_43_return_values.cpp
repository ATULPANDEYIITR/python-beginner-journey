#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Repository governance engine.
 *
 * Case study: an engineering organization needs a deterministic service
 * that decides whether a Pull Request may merge into a protected branch.
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic repository_governance.cpp -o governance
 *
 * The engine models:
 * - Pull Request lifecycle and commit synchronization
 * - Review decisions tied to a specific commit
 * - Approval eligibility and reviewer separation
 * - Required CI checks and unresolved discussions
 * - Protected-branch rules and merge eligibility
 *
 * This is an educational in-memory policy engine, not a Git hosting server.
 */

enum class PullRequestState {
    Open,
    Closed,
    Merged
};

enum class ReviewState {
    Approved,
    ChangesRequested,
    Commented
};

enum class CheckState {
    Pending,
    Success,
    Failure
};

enum class MergeStrategy {
    MergeCommit,
    Squash,
    Rebase
};

std::string toString(PullRequestState state) {
    switch (state) {
        case PullRequestState::Open: return "open";
        case PullRequestState::Closed: return "closed";
        case PullRequestState::Merged: return "merged";
    }
    throw std::logic_error("Unknown Pull Request state.");
}

std::string toString(ReviewState state) {
    switch (state) {
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes requested";
        case ReviewState::Commented: return "commented";
    }
    throw std::logic_error("Unknown review state.");
}

std::string toString(CheckState state) {
    switch (state) {
        case CheckState::Pending: return "pending";
        case CheckState::Success: return "success";
        case CheckState::Failure: return "failure";
    }
    throw std::logic_error("Unknown check state.");
}

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
    std::string body;
    bool eligibleReviewer;
};

struct ReviewComment {
    std::string reviewer;
    std::string filePath;
    unsigned int line;
    std::string body;
    bool resolved;
};

struct BranchProtection {
    std::string branchName;
    unsigned int requiredApprovals = 2;
    std::set<std::string> requiredChecks;
    bool requireResolvedConversations = true;
    bool requireLinearHistory = true;
    bool prohibitDirectPushes = true;
    bool prohibitForcePushes = true;
    bool prohibitDeletion = true;
    bool allowAdministratorBypass = false;
    std::set<std::string> permittedMergeStrategies;
};

struct PullRequest {
    std::string id;
    std::string title;
    std::string author;
    std::string sourceBranch;
    std::string targetBranch;
    std::string headSha;
    PullRequestState state = PullRequestState::Open;
    bool draft = false;
    bool sourceBranchDeleted = false;
    std::vector<Review> reviews;
    std::vector<ReviewComment> comments;
    std::map<std::string, CheckState> checks;
};

struct Eligibility {
    bool eligible = false;
    unsigned int approvalCount = 0;
    std::vector<std::string> blockers;
};

class RepositoryGovernance {
private:
    std::map<std::string, BranchProtection> protections_;
    std::map<std::string, PullRequest> pullRequests_;

    static bool validSha(const std::string& sha) {
        if (sha.size() < 7 || sha.size() > 40) {
            return false;
        }

        return std::all_of(sha.begin(), sha.end(), [](unsigned char c) {
            return std::isxdigit(c) != 0;
        });
    }

    static bool validBranchName(const std::string& branch) {
        return !branch.empty() &&
               branch.find(' ') == std::string::npos &&
               branch.find("..") == std::string::npos &&
               branch.front() != '/' &&
               branch.back() != '/';
    }

    const BranchProtection& protectionFor(const PullRequest& pr) const {
        auto iterator = protections_.find(pr.targetBranch);
        if (iterator == protections_.end()) {
            throw std::runtime_error(
                "No branch protection policy exists for " + pr.targetBranch
            );
        }
        return iterator->second;
    }

public:
    void protectBranch(const BranchProtection& protection) {
        if (!validBranchName(protection.branchName)) {
            throw std::invalid_argument("Invalid protected branch name.");
        }
        if (protection.requiredApprovals > 20) {
            throw std::invalid_argument("Approval requirement exceeds policy limit.");
        }
        if (protection.permittedMergeStrategies.empty()) {
            throw std::invalid_argument("At least one merge strategy is required.");
        }

        protections_[protection.branchName] = protection;
    }

    void openPullRequest(const PullRequest& pr) {
        if (pr.id.empty() || pr.title.empty() || pr.author.empty()) {
            throw std::invalid_argument("Pull Request identity fields are required.");
        }
        if (!validBranchName(pr.sourceBranch) ||
            !validBranchName(pr.targetBranch)) {
            throw std::invalid_argument("Invalid source or target branch.");
        }
        if (pr.sourceBranch == pr.targetBranch) {
            throw std::invalid_argument("Source and target must differ.");
        }
        if (!validSha(pr.headSha)) {
            throw std::invalid_argument("Invalid Pull Request head commit.");
        }
        if (pullRequests_.count(pr.id) != 0) {
            throw std::invalid_argument("Pull Request ID already exists.");
        }
        if (protections_.count(pr.targetBranch) == 0) {
            throw std::invalid_argument("Target branch has no protection policy.");
        }
        if (pr.state != PullRequestState::Open) {
            throw std::invalid_argument("New Pull Requests must be open.");
        }

        pullRequests_.emplace(pr.id, pr);
    }

    PullRequest& getPullRequest(const std::string& id) {
        auto iterator = pullRequests_.find(id);
        if (iterator == pullRequests_.end()) {
            throw std::out_of_range("Pull Request not found: " + id);
        }
        return iterator->second;
    }

    const PullRequest& getPullRequest(const std::string& id) const {
        auto iterator = pullRequests_.find(id);
        if (iterator == pullRequests_.end()) {
            throw std::out_of_range("Pull Request not found: " + id);
        }
        return iterator->second;
    }

    void markReady(const std::string& id) {
        PullRequest& pr = getPullRequest(id);
        if (pr.state != PullRequestState::Open || !pr.draft) {
            throw std::logic_error("Only an open draft can become ready.");
        }
        pr.draft = false;
    }

    void submitReview(
        const std::string& id,
        const std::string& reviewer,
        ReviewState state,
        const std::string& body,
        bool eligibleReviewer
    ) {
        PullRequest& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error("Reviews require an open Pull Request.");
        }
        if (reviewer.empty() || reviewer == pr.author || !eligibleReviewer) {
            throw std::invalid_argument("Reviewer is not eligible to review.");
        }

        // A reviewer has one effective current decision in this model.
        // A later review replaces that reviewer's previous decision.
        pr.reviews.erase(
            std::remove_if(
                pr.reviews.begin(),
                pr.reviews.end(),
                [&](const Review& review) {
                    return review.reviewer == reviewer;
                }
            ),
            pr.reviews.end()
        );

        pr.reviews.push_back(
            Review{reviewer, state, pr.headSha, body, eligibleReviewer}
        );
    }

    void addComment(
        const std::string& id,
        const std::string& reviewer,
        const std::string& filePath,
        unsigned int line,
        const std::string& body
    ) {
        PullRequest& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error("Cannot comment on a closed Pull Request.");
        }
        if (reviewer.empty() || filePath.empty() || line == 0 || body.empty()) {
            throw std::invalid_argument("Inline comment fields are required.");
        }

        pr.comments.push_back(
            ReviewComment{reviewer, filePath, line, body, false}
        );
    }

    void resolveComment(const std::string& id, std::size_t index) {
        PullRequest& pr = getPullRequest(id);
        if (index >= pr.comments.size()) {
            throw std::out_of_range("Comment index is out of range.");
        }
        pr.comments[index].resolved = true;
    }

    void setCheck(
        const std::string& id,
        const std::string& checkName,
        CheckState state
    ) {
        PullRequest& pr = getPullRequest(id);
        if (pr.state != PullRequestState::Open) {
            throw std::logic_error("Checks cannot be updated on a closed PR.");
        }
        if (checkName.empty()) {
            throw std::invalid_argument("Check name is required.");
        }
        pr.checks[checkName] = state;
    }

    void synchronize(const std::string& id, const std::string& newHeadSha) {
        PullRequest& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error("Only an open Pull Request can synchronize.");
        }
        if (!validSha(newHeadSha)) {
            throw std::invalid_argument("New head SHA is invalid.");
        }

        pr.headSha = newHeadSha;

        // This simplified model treats checks as head-specific and discards
        // old results. Real hosting systems track exact commit identities.
        pr.checks.clear();

        // Reviews tied to the old head cannot satisfy the current policy.
        // Keeping their history would be appropriate in a persistent audit log.
    }

    Eligibility evaluate(const std::string& id) const {
        const PullRequest& pr = getPullRequest(id);
        const BranchProtection& policy = protectionFor(pr);
        Eligibility result;

        if (pr.state != PullRequestState::Open) {
            result.blockers.push_back("Pull Request is not open.");
            return result;
        }

        if (pr.draft) {
            result.blockers.push_back("Pull Request is still a draft.");
        }

        std::unordered_map<std::string, ReviewState> latestDecisions;

        for (const Review& review : pr.reviews) {
            if (review.commitSha != pr.headSha) {
                continue;
            }
            if (!review.eligibleReviewer || review.reviewer == pr.author) {
                continue;
            }
            latestDecisions[review.reviewer] = review.state;
        }

        bool changesRequested = false;
        for (const auto& entry : latestDecisions) {
            if (entry.second == ReviewState::Approved) {
                ++result.approvalCount;
            } else if (entry.second == ReviewState::ChangesRequested) {
                changesRequested = true;
            }
        }

        if (changesRequested) {
            result.blockers.push_back("A current review requests changes.");
        }

        if (result.approvalCount < policy.requiredApprovals) {
            result.blockers.push_back(
                "Insufficient approvals: required " +
                std::to_string(policy.requiredApprovals) +
                ", found " + std::to_string(result.approvalCount) + "."
            );
        }

        for (const std::string& required : policy.requiredChecks) {
            auto check = pr.checks.find(required);
            if (check == pr.checks.end() || check->second != CheckState::Success) {
                result.blockers.push_back("Required check not successful: " + required);
            }
        }

        if (policy.requireResolvedConversations) {
            const bool unresolved = std::any_of(
                pr.comments.begin(),
                pr.comments.end(),
                [](const ReviewComment& comment) {
                    return !comment.resolved;
                }
            );
            if (unresolved) {
                result.blockers.push_back("Review conversations remain unresolved.");
            }
        }

        result.eligible = result.blockers.empty();
        return result;
    }

    void merge(
        const std::string& id,
        MergeStrategy strategy,
        bool administrator = false
    ) {
        PullRequest& pr = getPullRequest(id);
        const BranchProtection& policy = protectionFor(pr);

        if (policy.permittedMergeStrategies.count(
                strategy == MergeStrategy::MergeCommit ? "merge" :
                strategy == MergeStrategy::Squash ? "squash" : "rebase"
            ) == 0) {
            throw std::logic_error("Selected merge strategy is prohibited.");
        }

        if (administrator && !policy.allowAdministratorBypass) {
            throw std::logic_error("Administrator bypass is disabled.");
        }

        Eligibility eligibility = evaluate(id);
        if (!eligibility.eligible) {
            std::string message = "Merge blocked:";
            for (const std::string& blocker : eligibility.blockers) {
                message += "\n - " + blocker;
            }
            throw std::logic_error(message);
        }

        pr.state = PullRequestState::Merged;
        std::cout << "Merged " << pr.id << " using "
                  << (strategy == MergeStrategy::MergeCommit ? "merge commit" :
                      strategy == MergeStrategy::Squash ? "squash" : "rebase")
                  << ".\n";
    }

    void directPush(const std::string& branch, bool force) const {
        auto iterator = protections_.find(branch);
        if (iterator == protections_.end()) {
            throw std::runtime_error("Branch is not registered as protected.");
        }

        const BranchProtection& policy = iterator->second;
        if (policy.prohibitDirectPushes) {
            throw std::logic_error("Direct pushes to protected branch are prohibited.");
        }
        if (force && policy.prohibitForcePushes) {
            throw std::logic_error("Force pushes to protected branch are prohibited.");
        }
    }

    void deleteBranch(const std::string& branch) const {
        auto iterator = protections_.find(branch);
        if (iterator != protections_.end() && iterator->second.prohibitDeletion) {
            throw std::logic_error("Protected branch deletion is prohibited.");
        }
    }
};

void printEligibility(
    const std::string& id,
    const Eligibility& eligibility
) {
    std::cout << id << ": "
              << (eligibility.eligible ? "eligible" : "blocked")
              << ", approvals=" << eligibility.approvalCount << "\n";

    for (const std::string& blocker : eligibility.blockers) {
        std::cout << "  - " << blocker << "\n";
    }
}

int main() {
    try {
        RepositoryGovernance governance;

        BranchProtection mainPolicy;
        mainPolicy.branchName = "main";
        mainPolicy.requiredApprovals = 2;
        mainPolicy.requiredChecks = {"unit-tests", "security-scan"};
        mainPolicy.requireResolvedConversations = true;
        mainPolicy.requireLinearHistory = true;
        mainPolicy.prohibitDirectPushes = true;
        mainPolicy.prohibitForcePushes = true;
        mainPolicy.prohibitDeletion = true;
        mainPolicy.allowAdministratorBypass = false;
        mainPolicy.permittedMergeStrategies = {"squash", "rebase"};

        governance.protectBranch(mainPolicy);

        PullRequest pr;
        pr.id = "PR-418";
        pr.title = "Add signed release manifest";
        pr.author = "engineer-alex";
        pr.sourceBranch = "feature/signed-manifest";
        pr.targetBranch = "main";
        pr.headSha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
        pr.state = PullRequestState::Open;
        pr.draft = true;

        governance.openPullRequest(pr);

        std::cout << "Initial draft state:\n";
        printEligibility(pr.id, governance.evaluate(pr.id));

        governance.markReady(pr.id);

        governance.submitReview(
            pr.id,
            "reviewer-ada",
            ReviewState::Approved,
            "Signature verification is correct.",
            true
        );

        governance.submitReview(
            pr.id,
            "reviewer-lin",
            ReviewState::Commented,
            "Please clarify the release manifest schema.",
            true
        );

        governance.addComment(
            pr.id,
            "reviewer-lin",
            "src/release_manifest.cpp",
            84,
            "Validate the signing key identifier before use."
        );

        governance.setCheck(pr.id, "unit-tests", CheckState::Success);
        governance.setCheck(pr.id, "security-scan", CheckState::Pending);

        std::cout << "\nBlocked by review policy, conversation, and CI:\n";
        printEligibility(pr.id, governance.evaluate(pr.id));

        governance.submitReview(
            pr.id,
            "reviewer-lin",
            ReviewState::Approved,
            "The schema and key validation are now clear.",
            true
        );

        governance.resolveComment(pr.id, 0);
        governance.setCheck(pr.id, "security-scan", CheckState::Success);

        std::cout << "\nStill requires a second approval:\n";
        printEligibility(pr.id, governance.evaluate(pr.id));

        governance.submitReview(
            pr.id,
            "reviewer-grace",
            ReviewState::Approved,
            "The implementation and tests meet the release requirements.",
            true
        );

        std::cout << "\nReady for merge:\n";
        printEligibility(pr.id, governance.evaluate(pr.id));

        // Updating the head invalidates old head-specific check results.
        governance.synchronize(
            pr.id,
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        );

        std::cout << "\nAfter new commits:\n";
        printEligibility(pr.id, governance.evaluate(pr.id));

        // Review the updated commit and rerun the required checks.
        governance.submitReview(
            pr.id,
            "reviewer-ada",
            ReviewState::Approved,
            "The updated commit has been reviewed.",
            true
        );

        governance.submitReview(
            pr.id,
            "reviewer-lin",
            ReviewState::Approved,
            "The updated commit is acceptable.",
            true
        );

        governance.setCheck(pr.id, "unit-tests", CheckState::Success);
        governance.setCheck(pr.id, "security-scan", CheckState::Success);

        std::cout << "\nAfter re-review and successful checks:\n";
        printEligibility(pr.id, governance.evaluate(pr.id));

        governance.merge(pr.id, MergeStrategy::Squash);

        try {
            governance.directPush("main", false);
        } catch (const std::exception& error) {
            std::cout << "Direct-push guard: " << error.what() << "\n";
        }

        try {
            governance.deleteBranch("main");
        } catch (const std::exception& error) {
            std::cout << "Deletion guard: " << error.what() << "\n";
        }

        try {
            governance.getPullRequest("PR-MISSING");
        } catch (const std::exception& error) {
            std::cout << "Lookup failure: " << error.what() << "\n";
        }

    } catch (const std::exception& error) {
        std::cerr << "Governance error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
