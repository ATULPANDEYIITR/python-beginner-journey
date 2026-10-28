#include <algorithm>
#include <exception>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
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

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
    bool stale{false};
};

struct StatusCheck {
    std::string name;
    bool passed;
};

struct BranchProtection {
    std::size_t requiredApprovals{2};
    std::set<std::string> requiredChecks{"tests", "security"};
    bool requireResolvedConversations{true};
    bool requireLinearHistory{true};
};

class GovernanceError : public std::runtime_error {
public:
    explicit GovernanceError(const std::string& message)
        : std::runtime_error(message) {}
};

class PullRequest {
public:
    PullRequest(
        int number,
        std::string source,
        std::string target,
        std::vector<std::string> commits)
        : number_(number),
          source_(std::move(source)),
          target_(std::move(target)),
          commits_(std::move(commits)),
          headSha_(commits_.back()) {
        if (source_ == target_) {
            throw GovernanceError("Source and target branches must differ.");
        }
        if (commits_.empty()) {
            throw GovernanceError("Pull request requires a changeset.");
        }
    }

    int number() const { return number_; }
    PRState state() const { return state_; }
    const std::string& headSha() const { return headSha_; }

    void addReview(Review review) {
        if (state_ != PRState::Open) {
            throw GovernanceError("Reviews require an open PR.");
        }
        reviews_.push_back(std::move(review));
    }

    void setCheck(std::string name, bool passed) {
        checks_[std::move(name)] = passed;
    }

    void setUnresolvedConversations(std::size_t count) {
        unresolvedConversations_ = count;
    }

    void setMergeStrategy(std::string strategy) {
        mergeStrategy_ = std::move(strategy);
    }

    void synchronizeWithBase() {
        synchronized_ = true;
        for (auto& review : reviews_) {
            review.stale = true;
        }
    }

    std::size_t activeApprovals() const {
        std::size_t count = 0;

        for (const auto& review : reviews_) {
            if (review.state == ReviewState::Approved &&
                !review.stale &&
                review.commitSha == headSha_) {
                ++count;
            }
        }

        return count;
    }

    void markMerged() {
        state_ = PRState::Merged;
    }

    void markClosed() {
        if (state_ == PRState::Merged) {
            throw GovernanceError("Merged PR cannot be closed separately.");
        }
        state_ = PRState::Closed;
    }

    std::vector<std::string> const& commits() const {
        return commits_;
    }

    const std::map<std::string, bool>& checks() const {
        return checks_;
    }

    bool synchronized() const {
        return synchronized_;
    }

    std::size_t unresolvedConversations() const {
        return unresolvedConversations_;
    }

    const std::string& mergeStrategy() const {
        return mergeStrategy_;
    }

private:
    int number_;
    std::string source_;
    std::string target_;
    std::vector<std::string> commits_;
    std::string headSha_;
    PRState state_{PRState::Open};
    std::vector<Review> reviews_;
    std::map<std::string, bool> checks_;
    std::size_t unresolvedConversations_{0};
    bool synchronized_{true};
    std::string mergeStrategy_{"squash"};
};

class Repository {
public:
    explicit Repository(std::string name, BranchProtection protection)
        : name_(std::move(name)), protection_(std::move(protection)) {
        branches_.insert("main");
        branches_.insert("develop");
    }

    void createCommit(const std::string& sha) {
        if (sha.size() < 7) {
            throw GovernanceError("Commit identifier is too short.");
        }
        if (!commits_.insert(sha).second) {
            throw GovernanceError("Duplicate commit.");
        }
    }

    PullRequest& createPullRequest(
        const std::string& source,
        const std::string& target,
        const std::vector<std::string>& commits) {

        if (!branches_.contains(source) || !branches_.contains(target)) {
            throw GovernanceError("Unknown branch.");
        }

        if (commits.empty()) {
            throw GovernanceError("Empty changeset.");
        }

        for (const auto& commit : commits) {
            if (!commits_.contains(commit)) {
                throw GovernanceError("PR references an unknown commit.");
            }
        }

        auto pr = std::make_unique<PullRequest>(
            nextPrNumber_++, source, target, commits);

        const int id = pr->number();
        auto [it, inserted] = pullRequests_.emplace(id, std::move(pr));

        if (!inserted) {
            throw GovernanceError("Could not allocate PR.");
        }

        return *it->second;
    }

    std::vector<std::string> evaluate(const PullRequest& pr) const {
        std::vector<std::string> failures;

        if (pr.state() != PRState::Open) {
            failures.emplace_back("PR is not open.");
        }

        if (!pr.synchronized()) {
            failures.emplace_back("Base branch synchronization is required.");
        }

        if (pr.activeApprovals() < protection_.requiredApprovals) {
            failures.emplace_back("Required approvals are not satisfied.");
        }

        for (const auto& required : protection_.requiredChecks) {
            auto it = pr.checks().find(required);
            if (it == pr.checks().end() || !it->second) {
                failures.push_back("Required check failed or missing: " + required);
            }
        }

        if (protection_.requireResolvedConversations &&
            pr.unresolvedConversations() != 0) {
            failures.emplace_back("Review conversations remain unresolved.");
        }

        if (protection_.requireLinearHistory &&
            pr.mergeStrategy() == "merge") {
            failures.emplace_back("Merge commits violate linear-history policy.");
        }

        return failures;
    }

    bool merge(PullRequest& pr) {
        try {
            const auto failures = evaluate(pr);

            if (!failures.empty()) {
                throw GovernanceError(joinFailures(failures));
            } else {
                // C++ has no native try/else syntax. The explicit else
                // documents the successful non-exceptional path.
                pr.markMerged();
                audit_.push_back(
                    "PR-" + std::to_string(pr.number()) + " merged");
                return true;
            }
        } catch (const GovernanceError& error) {
            audit_.push_back(
                "PR-" + std::to_string(pr.number()) +
                " rejected: " + error.what());
            return false;
        } catch (const std::exception& error) {
            audit_.push_back(
                "PR-" + std::to_string(pr.number()) +
                " unexpected failure: " + error.what());
            return false;
        } finally_placeholder:
        return false;
    }

    // C++17 does not provide a finally keyword. ScopeGuard models the
    // same cleanup guarantee using RAII.
    class ScopeGuard {
    public:
        explicit ScopeGuard(std::function<void()> cleanup)
            : cleanup_(std::move(cleanup)) {}

        ~ScopeGuard() {
            if (cleanup_) {
                cleanup_();
            }
        }

        ScopeGuard(const ScopeGuard&) = delete;
        ScopeGuard& operator=(const ScopeGuard&) = delete;

    private:
        std::function<void()> cleanup_;
    };

    bool mergeWithFinally(PullRequest& pr) {
        ScopeGuard finalized([&]() {
            audit_.push_back(
                "PR-" + std::to_string(pr.number()) +
                " merge attempt finalized");
        });

        try {
            const auto failures = evaluate(pr);

            if (!failures.empty()) {
                throw GovernanceError(joinFailures(failures));
            } else {
                pr.markMerged();
                audit_.push_back(
                    "PR-" + std::to_string(pr.number()) + " merged");
                return true;
            }
        } catch (const GovernanceError& error) {
            audit_.push_back(
                "PR-" + std::to_string(pr.number()) +
                " rejected: " + error.what());
            return false;
        }
    }

    const std::vector<std::string>& audit() const {
        return audit_;
    }

private:
    static std::string joinFailures(
        const std::vector<std::string>& failures) {

        std::string result;

        for (std::size_t i = 0; i < failures.size(); ++i) {
            if (i > 0) result += " ";
            result += failures[i];
        }

        return result;
    }

    std::string name_;
    BranchProtection protection_;
    std::set<std::string> branches_;
    std::set<std::string> commits_;
    std::map<int, std::unique_ptr<PullRequest>> pullRequests_;
    int nextPrNumber_{1};
    std::vector<std::string> audit_;
};

int main() {
    try {
        Repository repository(
            "security-platform",
            BranchProtection{
                2,
                {"tests", "security"},
                true,
                true
            });

        repository.createCommit("abcdef1");
        repository.createCommit("abcdef2");

        auto& pr = repository.createPullRequest(
            "develop",
            "main",
            {"abcdef1", "abcdef2"});

        pr.addReview({
            "alice",
            ReviewState::Approved,
            pr.headSha(),
            false
        });

        pr.addReview({
            "bob",
            ReviewState::Approved,
            pr.headSha(),
            false
        });

        pr.setCheck("tests", true);
        pr.setCheck("security", true);

        const auto failures = repository.evaluate(pr);

        if (failures.empty()) {
            std::cout << "PR is merge-eligible.\n";
        } else {
            std::cout << "PR is blocked:\n";
            for (const auto& failure : failures) {
                std::cout << "  - " << failure << '\n';
            }
        }

        const bool merged = repository.mergeWithFinally(pr);
        std::cout << "Merged: " << std::boolalpha << merged << '\n';

        std::cout << "\nAudit log:\n";
        for (const auto& event : repository.audit()) {
            std::cout << "  " << event << '\n';
        }

        // Demonstrate approval invalidation after synchronization.
        if (pr.state() == PRState::Merged) {
            std::cout << "\nPR is already merged; no synchronization is needed.\n";
        } else {
            pr.synchronizeWithBase();
            std::cout << "\nApprovals after synchronization: "
                      << pr.activeApprovals() << '\n';
        }

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
