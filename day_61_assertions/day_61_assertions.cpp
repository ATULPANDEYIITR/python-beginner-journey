#include <algorithm>
#include <cassert>
#include <exception>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class PullRequestState {
    Draft,
    Open,
    Merged,
    Closed
};

class ValidationError : public std::invalid_argument {
public:
    explicit ValidationError(const std::string& message)
        : std::invalid_argument(message) {}
};

class Repository {
private:
    std::string name_;
    std::string defaultBranch_;
    std::set<std::string> commits_;

    void checkInvariant() const {
        // These checks represent internal assumptions. External input is
        // validated with exceptions because assertions can be disabled.
        assert(!name_.empty());
        assert(!defaultBranch_.empty());
    }

public:
    Repository(std::string name, std::string defaultBranch)
        : name_(std::move(name)), defaultBranch_(std::move(defaultBranch)) {
        if (name_.empty()) {
            throw ValidationError("repository name cannot be empty");
        }
        if (defaultBranch_.empty()) {
            throw ValidationError("default branch cannot be empty");
        }
        checkInvariant();
    }

    void addCommit(const std::string& commitId) {
        if (commitId.empty()) {
            throw ValidationError("commit ID cannot be empty");
        }

        const auto [_, inserted] = commits_.insert(commitId);
        if (!inserted) {
            throw ValidationError("duplicate commit ID");
        }

        assert(commits_.find(commitId) != commits_.end());
        checkInvariant();
    }

    std::size_t commitCount() const {
        return commits_.size();
    }
};

struct Review {
    std::string reviewer;
    bool approved;
    bool unresolvedComments;
};

class PullRequest {
private:
    int number_;
    std::string sourceBranch_;
    std::string targetBranch_;
    std::vector<std::string> commits_;
    std::vector<Review> reviews_;
    PullRequestState state_;

    void checkInvariant() const {
        assert(number_ > 0);
        assert(!sourceBranch_.empty());
        assert(!targetBranch_.empty());
        assert(sourceBranch_ != targetBranch_);

        if (state_ == PullRequestState::Merged) {
            assert(!commits_.empty());
        }
    }

public:
    PullRequest(
        int number,
        std::string sourceBranch,
        std::string targetBranch
    )
        : number_(number),
          sourceBranch_(std::move(sourceBranch)),
          targetBranch_(std::move(targetBranch)),
          state_(PullRequestState::Draft) {
        if (number <= 0) {
            throw ValidationError("pull request number must be positive");
        }
        if (sourceBranch_.empty() || targetBranch_.empty()) {
            throw ValidationError("branch names are required");
        }
        if (sourceBranch_ == targetBranch_) {
            throw ValidationError("source and target branches must differ");
        }

        checkInvariant();
    }

    void addCommit(const std::string& commitId) {
        if (state_ == PullRequestState::Merged) {
            throw ValidationError("merged pull request cannot receive commits");
        }
        if (commitId.empty()) {
            throw ValidationError("commit ID cannot be empty");
        }

        if (std::find(commits_.begin(), commits_.end(), commitId) != commits_.end()) {
            throw ValidationError("duplicate pull request commit");
        }

        commits_.push_back(commitId);
        checkInvariant();
    }

    void addReview(const Review& review) {
        if (review.reviewer.empty()) {
            throw ValidationError("reviewer identity is required");
        }

        reviews_.push_back(review);
        checkInvariant();
    }

    void markReady() {
        if (state_ == PullRequestState::Merged) {
            throw ValidationError("merged pull request cannot become ready");
        }
        state_ = PullRequestState::Open;
        checkInvariant();
    }

    bool hasApproval() const {
        return std::any_of(
            reviews_.begin(),
            reviews_.end(),
            [](const Review& review) {
                return review.approved && !review.unresolvedComments;
            }
        );
    }

    bool hasUnresolvedComments() const {
        return std::any_of(
            reviews_.begin(),
            reviews_.end(),
            [](const Review& review) {
                return review.unresolvedComments;
            }
        );
    }

    bool canMerge() const {
        return state_ == PullRequestState::Open &&
               !commits_.empty() &&
               hasApproval() &&
               !hasUnresolvedComments();
    }

    void merge() {
        if (!canMerge()) {
            throw ValidationError(
                "pull request does not satisfy merge eligibility conditions"
            );
        }

        state_ = PullRequestState::Merged;
        checkInvariant();
    }

    PullRequestState state() const {
        return state_;
    }
};

double average(const std::vector<double>& values) {
    if (values.empty()) {
        throw ValidationError("average requires at least one value");
    }

    double total = 0.0;
    for (double value : values) {
        if (!std::isfinite(value)) {
            throw ValidationError("average requires finite values");
        }
        total += value;
    }

    const double result = total / static_cast<double>(values.size());

    // Mathematical postcondition.
    const auto [minimum, maximum] =
        std::minmax_element(values.begin(), values.end());

    assert(result >= *minimum);
    assert(result <= *maximum);

    return result;
}

void runTests() {
    Repository repository("assertion-lab", "main");
    repository.addCommit("c1");
    repository.addCommit("c2");

    assert(repository.commitCount() == 2);

    try {
        repository.addCommit("c1");
        throw std::logic_error("duplicate commit was accepted");
    } catch (const ValidationError&) {
        // Expected failure.
    }

    PullRequest pullRequest(101, "feature/assertions", "main");
    pullRequest.addCommit("c1");
    pullRequest.markReady();

    pullRequest.addReview({
        "reviewer-a",
        true,
        false
    });

    assert(pullRequest.canMerge());
    pullRequest.merge();
    assert(pullRequest.state() == PullRequestState::Merged);

    try {
        pullRequest.addCommit("c2");
        throw std::logic_error("merged PR accepted a new commit");
    } catch (const ValidationError&) {
        // Expected failure.
    }

    assert(average({10.0, 20.0, 30.0}) == 20.0);

    try {
        average({});
        throw std::logic_error("empty average was accepted");
    } catch (const ValidationError&) {
        // Expected failure.
    }
}

int main() {
    try {
        runTests();
        std::cout << "All C++17 assertion demonstrations and tests passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }
}
