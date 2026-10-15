#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Repository governance case study.
 *
 * C++ does not support Python-style named function arguments. This program
 * models named configuration through validated structures, explicit policy
 * objects, and builder methods. It evaluates whether a security-sensitive
 * Pull Request may merge into a protected production branch.
 */

namespace governance {

enum class PullRequestState {
    Draft,
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
        case PullRequestState::Draft: return "draft";
        case PullRequestState::Open: return "open";
        case PullRequestState::Closed: return "closed";
        case PullRequestState::Merged: return "merged";
    }
    throw std::logic_error("Unknown Pull Request state");
}

std::string toString(ReviewState state) {
    switch (state) {
        case ReviewState::Approved: return "approved";
        case ReviewState::ChangesRequested: return "changes requested";
        case ReviewState::Commented: return "commented";
    }
    throw std::logic_error("Unknown review state");
}

std::string toString(MergeStrategy strategy) {
    switch (strategy) {
        case MergeStrategy::MergeCommit: return "merge commit";
        case MergeStrategy::Squash: return "squash";
        case MergeStrategy::Rebase: return "rebase";
    }
    throw std::logic_error("Unknown merge strategy");
}

bool isBlank(const std::string& value) {
    return value.find_first_not_of(" \t\n\r") == std::string::npos;
}

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
    bool dismissed = false;
    bool eligible = true;
};

struct StatusCheck {
    std::string name;
    CheckState state;
};

struct Conversation {
    std::string id;
    bool resolved = false;
};

struct Commit {
    std::string sha;
    std::vector<std::string> changedFiles;
};

struct PullRequest {
    int id = 0;
    std::string title;
    std::string sourceBranch;
    std::string targetBranch;
    PullRequestState state = PullRequestState::Draft;
    std::vector<std::string> requestedReviewers;
    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::map<std::string, CheckState> checks;
    std::vector<Conversation> conversations;
    std::string mergeActor;
    MergeStrategy mergeStrategy = MergeStrategy::Squash;
};

struct BranchProtection {
    std::string branch = "main";
    int requiredApprovals = 2;
    std::set<std::string> requiredChecks{"unit-tests", "security-scan"};
    bool dismissStaleReviews = true;
    bool requireConversationResolution = true;
    bool requireLinearHistory = true;
    bool restrictDirectPushes = true;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool enforceForAdministrators = true;
    bool allowBypass = false;

    BranchProtection& setRequiredApprovals(int count) {
        if (count < 0) {
            throw std::invalid_argument(
                "Required approvals cannot be negative"
            );
        }
        requiredApprovals = count;
        return *this;
    }

    BranchProtection& setRequiredChecks(
        std::set<std::string> checksToRequire
    ) {
        for (const auto& check : checksToRequire) {
            if (isBlank(check)) {
                throw std::invalid_argument(
                    "Required check names cannot be blank"
                );
            }
        }
        requiredChecks = std::move(checksToRequire);
        return *this;
    }

    BranchProtection& setForcePushAllowed(bool allowed) {
        allowForcePush = allowed;
        return *this;
    }
};

class Repository {
private:
    std::string name_;
    std::unordered_map<int, PullRequest> pullRequests_;
    BranchProtection protection_;

    static bool containsReviewer(
        const std::vector<std::string>& reviewers,
        const std::string& reviewer
    ) {
        return std::find(
            reviewers.begin(), reviewers.end(), reviewer
        ) != reviewers.end();
    }

    static bool validSha(const std::string& sha) {
        if (sha.size() < 7 || sha.size() > 40) {
            return false;
        }

        return std::all_of(
            sha.begin(), sha.end(),
            [](unsigned char character) {
                return std::isxdigit(character) != 0 &&
                       !std::isupper(character);
            }
        );
    }

public:
    explicit Repository(std::string name, BranchProtection protection)
        : name_(std::move(name)), protection_(std::move(protection)) {
        if (isBlank(name_)) {
            throw std::invalid_argument("Repository name is required");
        }
        if (isBlank(protection_.branch)) {
            throw std::invalid_argument("Protected branch is required");
        }
    }

    const BranchProtection& protection() const {
        return protection_;
    }

    void createPullRequest(PullRequest request) {
        if (request.id <= 0) {
            throw std::invalid_argument("Pull Request ID must be positive");
        }
        if (pullRequests_.count(request.id)) {
            throw std::invalid_argument("Pull Request ID already exists");
        }
        if (isBlank(request.title)) {
            throw std::invalid_argument("Pull Request title is required");
        }
        if (request.sourceBranch.rfind("feature/", 0) != 0) {
            throw std::invalid_argument(
                "Source branch must begin with feature/"
            );
        }
        if (request.targetBranch != protection_.branch) {
            throw std::invalid_argument(
                "Pull Request must target the protected branch"
            );
        }
        if (request.sourceBranch == request.targetBranch) {
            throw std::invalid_argument(
                "Source and target branches must differ"
            );
        }

        for (const auto& reviewer : request.requestedReviewers) {
            if (isBlank(reviewer)) {
                throw std::invalid_argument(
                    "Requested reviewer cannot be blank"
                );
            }
        }

        std::sort(
            request.requestedReviewers.begin(),
            request.requestedReviewers.end()
        );

        request.requestedReviewers.erase(
            std::unique(
                request.requestedReviewers.begin(),
                request.requestedReviewers.end()
            ),
            request.requestedReviewers.end()
        );

        pullRequests_.emplace(request.id, std::move(request));
    }

    PullRequest& getPullRequest(int id) {
        auto found = pullRequests_.find(id);
        if (found == pullRequests_.end()) {
            throw std::out_of_range("Pull Request does not exist");
        }
        return found->second;
    }

    void addCommit(int id, Commit commit) {
        auto& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error(
                "Commits can only be added to open Pull Requests"
            );
        }

        if (!validSha(commit.sha)) {
            throw std::invalid_argument("Invalid lowercase hexadecimal SHA");
        }

        if (commit.changedFiles.empty()) {
            throw std::invalid_argument(
                "A commit must contain changed files"
            );
        }

        for (const auto& file : commit.changedFiles) {
            if (isBlank(file) || file.front() == '/') {
                throw std::invalid_argument(
                    "Changed file paths must be relative and non-empty"
                );
            }
        }

        const auto duplicate = std::find_if(
            pr.commits.begin(), pr.commits.end(),
            [&](const Commit& existing) {
                return existing.sha == commit.sha;
            }
        );

        if (duplicate != pr.commits.end()) {
            throw std::invalid_argument("Duplicate commit SHA");
        }

        pr.commits.push_back(std::move(commit));

        if (protection_.dismissStaleReviews) {
            const std::string& latestSha = pr.commits.back().sha;

            for (auto& review : pr.reviews) {
                if (review.commitSha != latestSha) {
                    review.dismissed = true;
                }
            }
        }
    }

    void submitReview(int id, Review review) {
        auto& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error(
                "Reviews require an open Pull Request"
            );
        }

        if (isBlank(review.reviewer)) {
            throw std::invalid_argument("Reviewer identity is required");
        }

        if (!containsReviewer(pr.requestedReviewers, review.reviewer)) {
            throw std::invalid_argument(
                "Reviewer was not requested for this Pull Request"
            );
        }

        if (pr.commits.empty() ||
            review.commitSha != pr.commits.back().sha) {
            throw std::invalid_argument(
                "Review must refer to the current commit"
            );
        }

        if (!review.eligible) {
            throw std::invalid_argument(
                "Ineligible reviewer cannot provide a qualifying review"
            );
        }

        // A later review by the same person supersedes the previous review.
        for (auto& existing : pr.reviews) {
            if (existing.reviewer == review.reviewer && !existing.dismissed) {
                existing.dismissed = true;
            }
        }

        pr.reviews.push_back(std::move(review));
    }

    void setCheck(int id, const std::string& name, CheckState state) {
        auto& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error(
                "Status checks cannot update a non-open Pull Request"
            );
        }

        if (isBlank(name)) {
            throw std::invalid_argument("Status-check name is required");
        }

        pr.checks[name] = state;
    }

    void addConversation(int id, Conversation conversation) {
        auto& pr = getPullRequest(id);

        if (pr.state != PullRequestState::Open) {
            throw std::logic_error(
                "Conversations require an open Pull Request"
            );
        }

        if (isBlank(conversation.id)) {
            throw std::invalid_argument("Conversation ID is required");
        }

        const auto duplicate = std::find_if(
            pr.conversations.begin(), pr.conversations.end(),
            [&](const Conversation& existing) {
                return existing.id == conversation.id;
            }
        );

        if (duplicate != pr.conversations.end()) {
            throw std::invalid_argument("Duplicate conversation ID");
        }

        pr.conversations.push_back(std::move(conversation));
    }

    void resolveConversation(int id, const std::string& conversationId) {
        auto& pr = getPullRequest(id);

        auto found = std::find_if(
            pr.conversations.begin(), pr.conversations.end(),
            [&](const Conversation& conversation) {
                return conversation.id == conversationId;
            }
        );

        if (found == pr.conversations.end()) {
            throw std::out_of_range("Conversation does not exist");
        }

        found->resolved = true;
    }

    std::vector<std::string> mergeBlockers(int id) const {
        const auto found = pullRequests_.find(id);
        if (found == pullRequests_.end()) {
            throw std::out_of_range("Pull Request does not exist");
        }

        const auto& pr = found->second;
        std::vector<std::string> blockers;

        if (pr.state != PullRequestState::Open) {
            blockers.push_back("Pull Request is not open");
        }

        if (pr.commits.empty()) {
            blockers.push_back("No commits have been submitted");
        }

        std::string latestSha;
        if (!pr.commits.empty()) {
            latestSha = pr.commits.back().sha;
        }

        std::unordered_map<std::string, ReviewState> latestReviews;

        for (const auto& review : pr.reviews) {
            if (review.dismissed ||
                !review.eligible ||
                review.commitSha != latestSha ||
                !containsReviewer(pr.requestedReviewers, review.reviewer)) {
                continue;
            }

            latestReviews[review.reviewer] = review.state;
        }

        int approvals = 0;
        bool changesRequested = false;

        for (const auto& [reviewer, state] : latestReviews) {
            (void) reviewer;

            if (state == ReviewState::Approved) {
                ++approvals;
            } else if (state == ReviewState::ChangesRequested) {
                changesRequested = true;
            }
        }

        if (changesRequested) {
            blockers.push_back(
                "A current reviewer has requested changes"
            );
        }

        if (approvals < protection_.requiredApprovals) {
            blockers.push_back(
                "Insufficient approvals: required " +
                std::to_string(protection_.requiredApprovals) +
                ", received " + std::to_string(approvals)
            );
        }

        for (const auto& requiredCheck : protection_.requiredChecks) {
            auto check = pr.checks.find(requiredCheck);

            if (check == pr.checks.end() ||
                check->second != CheckState::Success) {
                blockers.push_back(
                    "Required check is not successful: " + requiredCheck
                );
            }
        }

        if (protection_.requireConversationResolution) {
            const bool unresolved = std::any_of(
                pr.conversations.begin(), pr.conversations.end(),
                [](const Conversation& conversation) {
                    return !conversation.resolved;
                }
            );

            if (unresolved) {
                blockers.push_back(
                    "Unresolved review conversations remain"
                );
            }
        }

        return blockers;
    }

    void merge(
        int id,
        const std::string& actor,
        MergeStrategy strategy
    ) {
        auto& pr = getPullRequest(id);

        if (isBlank(actor)) {
            throw std::invalid_argument("Merge actor is required");
        }

        const auto blockers = mergeBlockers(id);
        if (!blockers.empty()) {
            std::string message = "Merge blocked:";
            for (const auto& blocker : blockers) {
                message += "\n - " + blocker;
            }
            throw std::logic_error(message);
        }

        pr.state = PullRequestState::Merged;
        pr.mergeActor = actor;
        pr.mergeStrategy = strategy;
    }

    void printPullRequest(int id) const {
        const auto found = pullRequests_.find(id);
        if (found == pullRequests_.end()) {
            throw std::out_of_range("Pull Request does not exist");
        }

        const auto& pr = found->second;

        std::cout << "\nPull Request #" << pr.id
                  << ": " << pr.title << '\n'
                  << "Source: " << pr.sourceBranch << '\n'
                  << "Target: " << pr.targetBranch << '\n'
                  << "State: " << toString(pr.state) << '\n'
                  << "Commits: " << pr.commits.size() << '\n';

        const auto blockers = mergeBlockers(id);
        if (blockers.empty()) {
            std::cout << "Merge eligibility: eligible\n";
        } else {
            std::cout << "Merge eligibility: blocked\n";
            for (const auto& blocker : blockers) {
                std::cout << "  - " << blocker << '\n';
            }
        }

        if (pr.state == PullRequestState::Merged) {
            std::cout << "Merged by: " << pr.mergeActor << '\n'
                      << "Strategy: " << toString(pr.mergeStrategy) << '\n';
        }
    }

    void directPush(const std::string& actor, bool administrator) const {
        if (protection_.restrictDirectPushes &&
            protection_.enforceForAdministrators) {
            throw std::logic_error(
                "Direct push denied by protected branch policy"
            );
        }

        if (protection_.restrictDirectPushes && !administrator) {
            throw std::logic_error(
                "Direct push denied for ordinary repository members"
            );
        }

        if (administrator && !protection_.allowBypass) {
            throw std::logic_error(
                "Administrator bypass is disabled"
            );
        }

        if (isBlank(actor)) {
            throw std::invalid_argument("Push actor is required");
        }
    }

    void forcePush() const {
        if (!protection_.allowForcePush) {
            throw std::logic_error(
                "Force push denied by protected branch policy"
            );
        }
    }

    void deleteProtectedBranch() const {
        if (!protection_.allowDeletion) {
            throw std::logic_error(
                "Protected branch deletion is disabled"
            );
        }
    }
};

}  // namespace governance

int main() {
    using namespace governance;

    try {
        std::cout << "Repository governance and named configuration\n";

        // Fluent setters emulate readable named configuration without
        // pretending that C++ supports named arguments at call sites.
        BranchProtection protection;
        protection.branch = "main";
        protection.setRequiredApprovals(2)
                  .setRequiredChecks({
                      "unit-tests",
                      "security-scan",
                      "lint"
                  })
                  .setForcePushAllowed(false);

        Repository repository("payments-platform", protection);

        PullRequest request;
        request.id = 418;
        request.title = "Enforce signed deployment artifacts";
        request.sourceBranch = "feature/signed-artifacts";
        request.targetBranch = "main";
        request.state = PullRequestState::Open;
        request.requestedReviewers = {"Maya", "Daniel"};

        repository.createPullRequest(request);

        repository.addCommit(
            418,
            {"a1b2c3d", {
                "src/signature.cpp",
                "tests/signature_test.cpp"
            }}
        );

        repository.addConversation(
            418,
            {"security-comment-17", false}
        );

        repository.submitReview(
            418,
            {"Maya", ReviewState::Approved, "a1b2c3d", false, true}
        );

        repository.setCheck(418, "unit-tests", CheckState::Success);
        repository.setCheck(418, "security-scan", CheckState::Success);
        repository.setCheck(418, "lint", CheckState::Success);

        std::cout << "\nInitial merge evaluation\n";
        repository.printPullRequest(418);

        repository.submitReview(
            418,
            {"Daniel", ReviewState::Approved, "a1b2c3d", false, true}
        );

        std::cout << "\nAfter the required reviews\n";
        repository.printPullRequest(418);

        try {
            repository.merge(418, "release-maintainer", MergeStrategy::Squash);
        } catch (const std::logic_error& error) {
            std::cout << "\nExpected merge rejection:\n"
                      << error.what() << '\n';
        }

        repository.resolveConversation(418, "security-comment-17");

        // A subsequent commit invalidates earlier approvals under this policy.
        repository.addCommit(
            418,
            {"b2c3d4e", {"src/signature.cpp"}}
        );

        std::cout << "\nAfter the source branch advances\n";
        repository.printPullRequest(418);

        repository.submitReview(
            418,
            {"Maya", ReviewState::Approved, "b2c3d4e", false, true}
        );

        repository.submitReview(
            418,
            {"Daniel", ReviewState::Approved, "b2c3d4e", false, true}
        );

        repository.merge(418, "release-maintainer", MergeStrategy::Squash);

        std::cout << "\nFinal merge state\n";
        repository.printPullRequest(418);

        std::cout << "\nProtected branch enforcement\n";

        try {
            repository.directPush("administrator", true);
        } catch (const std::logic_error& error) {
            std::cout << error.what() << '\n';
        }

        try {
            repository.forcePush();
        } catch (const std::logic_error& error) {
            std::cout << error.what() << '\n';
        }

        try {
            repository.deleteProtectedBranch();
        } catch (const std::logic_error& error) {
            std::cout << error.what() << '\n';
        }

        std::cout << "\nInput validation boundary\n";

        try {
            BranchProtection invalid;
            invalid.setRequiredApprovals(-1);
        } catch (const std::invalid_argument& error) {
            std::cout << "Invalid policy rejected: " << error.what() << '\n';
        }

        try {
            repository.getPullRequest(999);
        } catch (const std::out_of_range& error) {
            std::cout << "Unknown Pull Request rejected: "
                      << error.what() << '\n';
        }

    } catch (const std::exception& error) {
        std::cerr << "Repository governance failure: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
