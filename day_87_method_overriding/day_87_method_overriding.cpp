#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

enum class ReviewStatus {
    Pending,
    Approved,
    Rejected
};

enum class PullRequestState {
    Open,
    Draft,
    Merged,
    Closed
};

struct Commit {
    string hash;
    string message;
};

struct StatusCheck {
    string name;
    bool passed;
};

struct Review {
    string reviewer;
    ReviewStatus status;
    bool eligible;
    bool stale;
    bool dismissed;
};

class Branch {
public:
    string name;
    bool protectedBranch;
    bool allowsDirectPush;
    bool allowsForcePush;
    bool allowsDeletion;
    bool requiresLinearHistory;

    Branch(
        string branchName,
        bool protectedFlag,
        bool directPush,
        bool forcePush,
        bool deletion,
        bool linearHistory
    )
        : name(move(branchName)),
          protectedBranch(protectedFlag),
          allowsDirectPush(directPush),
          allowsForcePush(forcePush),
          allowsDeletion(deletion),
          requiresLinearHistory(linearHistory) {}

    void validateDirectPush() const {
        if (protectedBranch && !allowsDirectPush) {
            throw runtime_error(
                "Direct push rejected by branch protection"
            );
        }
    }

    void validateForcePush() const {
        if (protectedBranch && !allowsForcePush) {
            throw runtime_error(
                "Force push rejected by branch protection"
            );
        }
    }
};

class PullRequest {
private:
    set<string> resolvedConversations;
    set<string> allConversations;

public:
    int id;
    string title;
    string author;
    Branch* source;
    Branch* target;
    PullRequestState state;

    vector<Commit> commits;
    vector<Review> reviews;
    vector<StatusCheck> checks;

    bool baseBranchSynchronized;
    bool mergeConflict;
    bool changesApprovedByAuthor;

    PullRequest(
        int requestId,
        string requestTitle,
        string requestAuthor,
        Branch* sourceBranch,
        Branch* targetBranch
    )
        : id(requestId),
          title(move(requestTitle)),
          author(move(requestAuthor)),
          source(sourceBranch),
          target(targetBranch),
          state(PullRequestState::Open),
          baseBranchSynchronized(true),
          mergeConflict(false),
          changesApprovedByAuthor(false) {

        if (id <= 0 || author.empty() || !source || !target) {
            throw invalid_argument("Invalid Pull Request");
        }

        if (source->name == target->name) {
            throw invalid_argument(
                "Source and target branches must differ"
            );
        }
    }

    void addCommit(const Commit& commit) {
        if (state == PullRequestState::Merged ||
            state == PullRequestState::Closed) {
            throw runtime_error("Pull Request is not editable");
        }

        if (commit.hash.empty()) {
            throw invalid_argument("Commit hash cannot be empty");
        }

        auto duplicate = find_if(
            commits.begin(),
            commits.end(),
            [&](const Commit& existing) {
                return existing.hash == commit.hash;
            }
        );

        if (duplicate != commits.end()) {
            throw runtime_error("Duplicate commit");
        }

        commits.push_back(commit);

        // New commits make earlier approvals stale in this model.
        for (auto& review : reviews) {
            if (review.status == ReviewStatus::Approved) {
                review.stale = true;
            }
        }
    }

    void addReview(const Review& review) {
        if (state != PullRequestState::Open) {
            throw runtime_error("Reviews require an open request");
        }

        if (review.reviewer.empty()) {
            throw invalid_argument("Reviewer identity is required");
        }

        if (review.reviewer == author) {
            throw runtime_error("Self-review is prohibited");
        }

        reviews.push_back(review);
    }

    void addCheck(const StatusCheck& check) {
        if (check.name.empty()) {
            throw invalid_argument("Check name cannot be empty");
        }

        auto existing = find_if(
            checks.begin(),
            checks.end(),
            [&](const StatusCheck& current) {
                return current.name == check.name;
            }
        );

        if (existing == checks.end()) {
            checks.push_back(check);
        } else {
            existing->passed = check.passed;
        }
    }

    void addConversation(const string& conversationId) {
        if (conversationId.empty()) {
            throw invalid_argument("Conversation ID cannot be empty");
        }

        allConversations.insert(conversationId);
    }

    void resolveConversation(const string& conversationId) {
        if (!allConversations.count(conversationId)) {
            throw runtime_error("Unknown conversation");
        }

        resolvedConversations.insert(conversationId);
    }

    bool conversationsResolved() const {
        return allConversations == resolvedConversations;
    }

    void synchronizeBaseBranch(bool hasConflict) {
        if (state != PullRequestState::Open) {
            throw runtime_error("Cannot synchronize a closed request");
        }

        baseBranchSynchronized = true;
        mergeConflict = hasConflict;

        // Synchronization can invalidate previous approvals.
        for (auto& review : reviews) {
            if (review.status == ReviewStatus::Approved) {
                review.stale = true;
            }
        }
    }

    void reopen() {
        if (state != PullRequestState::Closed) {
            throw runtime_error("Only closed requests can be reopened");
        }

        state = PullRequestState::Open;
    }

    void close() {
        if (state == PullRequestState::Merged) {
            throw runtime_error("Merged requests cannot be closed");
        }

        state = PullRequestState::Closed;
    }
};

class GovernancePolicy {
public:
    size_t requiredApprovals;
    set<string> requiredChecks;
    bool requireConversationResolution;
    bool requireSynchronizedBase;
    bool restrictDirectPush;
    bool requireLinearHistory;
    bool allowDraftMerge;

    GovernancePolicy()
        : requiredApprovals(2),
          requiredChecks({"build", "unit-tests", "security-scan"}),
          requireConversationResolution(true),
          requireSynchronizedBase(true),
          restrictDirectPush(true),
          requireLinearHistory(true),
          allowDraftMerge(false) {}
};

struct EligibilityResult {
    bool eligible;
    vector<string> violations;
};

class MergeEligibilityEngine {
private:
    static size_t validApprovals(const PullRequest& request) {
        set<string> reviewers;

        for (const auto& review : request.reviews) {
            if (review.status == ReviewStatus::Approved &&
                review.eligible &&
                !review.stale &&
                !review.dismissed &&
                review.reviewer != request.author) {

                reviewers.insert(review.reviewer);
            }
        }

        return reviewers.size();
    }

public:
    static EligibilityResult evaluate(
        const PullRequest& request,
        const GovernancePolicy& policy
    ) {
        vector<string> violations;

        if (request.state != PullRequestState::Open &&
            request.state != PullRequestState::Draft) {
            violations.push_back("Pull Request is not open");
        }

        if (request.state == PullRequestState::Draft &&
            !policy.allowDraftMerge) {
            violations.push_back("Draft Pull Request cannot be merged");
        }

        if (request.commits.empty()) {
            violations.push_back("No proposed commits");
        }

        if (request.mergeConflict) {
            violations.push_back("Unresolved merge conflict");
        }

        if (policy.requireSynchronizedBase &&
            !request.baseBranchSynchronized) {
            violations.push_back("Source branch is behind target branch");
        }

        if (request.target->protectedBranch) {
            if (policy.requiredApprovals > 0 &&
                validApprovals(request) < policy.requiredApprovals) {
                violations.push_back("Insufficient valid approvals");
            }

            for (const auto& required : policy.requiredChecks) {
                auto found = find_if(
                    request.checks.begin(),
                    request.checks.end(),
                    [&](const StatusCheck& check) {
                        return check.name == required && check.passed;
                    }
                );

                if (found == request.checks.end()) {
                    violations.push_back(
                        "Missing or failing status check: " + required
                    );
                }
            }

            if (policy.requireConversationResolution &&
                !request.conversationsResolved()) {
                violations.push_back("Unresolved review conversations");
            }

            if (policy.requireLinearHistory &&
                !request.target->requiresLinearHistory) {
                violations.push_back(
                    "Target branch does not enforce linear history"
                );
            }
        }

        return {
            violations.empty(),
            violations
        };
    }

    static void merge(
        PullRequest& request,
        const GovernancePolicy& policy
    ) {
        EligibilityResult result = evaluate(request, policy);

        if (!result.eligible) {
            throw runtime_error(
                "Merge rejected: " + result.violations.front()
            );
        }

        request.state = PullRequestState::Merged;
    }
};

void printEvaluation(
    const PullRequest& request,
    const GovernancePolicy& policy
) {
    auto result = MergeEligibilityEngine::evaluate(request, policy);

    cout << "\nPull Request #" << request.id
         << ": " << request.title << '\n';

    cout << "Merge eligibility: "
         << (result.eligible ? "ELIGIBLE" : "BLOCKED")
         << '\n';

    for (const auto& violation : result.violations) {
        cout << " - " << violation << '\n';
    }
}

int main() {
    try {
        Branch feature(
            "feature/payment",
            false,
            true,
            true,
            true,
            false
        );

        Branch mainBranch(
            "main",
            true,
            false,
            false,
            false,
            true
        );

        GovernancePolicy policy;

        PullRequest request(
            101,
            "Implement payment processing",
            "developer_a",
            &feature,
            &mainBranch
        );

        request.addCommit({
            "a81f9c2",
            "Add payment processor"
        });

        request.addCommit({
            "b72d8e1",
            "Add payment validation"
        });

        request.addConversation("discussion-1");
        request.addConversation("discussion-2");

        request.addReview({
            "reviewer_a",
            ReviewStatus::Approved,
            true,
            false,
            false
        });

        request.addReview({
            "reviewer_b",
            ReviewStatus::Approved,
            true,
            false,
            false
        });

        request.addCheck({"build", true});
        request.addCheck({"unit-tests", true});
        request.addCheck({"security-scan", true});

        request.resolveConversation("discussion-1");

        printEvaluation(request, policy);

        cout << "\nResolving remaining discussion...\n";

        request.resolveConversation("discussion-2");

        printEvaluation(request, policy);

        cout << "\nSynchronizing source branch...\n";

        request.synchronizeBaseBranch(false);

        printEvaluation(request, policy);

        cout << "\nRefreshing reviewer decisions...\n";

        request.addReview({
            "reviewer_a",
            ReviewStatus::Approved,
            true,
            false,
            false
        });

        request.addReview({
            "reviewer_b",
            ReviewStatus::Approved,
            true,
            false,
            false
        });

        printEvaluation(request, policy);

        cout << "\nExecuting merge...\n";

        MergeEligibilityEngine::merge(request, policy);

        cout << "Final state: MERGED\n";

        cout << "\nDIRECT PUSH TEST\n";

        try {
            mainBranch.validateDirectPush();
        } catch (const exception& error) {
            cout << error.what() << '\n';
        }

        cout << "\nFORCE PUSH TEST\n";

        try {
            mainBranch.validateForcePush();
        } catch (const exception& error) {
            cout << error.what() << '\n';
        }

        cout << "\nSTALE APPROVAL TEST\n";

        PullRequest secondRequest(
            102,
            "Improve authentication",
            "developer_b",
            &feature,
            &mainBranch
        );

        secondRequest.addCommit({
            "c82a7d1",
            "Add authentication checks"
        });

        secondRequest.addReview({
            "reviewer_c",
            ReviewStatus::Approved,
            true,
            false,
            false
        });

        secondRequest.addReview({
            "reviewer_d",
            ReviewStatus::Approved,
            true,
            false,
            false
        });

        secondRequest.addCommit({
            "d91b4e2",
            "Modify authentication rules"
        });

        printEvaluation(secondRequest, policy);

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
