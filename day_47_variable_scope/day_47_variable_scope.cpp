#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

// Repository governance case study: local objects represent independent
// review and policy state. References are used only while their owners live.

enum class ReviewState {
    Pending,
    Approved,
    ChangesRequested,
    Dismissed
};

string toString(ReviewState state) {
    switch (state) {
        case ReviewState::Pending: return "PENDING";
        case ReviewState::Approved: return "APPROVED";
        case ReviewState::ChangesRequested: return "CHANGES_REQUESTED";
        case ReviewState::Dismissed: return "DISMISSED";
    }
    throw logic_error("Unknown review state");
}

struct Review {
    string reviewer;
    ReviewState state;
    string commitId;
};

struct PullRequest {
    int id;
    string author;
    string sourceBranch;
    string targetBranch;
    vector<string> commits;
    vector<Review> reviews;
    map<string, bool> checks;
    bool draft = false;
    bool conversationsResolved = true;
    bool open = true;
    bool merged = false;
    bool approvalsStale = false;
};

struct BranchProtection {
    string branch;
    size_t requiredApprovals = 1;
    set<string> requiredChecks;
    bool restrictDirectPushes = true;
    bool blockForcePushes = true;
    bool blockDeletion = true;
    bool requireResolvedConversations = true;
    bool requireLinearHistory = true;
    bool dismissStaleApprovals = true;
    bool allowAdministratorBypass = false;
};

struct Evaluation {
    bool eligible;
    vector<string> failures;
};

class GovernanceEngine {
private:
    BranchProtection policy_;

    bool hasLinearHistory(const PullRequest& pr) const {
        // The scenario represents a linear history as one commit chain.
        // This model receives a boolean check result for richer graph validation.
        auto found = pr.checks.find("linear-history");
        return found != pr.checks.end() && found->second;
    }

public:
    explicit GovernanceEngine(BranchProtection policy)
        : policy_(std::move(policy)) {
        if (policy_.branch.empty()) {
            throw invalid_argument("Protected branch cannot be empty");
        }
    }

    Evaluation evaluate(const PullRequest& pr) const {
        vector<string> failures;

        if (!pr.open || pr.merged) {
            failures.push_back("Pull request is not open and mergeable");
        }

        if (pr.draft) {
            failures.push_back("Draft pull request cannot be merged");
        }

        if (pr.author.empty() || pr.sourceBranch.empty() ||
            pr.targetBranch.empty() || pr.commits.empty()) {
            failures.push_back("Required pull request metadata is missing");
        }

        if (pr.targetBranch != policy_.branch) {
            failures.push_back("Target branch does not match the policy");
        }

        set<string> eligibleApprovers;
        for (const auto& review : pr.reviews) {
            // A later decision by the same reviewer replaces the earlier decision.
            if (review.reviewer == pr.author || review.reviewer.empty()) {
                continue;
            }

            if (review.state == ReviewState::Approved) {
                eligibleApprovers.insert(review.reviewer);
            } else {
                eligibleApprovers.erase(review.reviewer);
            }
        }

        if (policy_.dismissStaleApprovals && pr.approvalsStale) {
            eligibleApprovers.clear();
            failures.push_back("Approvals became stale after new commits");
        }

        if (eligibleApprovers.size() < policy_.requiredApprovals) {
            failures.push_back("Required number of distinct approvals not met");
        }

        for (const string& required : policy_.requiredChecks) {
            auto check = pr.checks.find(required);
            if (check == pr.checks.end()) {
                failures.push_back("Missing required check: " + required);
            } else if (!check->second) {
                failures.push_back("Failed required check: " + required);
            }
        }

        if (policy_.requireResolvedConversations && !pr.conversationsResolved) {
            failures.push_back("Review discussions remain unresolved");
        }

        if (policy_.requireLinearHistory && !hasLinearHistory(pr)) {
            failures.push_back("Linear-history requirement not satisfied");
        }

        return {failures.empty(), failures};
    }

    bool merge(PullRequest& pr) const {
        Evaluation result = evaluate(pr);
        if (!result.eligible) {
            cout << "PR #" << pr.id << " blocked:\n";
            for (const auto& failure : result.failures) {
                cout << "  - " << failure << '\n';
            }
            return false;
        }

        // Eligibility is checked immediately before changing lifecycle state.
        pr.merged = true;
        pr.open = false;
        cout << "PR #" << pr.id << " merged into " << policy_.branch << '\n';
        return true;
    }

    bool directPushAllowed(bool administrator) const {
        if (!policy_.restrictDirectPushes) return true;
        return administrator && policy_.allowAdministratorBypass;
    }

    bool forcePushAllowed(bool administrator) const {
        if (!policy_.blockForcePushes) return true;
        return administrator && policy_.allowAdministratorBypass;
    }

    bool branchDeletionAllowed(bool administrator) const {
        if (!policy_.blockDeletion) return true;
        return administrator && policy_.allowAdministratorBypass;
    }
};

class ReviewSession {
private:
    string reviewer_;
    ReviewState state_ = ReviewState::Pending;
    vector<string> comments_;

public:
    explicit ReviewSession(string reviewer) : reviewer_(std::move(reviewer)) {
        if (reviewer_.empty()) {
            throw invalid_argument("Reviewer identity is required");
        }
    }

    void addInlineComment(const string& path, int line, const string& body) {
        if (path.empty() || line < 1 || body.empty()) {
            throw invalid_argument("Inline comments require a path, line, and body");
        }
        comments_.push_back(path + ":" + to_string(line) + " " + body);
    }

    void submit(ReviewState next) {
        bool valid =
            (state_ == ReviewState::Pending &&
             (next == ReviewState::Approved || next == ReviewState::ChangesRequested)) ||
            ((state_ == ReviewState::Approved || state_ == ReviewState::ChangesRequested) &&
             next == ReviewState::Dismissed);

        if (!valid) {
            throw logic_error("Invalid review state transition");
        }
        state_ = next;
    }

    void print() const {
        cout << reviewer_ << ": " << toString(state_) << '\n';
        for (const auto& comment : comments_) {
            cout << "  " << comment << '\n';
        }
    }
};

int main() {
    try {
        cout << "Repository governance case study\n";

        BranchProtection policy;
        policy.branch = "main";
        policy.requiredApprovals = 2;
        policy.requiredChecks = {"unit-tests", "security-scan", "linear-history"};

        GovernanceEngine engine(policy);

        ReviewSession review("reviewer-ada");
        review.addInlineComment(
            "src/payment.cpp", 87,
            "Reject unsupported currency before updating the ledger."
        );
        review.submit(ReviewState::Approved);
        review.print();

        PullRequest pr{
            284,
            "developer-kim",
            "feature/currency-validation",
            "main",
            {"c101", "c102"},
            {
                {"reviewer-ada", ReviewState::Approved, "c102"},
                {"reviewer-lin", ReviewState::Approved, "c102"},
                {"developer-kim", ReviewState::Approved, "c102"}
            },
            {
                {"unit-tests", true},
                {"security-scan", true},
                {"linear-history", true}
            }
        };

        cout << "\nSuccessful merge evaluation\n";
        Evaluation result = engine.evaluate(pr);
        cout << "Eligible: " << boolalpha << result.eligible << '\n';
        engine.merge(pr);

        PullRequest blocked = pr;
        blocked.id = 285;
        blocked.open = true;
        blocked.merged = false;
        blocked.approvalsStale = true;
        blocked.checks["security-scan"] = false;
        blocked.conversationsResolved = false;

        cout << "\nBlocked merge evaluation\n";
        engine.merge(blocked);

        cout << "\nProtected operation decisions\n";
        cout << "Contributor direct push: "
             << engine.directPushAllowed(false) << '\n';
        cout << "Administrator force push: "
             << engine.forcePushAllowed(true) << '\n';
        cout << "Administrator branch deletion: "
             << engine.branchDeletionAllowed(true) << '\n';

        try {
            ReviewSession invalidReview("reviewer-noor");
            invalidReview.submit(ReviewState::Dismissed);
        } catch (const logic_error& error) {
            cout << "Review transition rejected: " << error.what() << '\n';
        }

        try {
            BranchProtection invalidPolicy;
            invalidPolicy.branch = "";
            GovernanceEngine invalidEngine(invalidPolicy);
        } catch (const invalid_argument& error) {
            cout << "Policy validation rejected: " << error.what() << '\n';
        }
    } catch (const exception& error) {
        cerr << "Governance engine error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
