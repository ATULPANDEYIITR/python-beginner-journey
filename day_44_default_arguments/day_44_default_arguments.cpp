#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

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

enum class MergeMethod {
    MergeCommit,
    Squash,
    Rebase
};

string toString(PullRequestState state) {
    switch (state) {
        case PullRequestState::Draft: return "DRAFT";
        case PullRequestState::Open: return "OPEN";
        case PullRequestState::Closed: return "CLOSED";
        case PullRequestState::Merged: return "MERGED";
    }
    throw logic_error("Unknown pull request state");
}

string toString(ReviewDecision decision) {
    switch (decision) {
        case ReviewDecision::Commented: return "COMMENTED";
        case ReviewDecision::Approved: return "APPROVED";
        case ReviewDecision::ChangesRequested: return "CHANGES_REQUESTED";
        case ReviewDecision::Dismissed: return "DISMISSED";
    }
    throw logic_error("Unknown review decision");
}

struct Review {
    string reviewer;
    ReviewDecision decision;
    int changesetRevision;
    bool dismissed = false;
};

struct StatusCheck {
    string name;
    CheckState state;
    bool required;
};

struct Conversation {
    string id;
    string text;
    bool resolved = false;
};

struct ProtectionPolicy {
    int requiredApprovals = 2;
    bool requireCI = true;
    bool requireSecurityScan = true;
    bool requireResolvedConversations = true;
    bool requireLinearHistory = false;
    bool prohibitDirectPush = true;
    bool prohibitForcePush = true;
    bool prohibitBranchDeletion = true;
    bool dismissStaleApprovals = true;
    bool allowAdministratorBypass = false;
    set<MergeMethod> permittedMergeMethods{
        MergeMethod::Squash,
        MergeMethod::Rebase
    };
};

struct EligibilityResult {
    bool eligible = false;
    vector<string> reasons;
    int countedApprovals = 0;
};

class PullRequest {
private:
    int number;
    string title;
    string author;
    string sourceBranch;
    string targetBranch;
    PullRequestState state;
    int revision = 0;
    int baseRevision = 0;

    vector<string> commits;
    vector<Review> reviews;
    map<string, StatusCheck> checks;
    vector<Conversation> conversations;
    set<string> requestedReviewers;

public:
    PullRequest(
        int number,
        string title,
        string author,
        string sourceBranch,
        string targetBranch = "main",
        bool draft = true
    )
        : number(number),
          title(move(title)),
          author(move(author)),
          sourceBranch(move(sourceBranch)),
          targetBranch(move(targetBranch)),
          state(draft ? PullRequestState::Draft : PullRequestState::Open) {
        if (number <= 0) {
            throw invalid_argument("Pull request number must be positive");
        }
        if (this->title.empty() || this->author.empty()) {
            throw invalid_argument("Title and author are required");
        }
        if (this->sourceBranch.empty() || this->targetBranch.empty()) {
            throw invalid_argument("Source and target branches are required");
        }
        if (this->sourceBranch == this->targetBranch) {
            throw invalid_argument("Source and target branches must differ");
        }
    }

    int getNumber() const {
        return number;
    }

    const string& getAuthor() const {
        return author;
    }

    PullRequestState getState() const {
        return state;
    }

    int getRevision() const {
        return revision;
    }

    const string& getSourceBranch() const {
        return sourceBranch;
    }

    const string& getTargetBranch() const {
        return targetBranch;
    }

    void markReady() {
        if (state != PullRequestState::Draft) {
            throw logic_error("Only a draft can be marked ready");
        }
        state = PullRequestState::Open;
    }

    void addCommit(const string& sha) {
        if (state != PullRequestState::Open &&
            state != PullRequestState::Draft) {
            throw logic_error("Commits require an active pull request");
        }
        if (sha.empty()) {
            throw invalid_argument("Commit identifier cannot be empty");
        }
        if (find(commits.begin(), commits.end(), sha) != commits.end()) {
            throw invalid_argument("Duplicate commit identifier");
        }

        commits.push_back(sha);
        ++revision;
        // Approvals are associated with a specific changeset revision.
        // Older reviews remain auditable but no longer count as current.
    }

    void requestReview(const string& reviewer) {
        if (state != PullRequestState::Open) {
            throw logic_error("Review requests require an open pull request");
        }
        if (reviewer.empty() || reviewer == author) {
            throw invalid_argument("Reviewer must be non-empty and independent");
        }
        requestedReviewers.insert(reviewer);
    }

    void submitReview(
        const string& reviewer,
        ReviewDecision decision
    ) {
        if (state != PullRequestState::Open) {
            throw logic_error("Reviews require an open pull request");
        }
        if (reviewer.empty() || reviewer == author) {
            throw invalid_argument("Authors cannot review their own pull request");
        }

        reviews.push_back({reviewer, decision, revision, false});
        requestedReviewers.erase(reviewer);
    }

    void dismissApprovals(const string& reviewer) {
        bool found = false;

        for (auto& review : reviews) {
            if (review.reviewer == reviewer &&
                review.decision == ReviewDecision::Approved &&
                !review.dismissed) {
                review.dismissed = true;
                found = true;
            }
        }

        if (!found) {
            throw invalid_argument("No active approval exists for this reviewer");
        }
    }

    void setCheck(
        const string& name,
        CheckState state,
        bool required = true
    ) {
        if (name.empty()) {
            throw invalid_argument("Status check name cannot be empty");
        }
        checks[name] = {name, state, required};
    }

    void addConversation(
        const string& id,
        const string& text,
        bool resolved = false
    ) {
        if (id.empty() || text.empty()) {
            throw invalid_argument("Conversation identifier and text are required");
        }
        conversations.push_back({id, text, resolved});
    }

    void resolveConversation(const string& id) {
        auto found = find_if(
            conversations.begin(),
            conversations.end(),
            [&](const Conversation& conversation) {
                return conversation.id == id;
            }
        );

        if (found == conversations.end()) {
            throw invalid_argument("Conversation does not exist");
        }
        found->resolved = true;
    }

    bool synchronizeBase(int newBaseRevision, bool hasConflicts) {
        if (state != PullRequestState::Open) {
            throw logic_error("Only an open pull request can synchronize");
        }
        if (newBaseRevision < baseRevision) {
            throw invalid_argument("Base revision cannot move backwards");
        }
        if (hasConflicts) {
            return false;
        }

        baseRevision = newBaseRevision;
        ++revision;
        return true;
    }

    EligibilityResult evaluate(
        const ProtectionPolicy& policy,
        MergeMethod method,
        bool administrator = false
    ) const {
        EligibilityResult result;

        if (state != PullRequestState::Open) {
            result.reasons.push_back("Pull request is not open");
        }

        if (policy.requiredApprovals < 0) {
            result.reasons.push_back("Policy has an invalid approval requirement");
        }

        if (!policy.permittedMergeMethods.count(method)) {
            result.reasons.push_back("Selected merge method is prohibited");
        }

        if (policy.requireLinearHistory && method == MergeMethod::MergeCommit) {
            result.reasons.push_back("Linear history prohibits merge commits");
        }

        // The latest review from each reviewer determines that reviewer's
        // current position. A later request for changes supersedes approval.
        map<string, Review> latestReviews;

        for (const auto& review : reviews) {
            auto found = latestReviews.find(review.reviewer);
            if (found == latestReviews.end() ||
                review.changesetRevision >= found->second.changesetRevision) {
                latestReviews[review.reviewer] = review;
            }
        }

        for (const auto& entry : latestReviews) {
            const Review& review = entry.second;
            if (review.decision == ReviewDecision::Approved &&
                !review.dismissed &&
                (!policy.dismissStaleApprovals ||
                 review.changesetRevision == revision)) {
                ++result.countedApprovals;
            }
        }

        if (result.countedApprovals < policy.requiredApprovals) {
            result.reasons.push_back(
                "Insufficient current approvals: " +
                to_string(result.countedApprovals) + "/" +
                to_string(policy.requiredApprovals)
            );
        }

        auto checkSucceeded = [&](const string& name) {
            auto found = checks.find(name);
            return found != checks.end() &&
                   found->second.state == CheckState::Success;
        };

        if (policy.requireCI && !checkSucceeded("ci")) {
            result.reasons.push_back("Required CI check has not succeeded");
        }

        if (policy.requireSecurityScan && !checkSucceeded("security")) {
            result.reasons.push_back("Required security scan has not succeeded");
        }

        for (const auto& entry : checks) {
            if (entry.second.required &&
                entry.second.state != CheckState::Success) {
                result.reasons.push_back(
                    "Required check failed or is pending: " + entry.first
                );
            }
        }

        if (policy.requireResolvedConversations) {
            for (const auto& conversation : conversations) {
                if (!conversation.resolved) {
                    result.reasons.push_back(
                        "Unresolved conversation: " + conversation.id
                    );
                }
            }
        }

        if (!requestedReviewers.empty()) {
            result.reasons.push_back("Review requests remain outstanding");
        }

        // Bypass is an explicit administrative exception, not an automatic
        // consequence of being an administrator.
        if (administrator && policy.allowAdministratorBypass) {
            result.reasons.clear();
        }

        result.eligible = result.reasons.empty();
        return result;
    }

    void merge(
        const ProtectionPolicy& policy,
        MergeMethod method,
        bool administrator = false
    ) {
        EligibilityResult result = evaluate(policy, method, administrator);
        if (!result.eligible) {
            string message = "Merge rejected:";
            for (const auto& reason : result.reasons) {
                message += "\n - " + reason;
            }
            throw logic_error(message);
        }
        state = PullRequestState::Merged;
    }

    void close() {
        if (state != PullRequestState::Open &&
            state != PullRequestState::Draft) {
            throw logic_error("Pull request cannot be closed from its current state");
        }
        state = PullRequestState::Closed;
    }

    void reopen() {
        if (state != PullRequestState::Closed) {
            throw logic_error("Only a closed, unmerged pull request can be reopened");
        }
        state = PullRequestState::Open;
    }

    void report(const EligibilityResult& result) const {
        cout << "\nPull request #" << number << ": " << title << '\n';
        cout << "Branches: " << sourceBranch << " -> " << targetBranch << '\n';
        cout << "State: " << toString(state) << ", revision: " << revision << '\n';
        cout << "Counted approvals: " << result.countedApprovals << '\n';
        cout << "Merge eligible: " << (result.eligible ? "yes" : "no") << '\n';

        for (const auto& reason : result.reasons) {
            cout << "  - " << reason << '\n';
        }
    }
};

int main() {
    try {
        ProtectionPolicy policy;
        policy.requiredApprovals = 2;
        policy.requireCI = true;
        policy.requireSecurityScan = true;
        policy.requireResolvedConversations = true;
        policy.requireLinearHistory = true;
        policy.allowAdministratorBypass = false;

        PullRequest pr(
            204,
            "Enforce deployment authorization",
            "developer-lee",
            "feature/deployment-auth",
            "main",
            true
        );

        pr.addCommit("a91c3e0");
        pr.markReady();

        pr.requestReview("reviewer-alex");
        pr.requestReview("reviewer-sam");

        pr.submitReview("reviewer-alex", ReviewDecision::Approved);
        pr.submitReview("reviewer-sam", ReviewDecision::Approved);

        pr.setCheck("ci", CheckState::Success);
        pr.setCheck("security", CheckState::Success);
        pr.setCheck("integration", CheckState::Success);

        pr.addConversation(
            "discussion-17",
            "Confirm denied deployment attempts are audited",
            false
        );

        auto blocked = pr.evaluate(policy, MergeMethod::Squash);
        pr.report(blocked);

        pr.resolveConversation("discussion-17");

        // Updating the changeset makes earlier approvals stale.
        pr.addCommit("b52d7f1");
        auto stale = pr.evaluate(policy, MergeMethod::Squash);
        pr.report(stale);

        pr.submitReview("reviewer-alex", ReviewDecision::Approved);
        pr.submitReview("reviewer-sam", ReviewDecision::Approved);

        auto ready = pr.evaluate(policy, MergeMethod::Squash);
        pr.report(ready);

        pr.merge(policy, MergeMethod::Squash);
        cout << "\nFinal state: " << toString(pr.getState()) << '\n';

        // A separate pull request demonstrates rejected state transitions.
        PullRequest closedPR(
            205,
            "Document release checks",
            "developer-mira",
            "docs/release-checks",
            "main",
            false
        );
        closedPR.close();

        try {
            closedPR.merge(policy, MergeMethod::Squash);
        } catch (const exception& error) {
            cout << "\nExpected rejection: " << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Governance error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
