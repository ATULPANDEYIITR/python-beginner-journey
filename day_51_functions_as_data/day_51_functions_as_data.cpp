#include <algorithm>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class PullRequestState {
    Draft,
    Open,
    Closed,
    Merged
};

enum class ReviewState {
    Commented,
    Approved,
    ChangesRequested,
    Dismissed
};

enum class MergeStrategy {
    MergeCommit,
    Squash,
    Rebase
};

struct Commit {
    std::string sha;
    std::string message;
    std::string author;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::vector<std::string> comments;
};

struct StatusCheck {
    std::string name;
    bool passed;
};

struct PullRequest {
    int number;
    std::string sourceBranch;
    std::string targetBranch;
    std::vector<Commit> commits;
    PullRequestState state{PullRequestState::Open};
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    int openConversations{0};
    bool mergeable{true};
    bool synchronized{true};
};

struct BranchProtection {
    std::string branchName;
    std::size_t requiredReviews{0};
    std::set<std::string> requiredChecks;
    bool requireConversationResolution{false};
    bool requireLinearHistory{false};
    bool allowDirectPush{false};
    bool allowForcePush{false};
    bool allowDeletion{false};
    bool allowAdminBypass{false};
};

struct Repository {
    std::string name;
    std::string defaultBranch;
    std::map<std::string, BranchProtection> protection;
};

/*
 * Function objects are stored as values and passed into the governance
 * engine. std::function gives the engine a uniform callable interface while
 * still permitting lambdas, function pointers, and stateful functors.
 */
using GovernanceRule =
    std::function<bool(const PullRequest&, const Repository&)>;

class GovernanceEngine {
private:
    std::map<std::string, GovernanceRule> rules_;

public:
    void registerRule(std::string name, GovernanceRule rule) {
        if (name.empty() || !rule) {
            throw std::invalid_argument("Rule name and callable are required.");
        }
        rules_[std::move(name)] = std::move(rule);
    }

    bool evaluate(
        const std::string& name,
        const PullRequest& pr,
        const Repository& repository) const {

        auto it = rules_.find(name);
        if (it == rules_.end()) {
            throw std::out_of_range("Unknown governance rule: " + name);
        }

        return it->second(pr, repository);
    }

    std::vector<std::string> passingRules(
        const PullRequest& pr,
        const Repository& repository) const {

        std::vector<std::string> result;

        for (const auto& [name, rule] : rules_) {
            if (rule(pr, repository)) {
                result.push_back(name);
            }
        }

        return result;
    }
};

const BranchProtection& protectionFor(
    const PullRequest& pr,
    const Repository& repository) {

    auto it = repository.protection.find(pr.targetBranch);

    if (it == repository.protection.end()) {
        throw std::runtime_error(
            "Target branch has no branch-protection policy."
        );
    }

    return it->second;
}

bool isOpenAndMergeable(
    const PullRequest& pr,
    const Repository&) {

    return pr.state == PullRequestState::Open &&
           pr.mergeable &&
           pr.synchronized;
}

bool hasRequiredApprovals(
    const PullRequest& pr,
    const Repository& repository) {

    const auto& policy = protectionFor(pr, repository);
    std::set<std::string> approvedReviewers;

    for (const auto& review : pr.reviews) {
        if (review.state == ReviewState::Approved) {
            approvedReviewers.insert(review.reviewer);
        }
    }

    /*
     * A set prevents multiple approvals from the same reviewer from
     * satisfying a multi-review requirement.
     */
    return approvedReviewers.size() >= policy.requiredReviews;
}

bool hasNoRequestedChanges(
    const PullRequest& pr,
    const Repository&) {

    return std::none_of(
        pr.reviews.begin(),
        pr.reviews.end(),
        [](const Review& review) {
            return review.state == ReviewState::ChangesRequested;
        }
    );
}

bool requiredChecksPass(
    const PullRequest& pr,
    const Repository& repository) {

    const auto& policy = protectionFor(pr, repository);

    for (const auto& required : policy.requiredChecks) {
        auto check = std::find_if(
            pr.checks.begin(),
            pr.checks.end(),
            [&](const StatusCheck& current) {
                return current.name == required;
            }
        );

        if (check == pr.checks.end() || !check->passed) {
            return false;
        }
    }

    return true;
}

bool conversationsResolved(
    const PullRequest& pr,
    const Repository& repository) {

    const auto& policy = protectionFor(pr, repository);

    return !policy.requireConversationResolution ||
           pr.openConversations == 0;
}

bool branchPolicyAllowsMerge(
    const PullRequest& pr,
    const Repository& repository) {

    return isOpenAndMergeable(pr, repository) &&
           hasRequiredApprovals(pr, repository) &&
           hasNoRequestedChanges(pr, repository) &&
           requiredChecksPass(pr, repository) &&
           conversationsResolved(pr, repository);
}

/*
 * Higher-order composition: the function returned from allOf becomes a new
 * piece of policy data. This separates policy construction from execution.
 */
GovernanceRule allOf(std::vector<GovernanceRule> rules) {
    if (rules.empty()) {
        throw std::invalid_argument("Cannot compose an empty rule set.");
    }

    return [rules = std::move(rules)](
               const PullRequest& pr,
               const Repository& repository) {

        return std::all_of(
            rules.begin(),
            rules.end(),
            [&](const GovernanceRule& rule) {
                return rule(pr, repository);
            }
        );
    };
}

std::string merge(
    PullRequest& pr,
    const Repository& repository,
    MergeStrategy strategy) {

    if (!branchPolicyAllowsMerge(pr, repository)) {
        throw std::runtime_error(
            "Pull Request does not satisfy merge policy."
        );
    }

    pr.state = PullRequestState::Merged;

    switch (strategy) {
        case MergeStrategy::MergeCommit:
            return "Merge commit created";
        case MergeStrategy::Squash:
            return "Commits squashed into target branch";
        case MergeStrategy::Rebase:
            return "Commits rebased onto target branch";
    }

    throw std::logic_error("Unknown merge strategy.");
}

void printRules(const std::vector<std::string>& rules) {
    std::cout << "Passing rules:\n";
    for (const auto& rule : rules) {
        std::cout << "  " << rule << '\n';
    }
}

int main() {
    try {
        Repository repository{
            "inventory-service",
            "main",
            {}
        };

        repository.protection.emplace(
            "main",
            BranchProtection{
                "main",
                2,
                {"unit-tests", "security-scan"},
                true,
                true,
                false,
                false,
                false,
                false
            }
        );

        PullRequest pr{
            500,
            "feature/inventory-reservation",
            "main",
            {
                {"abc123", "Implement reservation validation", "alice"},
                {"def456", "Add concurrency tests", "alice"}
            }
        };

        pr.reviews.push_back(
            {"bob", ReviewState::Approved, {}}
        );

        pr.reviews.push_back(
            {"carol", ReviewState::Approved, {}}
        );

        pr.checks.push_back({"unit-tests", true});
        pr.checks.push_back({"security-scan", true});

        GovernanceEngine engine;

        /*
         * Named functions are registered as data.
         */
        engine.registerRule("mergeable", isOpenAndMergeable);
        engine.registerRule("approvals", hasRequiredApprovals);
        engine.registerRule("review-state", hasNoRequestedChanges);
        engine.registerRule("status-checks", requiredChecksPass);
        engine.registerRule("conversations", conversationsResolved);

        /*
         * A lambda is also a function object. It can enforce a repository
         * convention without requiring a separate named function.
         */
        engine.registerRule(
            "has-commits",
            [](const PullRequest& candidate, const Repository&) {
                return !candidate.commits.empty();
            }
        );

        printRules(engine.passingRules(pr, repository));

        /*
         * The same function values can be composed into a reusable policy.
         */
        GovernanceRule productionMergePolicy = allOf({
            isOpenAndMergeable,
            hasRequiredApprovals,
            hasNoRequestedChanges,
            requiredChecksPass,
            conversationsResolved
        });

        std::cout
            << "Production merge policy: "
            << std::boolalpha
            << productionMergePolicy(pr, repository)
            << '\n';

        std::cout
            << "Merge result: "
            << merge(pr, repository, MergeStrategy::Squash)
            << '\n';

        /*
         * Failure case: two reviews by the same person do not count as
         * two independent approvals because approval identity is set-based.
         */
        PullRequest blocked{
            501,
            "feature/reporting",
            "main",
            {{"xyz789", "Add reporting endpoint", "dave"}}
        };

        blocked.reviews.push_back(
            {"bob", ReviewState::Approved, {}}
        );

        blocked.reviews.push_back(
            {"bob", ReviewState::Approved, {}}
        );

        blocked.checks.push_back({"unit-tests", true});
        blocked.checks.push_back({"security-scan", true});

        std::cout
            << "Duplicate-review approval result: "
            << hasRequiredApprovals(blocked, repository)
            << '\n';

        /*
         * Functions can be stored in containers alongside descriptive data.
         * This models configurable governance without serializing executable
         * code itself.
         */
        std::vector<std::pair<std::string, GovernanceRule>> auditRules{
            {"mergeable", isOpenAndMergeable},
            {"approvals", hasRequiredApprovals},
            {"checks", requiredChecksPass}
        };

        std::cout << "Audit evaluation:\n";
        for (const auto& [name, rule] : auditRules) {
            std::cout
                << "  "
                << std::setw(12)
                << std::left
                << name
                << ": "
                << rule(blocked, repository)
                << '\n';
        }

        /*
         * Security boundary: executable functions are selected from a
         * trusted in-process registry. User input should identify a known
         * policy name, not be converted directly into executable code.
         */
    } catch (const std::exception& error) {
        std::cerr << "Governance error: "
                  << error.what()
                  << '\n';
        return 1;
    }

    return 0;
}
