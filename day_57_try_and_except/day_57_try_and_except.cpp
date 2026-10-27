#include <algorithm>
#include <iostream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

enum class ReviewDecision {
    Pending,
    Approved,
    ChangesRequested,
    Rejected
};

enum class CheckState {
    Pending,
    Passed,
    Failed
};

enum class PullRequestState {
    Draft,
    Open,
    Blocked,
    Mergeable,
    Merged,
    Closed
};

class RepositoryError : public std::runtime_error {
public:
    explicit RepositoryError(const std::string& message)
        : std::runtime_error(message) {}
};

class ValidationError : public RepositoryError {
public:
    explicit ValidationError(const std::string& message)
        : RepositoryError(message) {}
};

class MergePolicyError : public RepositoryError {
public:
    explicit MergePolicyError(const std::string& message)
        : RepositoryError(message) {}
};

struct Review {
    std::string reviewer;
    ReviewDecision decision;
    bool dismissed{false};
};

struct StatusCheck {
    std::string name;
    CheckState state;
};

struct PullRequest {
    int number;
    std::string sourceBranch;
    std::string targetBranch;
    PullRequestState state;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    int unresolvedConversations{0};
};

class RepositoryGovernanceEngine {
private:
    int requiredApprovals_;
    bool requireResolvedConversations_;
    bool requireAllChecksPassed_;

    static void validateBranch(const std::string& branch) {
        if (branch.empty()) {
            throw ValidationError("Branch name cannot be empty.");
        }

        if (branch.size() > 255) {
            throw ValidationError("Branch name is too long.");
        }

        if (branch.find(' ') != std::string::npos) {
            throw ValidationError("Branch names cannot contain spaces.");
        }
    }

public:
    RepositoryGovernanceEngine(
        int requiredApprovals,
        bool requireResolvedConversations,
        bool requireAllChecksPassed
    )
        : requiredApprovals_(requiredApprovals),
          requireResolvedConversations_(requireResolvedConversations),
          requireAllChecksPassed_(requireAllChecksPassed) {
        if (requiredApprovals < 0) {
            throw ValidationError("Required approvals cannot be negative.");
        }
    }

    bool isMergeEligible(const PullRequest& pullRequest) const {
        validateBranch(pullRequest.sourceBranch);
        validateBranch(pullRequest.targetBranch);

        if (pullRequest.sourceBranch == pullRequest.targetBranch) {
            throw ValidationError(
                "Source and target branches must differ."
            );
        }

        if (pullRequest.state != PullRequestState::Open &&
            pullRequest.state != PullRequestState::Blocked &&
            pullRequest.state != PullRequestState::Mergeable) {
            return false;
        }

        const int approvals = static_cast<int>(std::count_if(
            pullRequest.reviews.begin(),
            pullRequest.reviews.end(),
            [](const Review& review) {
                return review.decision == ReviewDecision::Approved &&
                       !review.dismissed;
            }
        ));

        const bool hasChangesRequested = std::any_of(
            pullRequest.reviews.begin(),
            pullRequest.reviews.end(),
            [](const Review& review) {
                return review.decision == ReviewDecision::ChangesRequested &&
                       !review.dismissed;
            }
        );

        if (hasChangesRequested) {
            return false;
        }

        if (approvals < requiredApprovals_) {
            return false;
        }

        if (requireResolvedConversations_ &&
            pullRequest.unresolvedConversations > 0) {
            return false;
        }

        if (requireAllChecksPassed_) {
            const bool allPassed = !pullRequest.checks.empty() &&
                std::all_of(
                    pullRequest.checks.begin(),
                    pullRequest.checks.end(),
                    [](const StatusCheck& check) {
                        return check.state == CheckState::Passed;
                    }
                );

            if (!allPassed) {
                return false;
            }
        }

        return true;
    }

    PullRequest merge(PullRequest pullRequest) const {
        if (!isMergeEligible(pullRequest)) {
            throw MergePolicyError(
                "Pull Request does not satisfy merge policy."
            );
        }

        pullRequest.state = PullRequestState::Merged;
        return pullRequest;
    }
};

class Repository {
private:
    std::string name_;
    bool protectedBranch_;
    std::map<int, PullRequest> pullRequests_;

public:
    Repository(std::string name, bool protectedBranch)
        : name_(std::move(name)),
          protectedBranch_(protectedBranch) {
        if (name_.empty()) {
            throw ValidationError("Repository name cannot be empty.");
        }
    }

    void addPullRequest(PullRequest pullRequest) {
        if (pullRequests_.contains(pullRequest.number)) {
            throw ValidationError(
                "Pull Request number already exists."
            );
        }

        pullRequests_.emplace(
            pullRequest.number,
            std::move(pullRequest)
        );
    }

    std::optional<PullRequest> findPullRequest(int number) const {
        auto iterator = pullRequests_.find(number);

        if (iterator == pullRequests_.end()) {
            return std::nullopt;
        }

        return iterator->second;
    }

    PullRequest mergePullRequest(
        int number,
        const RepositoryGovernanceEngine& engine
    ) {
        if (!protectedBranch_) {
            throw MergePolicyError(
                "This repository is not configured for governed merging."
            );
        }

        auto iterator = pullRequests_.find(number);

        if (iterator == pullRequests_.end()) {
            throw ValidationError("Pull Request was not found.");
        }

        iterator->second = engine.merge(iterator->second);
        return iterator->second;
    }
};

std::string stateName(PullRequestState state) {
    switch (state) {
        case PullRequestState::Draft:
            return "draft";
        case PullRequestState::Open:
            return "open";
        case PullRequestState::Blocked:
            return "blocked";
        case PullRequestState::Mergeable:
            return "mergeable";
        case PullRequestState::Merged:
            return "merged";
        case PullRequestState::Closed:
            return "closed";
    }

    return "unknown";
}

int main() {
    try {
        RepositoryGovernanceEngine engine(
            2,
            true,
            true
        );

        Repository repository("secure-platform", true);

        PullRequest validPullRequest{
            101,
            "feature/retry-handling",
            "main",
            PullRequestState::Open,
            {
                {"alice", ReviewDecision::Approved, false},
                {"bob", ReviewDecision::Approved, false}
            },
            {
                {"build", CheckState::Passed},
                {"security", CheckState::Passed},
                {"tests", CheckState::Passed}
            },
            0
        };

        PullRequest blockedPullRequest{
            102,
            "feature/incomplete-review",
            "main",
            PullRequestState::Open,
            {
                {"alice", ReviewDecision::Approved, false}
            },
            {
                {"build", CheckState::Passed},
                {"security", CheckState::Failed}
            },
            1
        };

        repository.addPullRequest(validPullRequest);
        repository.addPullRequest(blockedPullRequest);

        for (int number : {101, 102, 999}) {
            try {
                auto request = repository.findPullRequest(number);

                if (!request.has_value()) {
                    throw ValidationError(
                        "Pull Request " +
                        std::to_string(number) +
                        " was not found."
                    );
                }

                bool eligible = engine.isMergeEligible(*request);

                std::cout
                    << "PR #" << number
                    << " merge eligible: "
                    << std::boolalpha
                    << eligible
                    << '\n';
            } catch (const ValidationError& error) {
                std::cout
                    << "Validation failure: "
                    << error.what()
                    << '\n';
            }
        }

        try {
            PullRequest merged =
                repository.mergePullRequest(101, engine);

            std::cout
                << "PR #" << merged.number
                << " state: "
                << stateName(merged.state)
                << '\n';
        } catch (const MergePolicyError& error) {
            std::cout
                << "Merge blocked: "
                << error.what()
                << '\n';
        }

        try {
            repository.mergePullRequest(102, engine);
        } catch (const RepositoryError& error) {
            std::cout
                << "Expected merge failure: "
                << error.what()
                << '\n';
        }

        try {
            PullRequest invalid{
                103,
                "",
                "main",
                PullRequestState::Open,
                {},
                {},
                0
            };

            engine.isMergeEligible(invalid);
        } catch (const ValidationError& error) {
            std::cout
                << "Expected validation failure: "
                << error.what()
                << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
