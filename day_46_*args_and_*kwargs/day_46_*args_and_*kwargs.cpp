#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

enum class ReviewState {
    Approved,
    ChangesRequested,
    Commented
};

enum class CheckState {
    Passed,
    Failed,
    Pending
};

enum class PullRequestState {
    Open,
    Closed,
    Merged
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
    bool eligibleReviewer = true;
};

struct StatusCheck {
    std::string name;
    CheckState state;
};

struct BranchProtection {
    std::string branchName;
    int requiredApprovals = 2;
    bool requireAllConversationsResolved = true;
    bool requireLinearHistory = true;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool restrictDirectPushes = true;
    bool allowAdministratorBypass = false;
    std::set<std::string> requiredChecks;
    std::set<std::string> authorizedPushers;
};

struct PullRequest {
    int number;
    std::string title;
    std::string author;
    std::string sourceBranch;
    std::string targetBranch;
    std::string headSha;
    std::string baseSha;
    PullRequestState state = PullRequestState::Open;
    bool draft = false;
    bool hasMergeConflicts = false;
    bool linearHistory = true;
    int unresolvedConversations = 0;
    std::vector<Review> reviews;
    std::map<std::string, CheckState> checks;
};

struct EligibilityResult {
    bool eligible = false;
    std::vector<std::string> blockers;
    int currentApprovals = 0;
};

class GovernanceEngine {
public:
    static void validatePullRequest(const PullRequest& pr) {
        if (pr.number <= 0) {
            throw std::invalid_argument("Pull request number must be positive.");
        }
        if (pr.title.empty() || pr.author.empty() ||
            pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            throw std::invalid_argument("Required pull request fields are empty.");
        }
        if (pr.sourceBranch == pr.targetBranch) {
            throw std::invalid_argument("Source and target branches must differ.");
        }
        if (pr.unresolvedConversations < 0) {
            throw std::invalid_argument("Conversation count cannot be negative.");
        }
    }

    static EligibilityResult evaluate(
        const PullRequest& pr,
        const BranchProtection& protection
    ) {
        validatePullRequest(pr);

        if (protection.requiredApprovals < 0) {
            throw std::invalid_argument("Approval requirement cannot be negative.");
        }

        EligibilityResult result;

        auto block = [&result](const std::string& reason) {
            result.blockers.push_back(reason);
        };

        if (pr.state != PullRequestState::Open) {
            block("Pull request is not open.");
        }
        if (pr.draft) {
            block("Draft pull requests cannot be merged.");
        }
        if (pr.targetBranch != protection.branchName) {
            block("Target branch does not match the evaluated protection policy.");
        }
        if (pr.hasMergeConflicts) {
            block("Merge conflicts must be resolved.");
        }
        if (protection.requireLinearHistory && !pr.linearHistory) {
            block("The proposed merge violates linear-history requirements.");
        }
        if (protection.requireAllConversationsResolved &&
            pr.unresolvedConversations > 0) {
            block("Review conversations remain unresolved.");
        }

        // Only the latest review by each eligible reviewer for the current
        // source commit determines that reviewer's current decision.
        std::map<std::string, Review> latestReviews;
        for (const auto& review : pr.reviews) {
            if (review.eligibleReviewer &&
                review.reviewer != pr.author &&
                review.commitSha == pr.headSha) {
                latestReviews[review.reviewer] = review;
            }
        }

        bool currentChangesRequested = false;
        for (const auto& entry : latestReviews) {
            if (entry.second.state == ReviewState::Approved) {
                ++result.currentApprovals;
            }
            if (entry.second.state == ReviewState::ChangesRequested) {
                currentChangesRequested = true;
            }
        }

        if (result.currentApprovals < protection.requiredApprovals) {
            block("Required approval count has not been reached.");
        }
        if (currentChangesRequested) {
            block("A current reviewer has requested changes.");
        }

        // A required check is satisfied only by an explicit passing result.
        // Missing and pending checks both prevent merging.
        for (const auto& requiredName : protection.requiredChecks) {
            auto found = pr.checks.find(requiredName);
            if (found == pr.checks.end() ||
                found->second != CheckState::Passed) {
                block("Required check is not passing: " + requiredName);
            }
        }

        result.eligible = result.blockers.empty();
        return result;
    }

    static void synchronize(PullRequest& pr, const std::string& newHeadSha) {
        if (pr.state != PullRequestState::Open) {
            throw std::logic_error("Only open pull requests can be synchronized.");
        }
        if (newHeadSha.empty() || newHeadSha == pr.headSha) {
            throw std::invalid_argument("A different, non-empty commit is required.");
        }

        pr.headSha = newHeadSha;
        // The check map is cleared because checks on an earlier commit do not
        // establish that the updated source revision passes validation.
        pr.checks.clear();
    }

    static void merge(PullRequest& pr, const BranchProtection& protection) {
        const EligibilityResult result = evaluate(pr, protection);
        if (!result.eligible) {
            throw std::logic_error(
                "Merge rejected: " + joinBlockers(result.blockers)
            );
        }
        pr.state = PullRequestState::Merged;
    }

    static bool canDirectPush(
        const BranchProtection& protection,
        const std::string& actor
    ) {
        if (!protection.restrictDirectPushes) {
            return true;
        }
        return protection.authorizedPushers.count(actor) > 0;
    }

    static bool canForcePush(const BranchProtection& protection, bool isAdmin) {
        if (isAdmin && protection.allowAdministratorBypass) {
            return true;
        }
        return protection.allowForcePush;
    }

    static bool canDeleteBranch(
        const BranchProtection& protection,
        bool isAdmin
    ) {
        if (isAdmin && protection.allowAdministratorBypass) {
            return true;
        }
        return protection.allowDeletion;
    }

private:
    static std::string joinBlockers(const std::vector<std::string>& blockers) {
        std::string result;
        for (const auto& blocker : blockers) {
            if (!result.empty()) {
                result += " ";
            }
            result += "[" + blocker + "]";
        }
        return result;
    }
};

static std::string reviewStateName(ReviewState state) {
    switch (state) {
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes requested";
        case ReviewState::Commented: return "commented";
    }
    return "unknown";
}

static void printEligibility(const EligibilityResult& result) {
    std::cout << "Merge eligible: " << (result.eligible ? "yes" : "no")
              << "\nCurrent approvals: " << result.currentApprovals << '\n';

    for (const auto& blocker : result.blockers) {
        std::cout << "Blocked by: " << blocker << '\n';
    }
}

int main() {
    try {
        BranchProtection protection{
            "main",
            2,
            true,
            true,
            false,
            false,
            true,
            false,
            {"unit-tests", "security-scan"},
            {"release-bot"}
        };

        PullRequest pr{
            184,
            "Require verified deployment manifests",
            "maya",
            "feature/verified-manifests",
            "main",
            "a91c2ef",
            "70bd119"
        };

        pr.draft = false;
        pr.linearHistory = true;
        pr.unresolvedConversations = 0;
        pr.reviews = {
            {"alex", ReviewState::Approved, "a91c2ef", true},
            {"sam", ReviewState::Approved, "a91c2ef", true},
            {"maya", ReviewState::Approved, "a91c2ef", true}
        };
        pr.checks = {
            {"unit-tests", CheckState::Passed},
            {"security-scan", CheckState::Passed}
        };

        std::cout << "Repository governance case study\n";
        std::cout << "Pull request #" << pr.number << ": " << pr.title << '\n';

        auto result = GovernanceEngine::evaluate(pr, protection);
        printEligibility(result);

        std::cout << "\nSource branch synchronization\n";
        GovernanceEngine::synchronize(pr, "c814d02");
        result = GovernanceEngine::evaluate(pr, protection);
        printEligibility(result);

        std::cout << "\nRevalidation of updated source commit\n";
        pr.reviews.push_back(
            {"alex", ReviewState::Approved, "c814d02", true}
        );
        pr.reviews.push_back(
            {"sam", ReviewState::Approved, "c814d02", true}
        );
        pr.checks["unit-tests"] = CheckState::Passed;
        pr.checks["security-scan"] = CheckState::Passed;

        result = GovernanceEngine::evaluate(pr, protection);
        printEligibility(result);

        GovernanceEngine::merge(pr, protection);
        std::cout << "Final pull request state: merged\n";

        std::cout << "Developer direct push allowed: "
                  << (GovernanceEngine::canDirectPush(protection, "maya")
                      ? "yes" : "no") << '\n';
        std::cout << "Release bot direct push allowed: "
                  << (GovernanceEngine::canDirectPush(protection, "release-bot")
                      ? "yes" : "no") << '\n';
        std::cout << "Administrator force push allowed: "
                  << (GovernanceEngine::canForcePush(protection, true)
                      ? "yes" : "no") << '\n';
        std::cout << "Administrator branch deletion allowed: "
                  << (GovernanceEngine::canDeleteBranch(protection, true)
                      ? "yes" : "no") << '\n';

        try {
            GovernanceEngine::merge(pr, protection);
        } catch (const std::logic_error& error) {
            std::cout << "Repeated merge rejected: " << error.what() << '\n';
        }

        std::cout << "Review states remain distinct: "
                  << reviewStateName(ReviewState::ChangesRequested) << '\n';

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Governance error: " << error.what() << '\n';
        return 1;
    }
}
