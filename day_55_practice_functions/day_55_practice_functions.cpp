#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class PRState { Draft, Open, Merged, Closed };
enum class ReviewState { Commented, Approved, ChangesRequested, Dismissed };
enum class CheckState { Pending, Passed, Failed };
enum class MergeStrategy { MergeCommit, Squash, Rebase };

std::string toString(PRState state) {
    switch (state) {
        case PRState::Draft: return "draft";
        case PRState::Open: return "open";
        case PRState::Merged: return "merged";
        case PRState::Closed: return "closed";
    }
    throw std::logic_error("Unknown pull request state");
}

std::string toString(ReviewState state) {
    switch (state) {
        case ReviewState::Commented: return "commented";
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes_requested";
        case ReviewState::Dismissed: return "dismissed";
    }
    throw std::logic_error("Unknown review state");
}

struct Commit {
    std::string sha;
    std::string message;
    std::string parent;
};

class Branch {
public:
    explicit Branch(std::string name) : name_(std::move(name)) {
        if (name_.empty()) throw std::invalid_argument("Branch name is required");
    }

    void addCommit(const Commit& commit) {
        if (deleted_) throw std::runtime_error("Cannot commit to deleted branch");
        if (commit.sha.empty()) throw std::invalid_argument("Commit SHA is required");

        const auto duplicate = std::find_if(
            commits_.begin(), commits_.end(),
            [&](const Commit& existing) { return existing.sha == commit.sha; }
        );
        if (duplicate != commits_.end()) {
            throw std::invalid_argument("Duplicate commit SHA");
        }

        if (!commits_.empty() && commit.parent != commits_.back().sha) {
            throw std::invalid_argument("Commit parent does not match branch head");
        }
        if (commits_.empty() && !commit.parent.empty()) {
            throw std::invalid_argument("Initial branch commit cannot have a parent");
        }
        commits_.push_back(commit);
    }

    const std::string& name() const { return name_; }
    const std::vector<Commit>& commits() const { return commits_; }

    std::string head() const {
        return commits_.empty() ? "" : commits_.back().sha;
    }

    void deleteBranch() {
        if (!commits_.empty()) {
            throw std::runtime_error("Example policy forbids deleting non-empty branches");
        }
        deleted_ = true;
    }

private:
    std::string name_;
    std::vector<Commit> commits_;
    bool deleted_ = false;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string headSha;
    std::vector<std::string> comments;
    bool discussionResolved = true;
};

struct ProtectionPolicy {
    std::size_t requiredApprovals = 2;
    std::set<std::string> requiredChecks{"build", "tests", "security"};
    bool requireResolvedConversations = true;
    bool requireLinearHistory = true;
    bool restrictDirectPush = true;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool allowAdminBypass = false;
};

struct Eligibility {
    bool eligible = false;
    std::vector<std::string> blockers;
    std::set<std::string> approvals;
};

class PullRequest {
public:
    PullRequest(int number, std::string author, Branch& source, Branch& target,
                std::set<std::string> eligibleReviewers, MergeStrategy strategy)
        : number_(number), author_(std::move(author)), source_(source),
          target_(target), eligibleReviewers_(std::move(eligibleReviewers)),
          strategy_(strategy), headSha_(source.head()), baseSha_(target.head()) {
        if (number_ <= 0) throw std::invalid_argument("PR number must be positive");
        if (author_.empty()) throw std::invalid_argument("Author is required");
        if (&source_ == &target_ || source_.name() == target_.name()) {
            throw std::invalid_argument("Source and target must differ");
        }
        if (eligibleReviewers_.count(author_)) {
            throw std::invalid_argument("Author cannot review their own PR");
        }
    }

    void markDraft() {
        requireOpen();
        state_ = PRState::Draft;
    }

    void markReady() {
        if (state_ != PRState::Draft) {
            throw std::runtime_error("Only draft PRs can become ready");
        }
        state_ = PRState::Open;
    }

    void synchronizeBranches() {
        requireOpen();
        headSha_ = source_.head();
        baseSha_ = target_.head();
    }

    void submitReview(const std::string& reviewer, ReviewState state,
                      std::vector<std::string> comments = {}) {
        requireOpen();
        if (!eligibleReviewers_.count(reviewer)) {
            throw std::runtime_error("Reviewer is not eligible");
        }
        if (reviewer == author_) {
            throw std::runtime_error("Self-review is prohibited");
        }
        if (state == ReviewState::Dismissed) {
            throw std::invalid_argument("Dismissal is not a submitted decision");
        }
        if (headSha_.empty()) {
            throw std::runtime_error("Cannot review an empty changeset");
        }

        reviews_.push_back(
            Review{reviewer, state, headSha_, std::move(comments), true}
        );
    }

    void dismissReview(const std::string& reviewer) {
        requireOpen();
        for (auto it = reviews_.rbegin(); it != reviews_.rend(); ++it) {
            if (it->reviewer == reviewer && it->state != ReviewState::Dismissed) {
                it->state = ReviewState::Dismissed;
                return;
            }
        }
        throw std::runtime_error("No review decision to dismiss");
    }

    void setCheck(const std::string& name, CheckState status) {
        requireOpen();
        if (name.empty()) throw std::invalid_argument("Check name is required");
        checks_[name] = {status, headSha_};
    }

    void setUnresolvedConversations(std::size_t count) {
        requireOpen();
        unresolvedConversations_ = count;
    }

    Eligibility evaluate(const ProtectionPolicy& policy) const {
        Eligibility result;

        if (state_ != PRState::Open) result.blockers.push_back("PR is not open");
        if (source_.commits().empty()) result.blockers.push_back("Source branch is empty");
        if (headSha_ != source_.head()) result.blockers.push_back("Source head is stale");
        if (baseSha_ != target_.head()) result.blockers.push_back("Target base is stale");

        // Keep only each reviewer's latest decision. A stale head never approves
        // the current changeset, even if the reviewer previously approved it.
        std::map<std::string, const Review*> latest;
        for (const auto& review : reviews_) latest[review.reviewer] = &review;

        for (const auto& entry : latest) {
            const Review& review = *entry.second;
            if (review.state == ReviewState::Approved &&
                review.headSha == headSha_ &&
                eligibleReviewers_.count(review.reviewer)) {
                result.approvals.insert(review.reviewer);
            }
        }

        if (result.approvals.size() < policy.requiredApprovals) {
            result.blockers.push_back(
                "Insufficient current approvals: " +
                std::to_string(result.approvals.size()) + "/" +
                std::to_string(policy.requiredApprovals)
            );
        }

        for (const auto& required : policy.requiredChecks) {
            auto found = checks_.find(required);
            if (found == checks_.end() ||
                found->second.first != CheckState::Passed ||
                found->second.second != headSha_) {
                result.blockers.push_back("Required check missing, failing, or stale: " + required);
            }
        }

        if (policy.requireResolvedConversations && unresolvedConversations_ > 0) {
            result.blockers.push_back("Unresolved review conversations remain");
        }

        if (policy.requireLinearHistory && strategy_ == MergeStrategy::MergeCommit) {
            result.blockers.push_back("Merge commits violate linear-history policy");
        }

        result.eligible = result.blockers.empty();
        return result;
    }

    std::string merge(const ProtectionPolicy& policy) {
        requireOpen();
        const Eligibility result = evaluate(policy);
        if (!result.eligible) {
            std::string message = "Merge blocked:";
            for (const auto& blocker : result.blockers) message += " " + blocker + ";";
            throw std::runtime_error(message);
        }

        const std::string sha = "merge-pr-" + std::to_string(number_) + "-" + headSha_;
        target_.addCommit(Commit{sha, "Merge pull request #" + std::to_string(number_),
                                 target_.head()});
        state_ = PRState::Merged;
        mergedSha_ = sha;
        return sha;
    }

    void close() {
        requireOpen();
        state_ = PRState::Closed;
    }

    void reopen() {
        if (state_ != PRState::Closed) {
            throw std::runtime_error("Only closed, unmerged PRs can reopen");
        }
        state_ = PRState::Open;
        synchronizeBranches();
    }

    PRState state() const { return state_; }

private:
    void requireOpen() const {
        if (state_ != PRState::Open) {
            throw std::runtime_error("Operation requires an open PR");
        }
    }

    int number_;
    std::string author_;
    Branch& source_;
    Branch& target_;
    std::set<std::string> eligibleReviewers_;
    MergeStrategy strategy_;
    PRState state_ = PRState::Open;
    std::string headSha_;
    std::string baseSha_;
    std::string mergedSha_;
    std::vector<Review> reviews_;
    std::map<std::string, std::pair<CheckState, std::string>> checks_;
    std::size_t unresolvedConversations_ = 0;
};

int main() {
    try {
        Branch main("main");
        main.addCommit({"base001", "Initial release", ""});

        Branch feature("feature/payment-validation");
        feature.addCommit({"feat001", "Validate payment requests", ""});

        ProtectionPolicy policy;
        policy.requiredApprovals = 2;
        policy.requiredChecks = {"build", "tests", "security"};

        PullRequest pr(
            42, "developer", feature, main,
            {"alex", "sam", "jordan"}, MergeStrategy::Squash
        );

        pr.setCheck("build", CheckState::Passed);
        pr.setCheck("tests", CheckState::Passed);
        pr.setCheck("security", CheckState::Passed);
        pr.setUnresolvedConversations(1);

        pr.submitReview("alex", ReviewState::Approved,
                        {"Required fields are validated."});
        pr.submitReview("sam", ReviewState::ChangesRequested,
                        {"Add duplicate transaction coverage."});

        Eligibility first = pr.evaluate(policy);
        std::cout << "Initial eligibility: "
                  << (first.eligible ? "eligible" : "blocked") << '\n';
        for (const auto& reason : first.blockers) {
            std::cout << "  BLOCKED: " << reason << '\n';
        }

        pr.submitReview("sam", ReviewState::Approved,
                        {"Duplicate transaction test passes."});
        pr.setUnresolvedConversations(0);

        Eligibility finalResult = pr.evaluate(policy);
        if (!finalResult.eligible) {
            throw std::runtime_error("Unexpected merge blockers");
        }

        const std::string mergedSha = pr.merge(policy);
        std::cout << "Merged commit: " << mergedSha << '\n';
        std::cout << "Final state: " << toString(pr.state()) << '\n';

        // Merge operations are irreversible lifecycle transitions in this model.
        try {
            pr.reopen();
        } catch (const std::exception& ex) {
            std::cout << "Expected lifecycle restriction: " << ex.what() << '\n';
        }

        // A separate PR illustrates that a merge-commit strategy can be rejected.
        Branch feature2("feature/audit-logging");
        feature2.addCommit({"audit001", "Add audit logging", ""});
        PullRequest pr2(
            43, "developer", feature2, main,
            {"alex", "sam"}, MergeStrategy::MergeCommit
        );
        pr2.submitReview("alex", ReviewState::Approved);
        pr2.submitReview("sam", ReviewState::Approved);
        pr2.setCheck("build", CheckState::Passed);
        pr2.setCheck("tests", CheckState::Passed);
        pr2.setCheck("security", CheckState::Passed);

        const Eligibility historyResult = pr2.evaluate(policy);
        std::cout << "Linear-history policy: "
                  << (historyResult.eligible ? "eligible" : "blocked") << '\n';
        for (const auto& reason : historyResult.blockers) {
            std::cout << "  BLOCKED: " << reason << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Governance failure: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
