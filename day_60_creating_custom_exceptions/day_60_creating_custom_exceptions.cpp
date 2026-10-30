#include <algorithm>
#include <exception>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Custom exceptions provide typed failure categories and stable error codes.
 * Callers can catch WorkflowError for common handling or a specific subtype
 * for recovery that depends on the failed repository operation.
 */
class WorkflowError : public std::runtime_error {
private:
    std::string code_;
    bool retryable_;

public:
    WorkflowError(std::string message, std::string code, bool retryable = false)
        : std::runtime_error(std::move(message)),
          code_(std::move(code)),
          retryable_(retryable) {}

    const std::string& code() const noexcept {
        return code_;
    }

    bool retryable() const noexcept {
        return retryable_;
    }
};

class ValidationError : public WorkflowError {
public:
    explicit ValidationError(const std::string& message)
        : WorkflowError(message, "VALIDATION_ERROR") {}
};

class ResourceNotFoundError : public WorkflowError {
public:
    explicit ResourceNotFoundError(const std::string& message)
        : WorkflowError(message, "RESOURCE_NOT_FOUND") {}
};

class StateTransitionError : public WorkflowError {
public:
    explicit StateTransitionError(const std::string& message)
        : WorkflowError(message, "INVALID_STATE_TRANSITION") {}
};

class ReviewerEligibilityError : public WorkflowError {
public:
    explicit ReviewerEligibilityError(const std::string& message)
        : WorkflowError(message, "REVIEWER_NOT_ELIGIBLE") {}
};

class ProtectionViolationError : public WorkflowError {
public:
    explicit ProtectionViolationError(const std::string& message)
        : WorkflowError(message, "BRANCH_PROTECTION_VIOLATION") {}
};

class MergeConflictError : public WorkflowError {
public:
    explicit MergeConflictError(const std::string& message)
        : WorkflowError(message, "MERGE_CONFLICT") {}
};

class MergeEligibilityError : public WorkflowError {
private:
    std::vector<std::string> reasons_;

public:
    explicit MergeEligibilityError(std::vector<std::string> reasons)
        : WorkflowError("Pull Request does not satisfy merge policy.",
                        "MERGE_NOT_ELIGIBLE"),
          reasons_(std::move(reasons)) {}

    const std::vector<std::string>& reasons() const noexcept {
        return reasons_;
    }
};

class ConcurrencyError : public WorkflowError {
public:
    explicit ConcurrencyError(const std::string& message)
        : WorkflowError(message, "CONCURRENCY_CONFLICT", true) {}
};

enum class PullRequestState {
    Draft,
    Open,
    Closed,
    Merged
};

enum class ReviewDecision {
    Commented,
    Approved,
    ChangesRequested,
    Dismissed
};

enum class CheckState {
    Pending,
    Success,
    Failure
};

enum class MergeStrategy {
    Merge,
    Squash,
    Rebase
};

std::string toString(PullRequestState state) {
    switch (state) {
        case PullRequestState::Draft: return "DRAFT";
        case PullRequestState::Open: return "OPEN";
        case PullRequestState::Closed: return "CLOSED";
        case PullRequestState::Merged: return "MERGED";
    }
    return "UNKNOWN";
}

std::string toString(ReviewDecision decision) {
    switch (decision) {
        case ReviewDecision::Commented: return "COMMENTED";
        case ReviewDecision::Approved: return "APPROVED";
        case ReviewDecision::ChangesRequested: return "CHANGES_REQUESTED";
        case ReviewDecision::Dismissed: return "DISMISSED";
    }
    return "UNKNOWN";
}

std::string toString(MergeStrategy strategy) {
    switch (strategy) {
        case MergeStrategy::Merge: return "MERGE";
        case MergeStrategy::Squash: return "SQUASH";
        case MergeStrategy::Rebase: return "REBASE";
    }
    return "UNKNOWN";
}

struct Commit {
    std::string sha;
    std::string message;
    std::string parentSha;
    std::string author;
};

struct Branch {
    std::string name;
    std::string headSha;
    bool protectedBranch = false;
    bool deleted = false;
};

struct Review {
    std::string reviewer;
    ReviewDecision decision;
    std::string commitSha;
    std::string baseSha;
};

struct StatusCheck {
    std::string name;
    std::string commitSha;
    CheckState state;
    std::string details;
};

struct ReviewDiscussion {
    int id;
    std::string reviewer;
    std::string path;
    int line;
    std::string body;
    bool resolved = false;
};

struct BranchProtection {
    std::size_t requiredApprovals = 1;
    std::set<std::string> requiredChecks{
        "unit-tests",
        "security-scan"
    };
    bool requireConversationResolution = true;
    bool requireLinearHistory = true;
    bool restrictDirectPush = true;
    bool restrictForcePush = true;
    bool restrictDeletion = true;
    bool dismissStaleReviews = true;
    bool enforceAdministrators = true;
    bool allowBypass = false;
    std::set<std::string> bypassUsers;
    std::set<MergeStrategy> allowedStrategies{
        MergeStrategy::Squash,
        MergeStrategy::Rebase
    };
};

struct PullRequest {
    int number = 0;
    std::string title;
    std::string author;
    std::string sourceBranch;
    std::string targetBranch;
    PullRequestState state = PullRequestState::Open;
    std::string baseShaSeen;
    std::size_t version = 1;
    bool hasConflicts = false;
    std::string mergedSha;
    std::vector<Review> reviews;
    std::vector<ReviewDiscussion> discussions;
    std::map<std::pair<std::string, std::string>, StatusCheck> checks;
};

struct EligibilityReport {
    bool eligible = false;
    std::size_t approvals = 0;
    std::vector<std::string> reasons;
};

class RepositoryGovernanceEngine {
private:
    std::map<std::string, Branch> branches_;
    std::map<std::string, Commit> commits_;
    std::map<int, PullRequest> pullRequests_;
    std::set<std::string> eligibleReviewers_;
    BranchProtection protection_;
    int nextPullRequest_ = 0;
    int nextDiscussion_ = 0;
    int nextCommit_ = 0;

    std::string createSha() {
        std::ostringstream output;
        output << "commit-" << ++nextCommit_;
        return output.str();
    }

    Branch& requireBranch(const std::string& name) {
        auto iterator = branches_.find(name);
        if (iterator == branches_.end() || iterator->second.deleted) {
            throw ResourceNotFoundError("Branch '" + name + "' does not exist.");
        }
        return iterator->second;
    }

    PullRequest& requirePullRequest(int number) {
        auto iterator = pullRequests_.find(number);
        if (iterator == pullRequests_.end()) {
            throw ResourceNotFoundError(
                "Pull Request #" + std::to_string(number) + " does not exist."
            );
        }
        return iterator->second;
    }

    bool canBypass(const std::string& actor) const {
        return protection_.allowBypass &&
               !protection_.enforceAdministrators &&
               protection_.bypassUsers.count(actor) > 0;
    }

    Commit makeCommit(
        const std::string& message,
        const std::string& parent,
        const std::string& author
    ) {
        Commit commit{
            createSha(),
            message,
            parent,
            author
        };
        commits_.emplace(commit.sha, commit);
        return commit;
    }

public:
    RepositoryGovernanceEngine(
        std::set<std::string> eligibleReviewers,
        BranchProtection protection = {}
    )
        : eligibleReviewers_(std::move(eligibleReviewers)),
          protection_(std::move(protection)) {
        Commit root = makeCommit("Initial repository state", "", "system");
        branches_.emplace(
            "main",
            Branch{"main", root.sha, true, false}
        );
    }

    void createBranch(
        const std::string& name,
        const std::string& fromBranch = "main"
    ) {
        if (name.empty()) {
            throw ValidationError("Branch name cannot be empty.");
        }
        Branch& parent = requireBranch(fromBranch);

        auto existing = branches_.find(name);
        if (existing != branches_.end() && !existing->second.deleted) {
            throw ValidationError("Branch '" + name + "' already exists.");
        }

        branches_[name] = Branch{name, parent.headSha, false, false};
    }

    Commit pushCommit(
        const std::string& branchName,
        const std::string& message,
        const std::string& author,
        bool force = false,
        const std::string& expectedParent = ""
    ) {
        Branch& branch = requireBranch(branchName);
        if (message.empty() || author.empty()) {
            throw ValidationError("Commit message and author are required.");
        }

        const bool bypass = canBypass(author);
        if (branch.protectedBranch && !bypass) {
            if (protection_.restrictDirectPush) {
                throw ProtectionViolationError(
                    "Direct pushes to protected branch '" + branchName + "' are prohibited."
                );
            }
            if (force && protection_.restrictForcePush) {
                throw ProtectionViolationError(
                    "Force pushes to protected branch '" + branchName + "' are prohibited."
                );
            }
        }

        if (!expectedParent.empty() && expectedParent != branch.headSha) {
            throw ConcurrencyError("Branch head changed before commit creation.");
        }

        Commit commit = makeCommit(message, branch.headSha, author);
        branch.headSha = commit.sha;

        for (auto& item : pullRequests_) {
            PullRequest& pr = item.second;
            if (
                pr.sourceBranch == branchName &&
                (pr.state == PullRequestState::Open ||
                 pr.state == PullRequestState::Draft)
            ) {
                ++pr.version;
            }
        }
        return commit;
    }

    void deleteBranch(const std::string& name, const std::string& actor) {
        Branch& branch = requireBranch(name);
        if (
            branch.protectedBranch &&
            protection_.restrictDeletion &&
            !canBypass(actor)
        ) {
            throw ProtectionViolationError(
                "Deletion of protected branch '" + name + "' is prohibited."
            );
        }
        branch.deleted = true;
    }

    int createPullRequest(
        const std::string& title,
        const std::string& sourceBranch,
        const std::string& targetBranch,
        const std::string& author,
        bool draft = false
    ) {
        if (title.empty() || author.empty()) {
            throw ValidationError("Pull Request title and author are required.");
        }
        if (sourceBranch == targetBranch) {
            throw ValidationError("Source and target branches must differ.");
        }

        Branch& source = requireBranch(sourceBranch);
        Branch& target = requireBranch(targetBranch);

        if (source.headSha == target.headSha) {
            throw ValidationError("The source branch contains no new commits.");
        }

        for (const auto& item : pullRequests_) {
            const PullRequest& existing = item.second;
            if (
                existing.sourceBranch == sourceBranch &&
                existing.targetBranch == targetBranch &&
                (existing.state == PullRequestState::Open ||
                 existing.state == PullRequestState::Draft)
            ) {
                throw ValidationError("An active Pull Request already exists.");
            }
        }

        PullRequest pr;
        pr.number = ++nextPullRequest_;
        pr.title = title;
        pr.author = author;
        pr.sourceBranch = sourceBranch;
        pr.targetBranch = targetBranch;
        pr.state = draft ? PullRequestState::Draft : PullRequestState::Open;
        pr.baseShaSeen = target.headSha;

        pullRequests_.emplace(pr.number, std::move(pr));
        return nextPullRequest_;
    }

    void readyForReview(int number) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Draft) {
            throw StateTransitionError(
                "Only a draft Pull Request can be marked ready."
            );
        }
        pr.state = PullRequestState::Open;
        ++pr.version;
    }

    void submitReview(
        int number,
        const std::string& reviewer,
        ReviewDecision decision
    ) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Open) {
            throw StateTransitionError("Reviews require an open Pull Request.");
        }
        if (reviewer == pr.author ||
            eligibleReviewers_.count(reviewer) == 0) {
            throw ReviewerEligibilityError(
                "Reviewer is not eligible or is the Pull Request author."
            );
        }

        Branch& source = requireBranch(pr.sourceBranch);
        Branch& target = requireBranch(pr.targetBranch);
        pr.reviews.push_back(
            Review{
                reviewer,
                decision,
                source.headSha,
                target.headSha
            }
        );
        ++pr.version;
    }

    void dismissReview(int number, const std::string& reviewer) {
        PullRequest& pr = requirePullRequest(number);
        for (auto iterator = pr.reviews.rbegin();
             iterator != pr.reviews.rend();
             ++iterator) {
            if (iterator->reviewer == reviewer &&
                iterator->decision != ReviewDecision::Dismissed) {
                iterator->decision = ReviewDecision::Dismissed;
                ++pr.version;
                return;
            }
        }
        throw ResourceNotFoundError("No active review exists for this reviewer.");
    }

    int addDiscussion(
        int number,
        const std::string& reviewer,
        const std::string& path,
        int line,
        const std::string& body
    ) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Open) {
            throw StateTransitionError("Discussions require an open Pull Request.");
        }
        if (reviewer == pr.author ||
            eligibleReviewers_.count(reviewer) == 0) {
            throw ReviewerEligibilityError("Commenter is not an eligible reviewer.");
        }
        if (path.empty() || body.empty() || line < 1) {
            throw ValidationError("Discussion path, body, and positive line are required.");
        }

        ReviewDiscussion discussion{
            ++nextDiscussion_,
            reviewer,
            path,
            line,
            body,
            false
        };
        pr.discussions.push_back(discussion);
        ++pr.version;
        return discussion.id;
    }

    void resolveDiscussion(int number, int discussionId) {
        PullRequest& pr = requirePullRequest(number);
        auto iterator = std::find_if(
            pr.discussions.begin(),
            pr.discussions.end(),
            [discussionId](const ReviewDiscussion& discussion) {
                return discussion.id == discussionId;
            }
        );

        if (iterator == pr.discussions.end()) {
            throw ResourceNotFoundError("Review discussion does not exist.");
        }
        iterator->resolved = true;
        ++pr.version;
    }

    void setStatusCheck(
        int number,
        const std::string& name,
        CheckState state,
        const std::string& details = "",
        const std::string& testedSha = ""
    ) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Open) {
            throw StateTransitionError("Checks require an open Pull Request.");
        }
        if (name.empty()) {
            throw ValidationError("Status check name cannot be empty.");
        }

        const std::string currentSha =
            requireBranch(pr.sourceBranch).headSha;
        const std::string actualSha =
            testedSha.empty() ? currentSha : testedSha;

        if (actualSha != currentSha) {
            throw ValidationError("Status check refers to a stale commit.");
        }

        const auto key = std::make_pair(name, actualSha);
        pr.checks[key] = StatusCheck{name, actualSha, state, details};
        ++pr.version;
    }

    void synchronizeBase(int number, bool conflict = false) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Open) {
            throw StateTransitionError(
                "Only open Pull Requests can synchronize their base."
            );
        }

        if (conflict) {
            pr.hasConflicts = true;
            ++pr.version;
            throw MergeConflictError(
                "Base synchronization produced merge conflicts."
            );
        }

        pr.baseShaSeen = requireBranch(pr.targetBranch).headSha;
        pr.hasConflicts = false;
        ++pr.version;
    }

    EligibilityReport evaluate(
        int number,
        MergeStrategy strategy,
        const std::string& actor
    ) {
        PullRequest& pr = requirePullRequest(number);
        Branch& source = requireBranch(pr.sourceBranch);
        Branch& target = requireBranch(pr.targetBranch);
        EligibilityReport report;

        const bool bypass = canBypass(actor);

        if (pr.state != PullRequestState::Open) {
            report.reasons.push_back("Pull Request is not open.");
        }
        if (pr.baseShaSeen != target.headSha) {
            report.reasons.push_back("Base branch must be synchronized.");
        }
        if (pr.hasConflicts) {
            report.reasons.push_back("Merge conflicts remain unresolved.");
        }
        if (protection_.allowedStrategies.count(strategy) == 0) {
            report.reasons.push_back("Merge strategy is not permitted.");
        }
        if (protection_.requireLinearHistory &&
            strategy == MergeStrategy::Merge) {
            report.reasons.push_back("Merge strategy violates linear history.");
        }

        // The most recent decision by each reviewer supersedes older decisions.
        std::map<std::string, Review> latest;
        for (const Review& review : pr.reviews) {
            latest[review.reviewer] = review;
        }

        bool changesRequested = false;
        for (const auto& item : latest) {
            const Review& review = item.second;
            if (review.decision == ReviewDecision::Dismissed) {
                continue;
            }

            const bool currentReview =
                review.commitSha == source.headSha;

            if (protection_.dismissStaleReviews && !currentReview) {
                continue;
            }

            if (review.decision == ReviewDecision::Approved) {
                ++report.approvals;
            }
            if (review.decision == ReviewDecision::ChangesRequested) {
                changesRequested = true;
            }
        }

        if (!bypass) {
            if (report.approvals < protection_.requiredApprovals) {
                report.reasons.push_back("Insufficient current approvals.");
            }
            if (changesRequested) {
                report.reasons.push_back("A reviewer has requested changes.");
            }

            for (const std::string& required : protection_.requiredChecks) {
                const auto iterator = pr.checks.find(
                    std::make_pair(required, source.headSha)
                );
                if (
                    iterator == pr.checks.end() ||
                    iterator->second.state != CheckState::Success
                ) {
                    report.reasons.push_back(
                        "Required check is missing or unsuccessful: " + required
                    );
                }
            }

            if (protection_.requireConversationResolution) {
                const bool unresolved = std::any_of(
                    pr.discussions.begin(),
                    pr.discussions.end(),
                    [](const ReviewDiscussion& discussion) {
                        return !discussion.resolved;
                    }
                );
                if (unresolved) {
                    report.reasons.push_back(
                        "At least one review discussion is unresolved."
                    );
                }
            }
        }

        report.eligible = report.reasons.empty();
        return report;
    }

    Commit merge(
        int number,
        MergeStrategy strategy,
        const std::string& actor,
        std::size_t expectedVersion = 0
    ) {
        PullRequest& pr = requirePullRequest(number);

        if (expectedVersion != 0 && expectedVersion != pr.version) {
            throw ConcurrencyError(
                "Pull Request changed after its eligibility was inspected."
            );
        }

        EligibilityReport report = evaluate(number, strategy, actor);
        if (!report.eligible) {
            throw MergeEligibilityError(std::move(report.reasons));
        }

        Branch& target = requireBranch(pr.targetBranch);
        Commit commit = makeCommit(
            toString(strategy) + " Pull Request #" +
                std::to_string(number) + ": " + pr.title,
            target.headSha,
            actor
        );

        // Only the merge service advances the protected target branch.
        target.headSha = commit.sha;
        pr.mergedSha = commit.sha;
        pr.state = PullRequestState::Merged;
        ++pr.version;
        return commit;
    }

    void closePullRequest(int number) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Open &&
            pr.state != PullRequestState::Draft) {
            throw StateTransitionError("Pull Request cannot be closed from this state.");
        }
        pr.state = PullRequestState::Closed;
        ++pr.version;
    }

    void reopenPullRequest(int number) {
        PullRequest& pr = requirePullRequest(number);
        if (pr.state != PullRequestState::Closed) {
            throw StateTransitionError("Only a closed Pull Request can be reopened.");
        }
        pr.state = PullRequestState::Open;
        ++pr.version;
    }
};

void printEligibility(const EligibilityReport& report) {
    std::cout << "Eligible: " << (report.eligible ? "yes" : "no") << '\n';
    std::cout << "Valid approvals: " << report.approvals << '\n';
    for (const std::string& reason : report.reasons) {
        std::cout << "  - " << reason << '\n';
    }
}

int main() {
    try {
        BranchProtection policy;
        policy.requiredApprovals = 1;
        policy.requiredChecks = {"unit-tests", "security-scan"};
        policy.requireConversationResolution = true;
        policy.requireLinearHistory = true;

        RepositoryGovernanceEngine repository(
            {"bob", "carol", "dave"},
            policy
        );

        repository.createBranch("feature/refund-validation");
        repository.pushCommit(
            "feature/refund-validation",
            "Validate refund request amounts",
            "alice"
        );

        const int pr = repository.createPullRequest(
            "Add refund validation",
            "feature/refund-validation",
            "main",
            "alice",
            true
        );

        repository.readyForReview(pr);

        const int discussion = repository.addDiscussion(
            pr,
            "bob",
            "payments/refunds.cpp",
            57,
            "Validate the lower bound before creating the refund."
        );
        repository.resolveDiscussion(pr, discussion);

        repository.setStatusCheck(
            pr,
            "unit-tests",
            CheckState::Success,
            "All unit tests passed"
        );
        repository.setStatusCheck(
            pr,
            "security-scan",
            CheckState::Success,
            "No critical findings"
        );
        repository.submitReview(pr, "bob", ReviewDecision::Approved);

        std::cout << "Pull Request #" << pr << " eligibility:\n";
        EligibilityReport report = repository.evaluate(
            pr,
            MergeStrategy::Squash,
            "alice"
        );
        printEligibility(report);

        Commit merged = repository.merge(
            pr,
            MergeStrategy::Squash,
            "alice"
        );
        std::cout << "\nMerged as " << merged.sha << '\n';

        // Protected branch failures are distinct from merge-policy failures.
        try {
            repository.pushCommit(
                "main",
                "Attempt direct protected-branch write",
                "alice"
            );
        } catch (const ProtectionViolationError& error) {
            std::cout << "\nProtected branch rejection ["
                      << error.code() << "]: " << error.what() << '\n';
        }

        repository.createBranch("feature/second-change");
        repository.pushCommit(
            "feature/second-change",
            "Add another refund rule",
            "alice"
        );
        const int second = repository.createPullRequest(
            "Add another refund rule",
            "feature/second-change",
            "main",
            "alice"
        );

        try {
            repository.submitReview(
                second,
                "alice",
                ReviewDecision::Approved
            );
        } catch (const ReviewerEligibilityError& error) {
            std::cout << "\nSelf-review rejection ["
                      << error.code() << "]: " << error.what() << '\n';
        }

        repository.submitReview(second, "bob", ReviewDecision::Approved);

        // Advancing the source head makes the earlier approval stale.
        repository.pushCommit(
            "feature/second-change",
            "Fix refund amount boundary case",
            "alice"
        );
        repository.setStatusCheck(
            second,
            "unit-tests",
            CheckState::Success
        );
        repository.setStatusCheck(
            second,
            "security-scan",
            CheckState::Success
        );

        std::cout << "\nEligibility after a source update:\n";
        printEligibility(
            repository.evaluate(second, MergeStrategy::Squash, "alice")
        );

        try {
            repository.merge(second, MergeStrategy::Squash, "alice");
        } catch (const MergeEligibilityError& error) {
            std::cout << "\nMerge rejected [" << error.code() << "]:\n";
            for (const std::string& reason : error.reasons()) {
                std::cout << "  - " << reason << '\n';
            }
        }

    } catch (const WorkflowError& error) {
        std::cerr << "Workflow failure [" << error.code() << "]: "
                  << error.what()
                  << " (retryable=" << (error.retryable() ? "true" : "false")
                  << ")\n";
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Unexpected failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
